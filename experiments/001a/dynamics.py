from __future__ import annotations

import hashlib
import math
from typing import Any, Callable

BASIN_NAMES = ("F_A", "F_B", "F_C", "F_D")
NODE_COUNT = 8
SQRT_HALF = 0.7071067811865476
CARRIERS = (
    complex(1.0, 0.0),
    complex(SQRT_HALF, SQRT_HALF),
    complex(0.0, 1.0),
    complex(-SQRT_HALF, SQRT_HALF),
    complex(-1.0, 0.0),
    complex(-SQRT_HALF, -SQRT_HALF),
    complex(0.0, -1.0),
    complex(SQRT_HALF, -SQRT_HALF),
)
SIGN_PATTERNS = (
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, -1, 1, -1, 1, -1, 1, -1),
    (1, 1, -1, -1, 1, 1, -1, -1),
    (1, -1, -1, 1, 1, -1, -1, 1),
)
ATTRACTORS = {
    name: tuple(CARRIERS[k] * SIGN_PATTERNS[j][k] for k in range(NODE_COUNT))
    for j, name in enumerate(BASIN_NAMES)
}

INPUT_DOMAIN = b"TranchNOSE-001A-Input-v1|"
DERIVE_DOMAIN = b"TranchNOSE-001A-Dynamics-Derive-v1|"
FIELD_DOMAIN = b"TranchNOSE-001A-Field-State-v1|"
ELECTRONIC_DOMAIN = b"TranchNOSE-001A-Electronic-State-v1|"
TOPOLOGY_DOMAIN = b"TranchNOSE-001A-Field-Topology-v1|"

# Input-address specifications intentionally use only strings/integers. The
# executable state below may use floats, but the manifest addresses stay simple,
# portable descriptions of the frozen inputs.
ATTRACTOR_SPEC = {
    "kind": "carrier-coded-hadamard-v1",
    "node_count": NODE_COUNT,
    "carrier_phase_eighth_turns": list(range(NODE_COUNT)),
    "sign_patterns": [list(row) for row in SIGN_PATTERNS],
}
INITIAL_FIELD_SPEC = {
    "kind": "target-with-phase-flips-v1",
    "phase_flip_nodes": [0, 1],
}
FIELD_TOPOLOGY_SPEC = {
    "kind": "dense-hebbian-projector-v1",
    "node_count": NODE_COUNT,
    "stored_attractors": len(BASIN_NAMES),
    "gain_ppm": 1_000_000,
}
LOCAL_TOPOLOGY_SPEC = {
    "kind": "ring-administrative-v1",
    "node_count": NODE_COUNT,
    "feeds_field_recurrence": False,
}
NONLINEARITY_SPEC = {
    "kind": "carrier-binary-phase-quantizer-v1",
    "zero_floor": "1e-12",
    "tie_break": "positive",
}
STIMULUS_SPEC = {
    "kind": "temporary-target-seed-v1",
    "active_steps": 2,
    "gain_ppm": 250_000,
}
INITIAL_ELECTRONIC_STATE = tuple(
    {"node": k, "enabled": True, "coupling_gain_ppm": 1_000_000}
    for k in range(NODE_COUNT)
)


def _round_float(value: float) -> float:
    value = round(float(value), 12)
    return 0.0 if value == -0.0 else value


def serialize_field(field: tuple[complex, ...] | list[complex]) -> list[list[float]]:
    return [[_round_float(z.real), _round_float(z.imag)] for z in field]


def initial_field(target: str) -> tuple[complex, ...]:
    if target not in ATTRACTORS:
        raise ValueError(f"unknown target {target}")
    field = list(ATTRACTORS[target])
    for node in INITIAL_FIELD_SPEC["phase_flip_nodes"]:
        field[node] *= -1
    return tuple(field)


def _hexx(domain: bytes, canonical_bytes: Callable[[Any], bytes], value: Any) -> str:
    return "sha256:" + hashlib.sha256(domain + canonical_bytes(value)).hexdigest()


