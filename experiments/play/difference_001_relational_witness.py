"""DIFFERENCE-001 — exact two-witness relational recovery play.

A small pinhole-stereo toy demonstrating a registered case where each witness
alone is ambiguous over the candidate world set while their relation (disparity)
recovers depth exactly.

This is not a retina model and makes no metaphysical claim about relations.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Iterable


SCHEMA = "tranchNOSE.play.difference-001/0.1"
BASELINE = Fraction(2, 1)
DEPTHS = tuple(range(1, 7))
X_POSITIONS = tuple(range(-10, 11))


@dataclass(frozen=True)
class World:
    x: int
    z: int


TARGET = World(x=0, z=2)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _digest(domain: str, value: object) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def candidate_worlds() -> tuple[World, ...]:
    return tuple(World(x=x, z=z) for z in DEPTHS for x in X_POSITIONS)


def observe(world: World) -> tuple[Fraction, Fraction]:
    if world.z <= 0:
        raise ValueError("depth must be positive")
    half = BASELINE / 2
    left = (Fraction(world.x, 1) + half) / world.z
    right = (Fraction(world.x, 1) - half) / world.z
    return left, right


def disparity(left: Fraction, right: Fraction) -> Fraction:
    return left - right


def depth_from_disparity(value: Fraction) -> Fraction:
    if value == 0:
        raise ValueError("zero disparity has no finite depth in this toy")
    return BASELINE / value


def worlds_matching_left(value: Fraction) -> tuple[World, ...]:
    return tuple(w for w in candidate_worlds() if observe(w)[0] == value)


def worlds_matching_right(value: Fraction) -> tuple[World, ...]:
    return tuple(w for w in candidate_worlds() if observe(w)[1] == value)


def worlds_matching_pair(left: Fraction, right: Fraction) -> tuple[World, ...]:
    return tuple(w for w in candidate_worlds() if observe(w) == (left, right))


def depth_set(worlds: Iterable[World]) -> tuple[int, ...]:
    return tuple(sorted({w.z for w in worlds}))


def run(target: World = TARGET) -> dict:
    left, right = observe(target)
    left_worlds = worlds_matching_left(left)
    right_worlds = worlds_matching_right(right)
    pair_worlds = worlds_matching_pair(left, right)

    left_depths = depth_set(left_worlds)
    right_depths = depth_set(right_worlds)
    pair_depths = depth_set(pair_worlds)
    relation = disparity(left, right)
    recovered_depth = depth_from_disparity(relation)

    observation_payload = {
        "left": _fraction_text(left),
        "right": _fraction_text(right),
    }
    relation_payload = {
        "kind": "signed_disparity",
        "left_minus_right": _fraction_text(relation),
    }

    receipt = {
        "schema": SCHEMA,
        "geometry": {
            "baseline": _fraction_text(BASELINE),
            "registered_depths": list(DEPTHS),
            "registered_x_positions": list(X_POSITIONS),
        },
        "target": {"x": target.x, "z": target.z},
        "left_witness": {
            "observation": _fraction_text(left),
            "candidate_depths": list(left_depths),
            "ambiguous_depth": len(left_depths) > 1,
        },
        "right_witness": {
            "observation": _fraction_text(right),
            "candidate_depths": list(right_depths),
            "ambiguous_depth": len(right_depths) > 1,
        },
        "pair": {
            "candidate_world_count": len(pair_worlds),
            "candidate_depths": list(pair_depths),
            "unique_registered_world": len(pair_worlds) == 1,
        },
        "relation": {
            **relation_payload,
            "recovered_depth": _fraction_text(recovered_depth),
            "matches_target_depth": recovered_depth == target.z,
        },
        "refs": {
            "left_observation_ref": _digest(
                "TranchNOSE-Difference001-Left-v1|",
                {"left": observation_payload["left"]},
            ),
            "right_observation_ref": _digest(
                "TranchNOSE-Difference001-Right-v1|",
                {"right": observation_payload["right"]},
            ),
            "pair_ref": _digest(
                "TranchNOSE-Difference001-Pair-v1|", observation_payload
            ),
            "relation_ref": _digest(
                "TranchNOSE-Difference001-Relation-v1|", relation_payload
            ),
        },
        "supports_relational_recovery_in_registered_geometry": (
            len(left_depths) > 1
            and len(right_depths) > 1
            and len(pair_worlds) == 1
            and recovered_depth == target.z
        ),
        "non_claims": [
            "this is an idealized pinhole-stereo toy, not a retina model",
            "relational recovery here does not imply relation is a physical substance",
            "registered-world insufficiency is not universal sensor insufficiency",
        ],
    }
    receipt["receipt_digest"] = _digest(
        "TranchNOSE-Difference001-Receipt-v1|", receipt
    )
    return receipt


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
