#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import rfc8785
from jsonschema import Draft202012Validator

RUN_DOMAIN = b"TranchNOSE-001A-Run-v1|"
RECEIPT_DOMAIN = b"TranchNOSE-001A-Receipt-v1|"
TRANSCRIPT_DOMAIN = b"TranchNOSE-001A-G-local-v1|"
STREAM_DOMAIN = b"TranchNOSE-001A-PRNG-v1|"
ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "receipt.schema.json"


def canonical_bytes(value: Any) -> bytes:
    return rfc8785.dumps(value)


def digest(domain: bytes, value: Any) -> str:
    return "sha256:" + hashlib.sha256(domain + canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_receipt(receipt: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(receipt)


class NamedStream:
    """Deterministic named stream using SHA-256(seed, name, counter)."""

    def __init__(self, name: str, seed: str):
        self.name = name
        self.seed = seed
        self.counter = 0

    def _block(self) -> bytes:
        payload = {"name": self.name, "seed": self.seed, "counter": self.counter}
        self.counter += 1
        return hashlib.sha256(STREAM_DOMAIN + canonical_bytes(payload)).digest()

    def uint32(self) -> int:
        return int.from_bytes(self._block()[:4], "big")

    def choice(self, values: list[Any]) -> Any:
        if not values:
            raise ValueError("choice requires a non-empty sequence")
        return values[self.uint32() % len(values)]


def named_streams(manifest: dict[str, Any]) -> dict[str, NamedStream]:
    streams = manifest["randomness"]["streams"]
    names = [s["name"] for s in streams]
    if len(names) != len(set(names)):
        raise ValueError("PRNG stream names must be unique")
    required = {"interventions", "coordination"}
    if set(names) != required:
        raise ValueError(f"synthetic harness requires exactly these streams: {sorted(required)}")
    return {s["name"]: NamedStream(s["name"], s["seed"]) for s in streams}


def build_interventions(manifest: dict[str, Any], stream: NamedStream) -> list[dict[str, Any]]:
    types = ["phase_corrupt", "node_remove", "noise_inject"]
    count = manifest["intervention_count"]
    max_steps = manifest["inputs"]["termination"]["max_steps"]
    out = []
    for order in range(count):
        out.append({
            "step": 1 + (stream.uint32() % max(1, max_steps - 1)),
            "order": order,
            "type": stream.choice(types),
            "parameters": {"magnitude_ppm": stream.uint32() % 1001},
        })
    return sorted(out, key=lambda item: (item["step"], item["order"]))


def build_transcript(manifest: dict[str, Any], stream: NamedStream) -> list[dict[str, Any]]:
    permitted = manifest["condition"]["permitted_coordination_classes"]
    if not permitted and manifest["coordination_message_count"]:
        raise ValueError("cannot emit coordination messages when no classes are permitted")
    transcript = []
    for seq in range(manifest["coordination_message_count"]):
        transcript.append({
            "seq": seq,
            "class": stream.choice(permitted),
            "payload_u32": stream.uint32(),
        })
    return transcript


def run_identity_input(manifest: dict[str, Any], interventions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": manifest["schema_version"],
        "experiment": manifest["experiment"],
        "implementation": manifest["implementation"],
        "condition": manifest["condition"],
        "randomness": manifest["randomness"],
        "inputs": manifest["inputs"],
        "interventions": interventions,
        "synthetic_harness": {"coordination_message_count": manifest["coordination_message_count"]},
    }


def build_receipt(manifest: dict[str, Any]) -> dict[str, Any]:
    streams = named_streams(manifest)
    interventions = build_interventions(manifest, streams["interventions"])
    transcript = build_transcript(manifest, streams["coordination"])
    transcript_digest = digest(TRANSCRIPT_DOMAIN, transcript)
    total_bits = sum(len(canonical_bytes(message)) * 8 for message in transcript)
    run_id = digest(RUN_DOMAIN, run_identity_input(manifest, interventions))

    receipt: dict[str, Any] = {
        "identity": {
            "schema_version": manifest["schema_version"],
            "experiment": manifest["experiment"],
            "implementation": manifest["implementation"],
            "run_id": run_id,
            "receipt_digest": "sha256:" + "0" * 64,
        },
        "randomness": copy.deepcopy(manifest["randomness"]),
        "condition": copy.deepcopy(manifest["condition"]),
        "inputs": copy.deepcopy(manifest["inputs"]),
        "interventions": interventions,
        "observations": {
            "final_overlap": {"F_A": 1.0, "F_B": 0.0, "F_C": 0.0, "F_D": 0.0},
            "winning_basin": "F_A",
            "converged": True,
            "convergence_step": manifest["inputs"]["termination"]["max_steps"],
            "attractor_lifetime_steps": 1,
            "final_field_digest": digest(b"TranchNOSE-001A-Synthetic-Field-v1|", {"run_id": run_id}),
            "final_electronic_state_digest": digest(b"TranchNOSE-001A-Synthetic-Electronic-v1|", {"run_id": run_id}),
            "final_topology_digest": digest(b"TranchNOSE-001A-Synthetic-Topology-v1|", manifest["inputs"]["field_topology"]),
        },
        "coordination_audit": {
            "transcript_digest": transcript_digest,
            "message_count": len(transcript),
            "total_bits": total_bits,
            "ceiling_compliant": total_bits <= manifest["condition"]["coordination_ceiling_bits"],
            "leakage_decoder": {"evaluated": False, "accuracy": None, "confidence": None},
            "causal_trace_controls": [],
        },
        "causal_attribution": {
            "ablation_matrix": {"A": None, "B": None, "C": None, "D": None, "delta_field": None, "delta_electronic": None, "interaction": None},
            "state_swap_controls": [],
            "attribution": "unresolved",
        },
        "failure": None,
    }

    digest_input = copy.deepcopy(receipt)
    digest_input["identity"].pop("receipt_digest")
    receipt["identity"]["receipt_digest"] = digest(RECEIPT_DOMAIN, digest_input)
    validate_receipt(receipt)
    return receipt


def replay(manifest: dict[str, Any], expected: dict[str, Any]) -> None:
    validate_receipt(expected)
    actual = build_receipt(manifest)
    if canonical_bytes(actual) != canonical_bytes(expected):
        raise AssertionError("exact replay mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description="TranchNOSE Experiment 001A synthetic receipt harness")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--write", type=Path, help="write the canonical receipt JSON")
    parser.add_argument("--replay", type=Path, help="assert exact replay against an existing receipt")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    receipt = build_receipt(manifest)
    if args.replay:
        replay(manifest, load_json(args.replay))
    if args.write:
        args.write.write_bytes(canonical_bytes(receipt) + b"\n")
    else:
        print(canonical_bytes(receipt).decode("utf-8"))


if __name__ == "__main__":
    main()