def expected_input_addresses(target: str, canonical_bytes: Callable[[Any], bytes]) -> dict[str, str]:
    if target not in ATTRACTORS:
        raise ValueError(f"unknown target {target}")
    return {
        "candidate_attractors": _hexx(INPUT_DOMAIN, canonical_bytes, ATTRACTOR_SPEC),
        "initial_field": _hexx(
            INPUT_DOMAIN,
            canonical_bytes,
            {"target": target, "spec": INITIAL_FIELD_SPEC},
        ),
        "initial_electronic_state": _hexx(
            INPUT_DOMAIN, canonical_bytes, list(INITIAL_ELECTRONIC_STATE)
        ),
        "field_topology": _hexx(INPUT_DOMAIN, canonical_bytes, FIELD_TOPOLOGY_SPEC),
        "local_topology": _hexx(INPUT_DOMAIN, canonical_bytes, LOCAL_TOPOLOGY_SPEC),
        "nonlinearity": _hexx(INPUT_DOMAIN, canonical_bytes, NONLINEARITY_SPEC),
        "stimulus": _hexx(INPUT_DOMAIN, canonical_bytes, STIMULUS_SPEC),
    }


def validate_condition(condition: dict[str, Any]) -> None:
    expected = {
        "A": (False, False),
        "B": (True, False),
        "C": (True, True),
    }
    label = condition["label"]
    if label not in expected:
        raise ValueError(f"unknown condition {label}")
    actual = (condition["field_recurrence"], condition["electronic_reconstruction"])
    if actual != expected[label]:
        raise ValueError(
            f"condition {label} must be mechanically {expected[label]}, got {actual}"
        )


def verify_manifest_inputs(
    manifest: dict[str, Any], canonical_bytes: Callable[[Any], bytes]
) -> None:
    target = manifest["inputs"]["target"]
    expected = expected_input_addresses(target, canonical_bytes)
    for key, address in expected.items():
        if manifest["inputs"][key] != address:
            raise ValueError(f"manifest input address mismatch for {key}")


def normalized_overlap(
    reference: tuple[complex, ...], field: tuple[complex, ...]
) -> float:
    ref_norm = sum(abs(z) ** 2 for z in reference)
    field_norm = sum(abs(z) ** 2 for z in field)
    if field_norm <= 1e-24:
        return 0.0
    inner = sum(a.conjugate() * b for a, b in zip(reference, field))
    return _round_float((abs(inner) ** 2) / (ref_norm * field_norm))


def overlaps(field: tuple[complex, ...]) -> dict[str, float]:
    return {
        name: normalized_overlap(ATTRACTORS[name], field)
        for name in BASIN_NAMES
    }


def winning_basin(score: dict[str, float]) -> str | None:
    if max(score.values()) <= 1e-15:
        return None
    return max(BASIN_NAMES, key=lambda name: score[name])


def _weights() -> tuple[tuple[complex, ...], ...]:
    rows = []
    for k in range(NODE_COUNT):
        row = []
        for l in range(NODE_COUNT):
            value = sum(
                ATTRACTORS[name][k] * ATTRACTORS[name][l].conjugate()
                for name in BASIN_NAMES
            ) / NODE_COUNT
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


WEIGHTS = _weights()


def _quantize(k: int, value: complex) -> complex:
    if abs(value) < 1e-12:
        return 0j
    carrier = CARRIERS[k]
    projected = value * carrier.conjugate()
    sign = 1 if projected.real >= 0 else -1
    return carrier * sign


def _derived_u32(intervention: dict[str, Any], label: str) -> int:
    payload = (
        f"{intervention['step']}|{intervention['order']}|{intervention['type']}|"
        f"{intervention['parameters'].get('magnitude_ppm', 0)}|{label}"
    ).encode("utf-8")
    return int.from_bytes(
        hashlib.sha256(DERIVE_DOMAIN + payload).digest()[:4], "big"
    )


