"""FIELD-LAB-001 — bounded relational perturbation crucible.

The founding instrument reuses the already-executable robotics R001 model.
It does not claim a generic causal oracle.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any

from experiments.robotics.r001_body_state import (
    BODIES,
    DT,
    STEPS,
    Controller,
    simulate,
)

SCHEMA = "tranchNOSE.field-lab.receipt/v0"
EXPERIMENT = "robotics.r001.body-morphology"
REQUIRED_INVARIANTS = ("controller", "challenge", "dt", "steps")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(domain: str, value: Any) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def _controller(value: Any) -> Controller:
    if value is None:
        return Controller()
    if not isinstance(value, dict):
        raise ValueError("current_field.controller must be an object")
    allowed = {"target_velocity", "kp", "command_limit"}
    if set(value) - allowed:
        raise ValueError("unknown controller field")
    return Controller(**value)


def _body_delta(before: Any, after: Any) -> dict[str, dict[str, float]]:
    left = asdict(before)
    right = asdict(after)
    return {
        key: {"before": left[key], "after": right[key]}
        for key in ("mass", "drag", "traction", "compliance")
        if left[key] != right[key]
    }


def run_field_lab(request: Any) -> dict[str, Any]:
    """Run the founding controlled body/morphology perturbation."""
    if not isinstance(request, dict):
        raise ValueError("FIELD_LAB_REQUEST_REQUIRED")
    if request.get("experiment") != EXPERIMENT:
        raise ValueError("UNSUPPORTED_FIELD_LAB_EXPERIMENT")

    packet = request.get("particular_packet")
    if not isinstance(packet, dict) or not packet:
        raise ValueError("PARTICULAR_PACKET_REQUIRED")

    current = request.get("current_field")
    perturbation = request.get("perturbation")
    if not isinstance(current, dict) or not isinstance(perturbation, dict):
        raise ValueError("CURRENT_FIELD_AND_PERTURBATION_REQUIRED")

    before_name = str(current.get("body") or "")
    after_name = str(perturbation.get("body") or "")
    if before_name not in BODIES or after_name not in BODIES:
        raise ValueError("UNKNOWN_DECLARED_BODY")
    if before_name == after_name:
        raise ValueError("PERTURBATION_MUST_CHANGE_DECLARED_BODY")

    declared = tuple(request.get("declared_invariants") or REQUIRED_INVARIANTS)
    if declared != REQUIRED_INVARIANTS:
        raise ValueError("FIELD_LAB_001_REQUIRES_EXACT_FOUNDING_INVARIANTS")

    controller = _controller(current.get("controller"))
    before = simulate(BODIES[before_name], controller)
    after = simulate(BODIES[after_name], controller)

    before_r = before["receipt"]
    after_r = after["receipt"]

    invariant_checks = {
        "controller": before_r["controller_ref"] == after_r["controller_ref"],
        "challenge": before_r["challenge"] == after_r["challenge"],
        "dt": True,
        "steps": len(before["trajectory"]) == len(after["trajectory"]) == STEPS,
    }
    all_invariants_hold = all(invariant_checks.values())
    body_changed = before_r["body_ref"] != after_r["body_ref"]
    trajectory_changed = (
        before_r["observations"]["trajectory_digest"]
        != after_r["observations"]["trajectory_digest"]
    )

    observations = {
        "trajectory_changed": trajectory_changed,
        "baseline_trajectory_ref": before_r["observations"]["trajectory_digest"],
        "perturbed_trajectory_ref": after_r["observations"]["trajectory_digest"],
        "final_position_delta": round(
            after_r["observations"]["final_position"]
            - before_r["observations"]["final_position"],
            9,
        ),
        "final_velocity_delta": round(
            after_r["observations"]["final_velocity"]
            - before_r["observations"]["final_velocity"],
            9,
        ),
        "recovery_step_before": before_r["observations"]["recovery_step"],
        "recovery_step_after": after_r["observations"]["recovery_step"],
    }

    supports = all_invariants_hold and body_changed and trajectory_changed
    core = {
        "schema": SCHEMA,
        "experiment": EXPERIMENT,
        "particular_packet_ref": _digest(
            "TranchNOSE-FieldLab-ParticularPacket-v1|", packet
        ),
        "before_field": {
            "body": before_name,
            "body_ref": before_r["body_ref"],
            "controller_ref": before_r["controller_ref"],
        },
        "after_field": {
            "body": after_name,
            "body_ref": after_r["body_ref"],
            "controller_ref": after_r["controller_ref"],
        },
        "declared_invariants": list(REQUIRED_INVARIANTS),
        "invariant_checks": invariant_checks,
        "perturbation": {
            "dimension": "body/morphology",
            "changed": _body_delta(BODIES[before_name], BODIES[after_name]),
        },
        "observations": observations,
        "causal_evidence": {
            "status": (
                "SUPPORTS_DECLARED_BODY_CAUSAL_RELEVANCE_IN_MODEL"
                if supports
                else "DOES_NOT_SUPPORT_CAUSAL_RELEVANCE"
            ),
            "scope": "deterministic TranchNOSE robotics R001 software model only",
            "basis": (
                "declared controller/challenge/dt/steps held fixed; "
                "declared body changed"
            ),
        },
        "counterfactual_candidate": {
            "statement": (
                f"Under the declared R001 model, replacing {before_name} with "
                f"{after_name} while holding the founding invariants fixed "
                f"{'changes' if trajectory_changed else 'does not change'} "
                "the trajectory."
            ),
            "historical_rewrite": False,
        },
        "authority": {
            "observe": True,
            "propose_counterfactual": True,
            "admit": False,
            "select": False,
            "mutate_external_state": False,
        },
        "laws": [
            "RELATIONAL DIFFERENCE != CAUSATION",
            "CONTROLLED PERTURBATION -> CAUSAL EVIDENCE",
            "CAUSAL EVIDENCE != UNIVERSAL LAW",
            "COUNTERFACTUAL != HISTORY",
            "OBSERVE != AUTHORIZE != MUTATE",
        ],
        "non_claims": [
            "software dynamics are not physical proof",
            "this result does not establish a universal body-behavior law",
            "the counterfactual candidate does not rewrite a witnessed occurrence",
            "FIELD LAB grants no admission, selection, or mutation authority",
        ],
    }
    result = dict(core)
    result["receipt_id"] = _digest("TranchNOSE-FieldLab-Receipt-v1|", core)
    return result