def _apply_intervention(
    field: list[complex],
    electronics: list[dict[str, Any]],
    active: list[bool],
    intervention: dict[str, Any],
) -> None:
    magnitude = intervention["parameters"].get("magnitude_ppm", 0) / 1_000_000.0
    node = _derived_u32(intervention, "node") % NODE_COUNT
    kind = intervention["type"]

    if kind == "phase_corrupt":
        angle = magnitude * math.pi * 1000.0
        field[node] *= complex(math.cos(angle), math.sin(angle))
    elif kind == "node_remove":
        active[node] = False
        electronics[node]["enabled"] = False
        field[node] = 0j
    elif kind == "noise_inject":
        phase_word = _derived_u32(intervention, "noise-phase")
        angle = (phase_word / 2**32) * 2.0 * math.pi
        amplitude = min(0.35, magnitude * 350.0)
        field[node] += amplitude * complex(math.cos(angle), math.sin(angle))


def simulate(
    manifest: dict[str, Any],
    interventions: list[dict[str, Any]],
) -> dict[str, Any]:
    validate_condition(manifest["condition"])
    target = manifest["inputs"]["target"]
    threshold = manifest["inputs"]["termination"]["recognition_threshold"]
    max_steps = manifest["inputs"]["termination"]["max_steps"]

    field = list(initial_field(target))
    electronics = [dict(item) for item in INITIAL_ELECTRONIC_STATE]
    active = [True] * NODE_COUNT
    by_step: dict[int, list[dict[str, Any]]] = {}
    for intervention in interventions:
        by_step.setdefault(intervention["step"], []).append(intervention)

    history: list[dict[str, Any]] = []
    for step in range(1, max_steps + 1):
        for intervention in by_step.get(step, []):
            _apply_intervention(field, electronics, active, intervention)

        transformed = [0j] * NODE_COUNT
        if manifest["condition"]["field_recurrence"]:
            for k in range(NODE_COUNT):
                if not active[k]:
                    continue
                transformed[k] = sum(
                    WEIGHTS[k][l] * field[l]
                    for l in range(NODE_COUNT)
                    if active[l]
                )

        if step <= STIMULUS_SPEC["active_steps"]:
            gain = STIMULUS_SPEC["gain_ppm"] / 1_000_000.0
            for k in range(NODE_COUNT):
                if active[k]:
                    transformed[k] += gain * ATTRACTORS[target][k]

        if manifest["condition"]["electronic_reconstruction"]:
            # Condition C only: an intentionally explicit reconstruction path.
            for k in range(NODE_COUNT):
                if active[k] and electronics[k]["enabled"]:
                    transformed[k] += ATTRACTORS[target][k]

        field = [
            _quantize(k, transformed[k]) if active[k] else 0j
            for k in range(NODE_COUNT)
        ]
        score = overlaps(tuple(field))
        winner = winning_basin(score)
        history.append(
            {
                "step": step,
                "overlap": score,
                "winning_basin": winner,
                "target_recognized": (
                    winner == target and score[target] >= threshold
                ),
            }
        )

    final_score = history[-1]["overlap"]
    final_winner = history[-1]["winning_basin"]

    lifetime = 0
    for item in reversed(history):
        if item["target_recognized"]:
            lifetime += 1
        else:
            break
    converged = lifetime > 0
    convergence_step = max_steps - lifetime + 1 if converged else None

    return {
        "field": tuple(field),
        "electronics": electronics,
        "active_nodes": active,
        "history": history,
        "final_overlap": final_score,
        "winning_basin": final_winner,
        "converged": converged,
        "convergence_step": convergence_step,
        "attractor_lifetime_steps": lifetime,
    }


def state_digests(
    result: dict[str, Any],
    canonical_bytes: Callable[[Any], bytes],
) -> dict[str, str]:
    return {
        "final_field_digest": _hexx(
            FIELD_DOMAIN, canonical_bytes, serialize_field(result["field"])
        ),
        "final_electronic_state_digest": _hexx(
            ELECTRONIC_DOMAIN, canonical_bytes, result["electronics"]
        ),
        "final_topology_digest": _hexx(
            TOPOLOGY_DOMAIN,
            canonical_bytes,
            {
                "spec": FIELD_TOPOLOGY_SPEC,
                "active_nodes": result["active_nodes"],
            },
        ),
    }
