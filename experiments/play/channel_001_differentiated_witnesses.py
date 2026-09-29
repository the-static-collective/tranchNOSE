"""CHANNEL-001 — differentiated witness play.

Compares two four-channel sensor banks over an exact registered world set.

The redundant bank repeats one broadband response four times.
The differentiated bank uses one broadband plus three overlapping selective
response profiles.

This is inspired by receptor differentiation but is not a retina model.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable


SCHEMA = "tranchNOSE.play.channel-001/0.1"
INTENSITIES = (1, 2, 3)
SPECTRAL_CLASSES = ("blue", "green", "red")
TARGET_CLASS = "red"
TARGET_INTENSITY = 1

# Toy profiles only. These are not biological cone sensitivity data.
SELECTIVE_PROFILES = {
    "blue": (3, 1, 0),
    "green": (0, 3, 1),
    "red": (0, 1, 3),
}


@dataclass(frozen=True)
class World:
    spectral_class: str
    intensity: int


def worlds() -> tuple[World, ...]:
    return tuple(
        World(spectral_class=spectral_class, intensity=intensity)
        for spectral_class in SPECTRAL_CLASSES
        for intensity in INTENSITIES
    )


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _digest(domain: str, value: object) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def _validate_world(world: World) -> None:
    if world.spectral_class not in SPECTRAL_CLASSES:
        raise ValueError("unknown spectral class")
    if world.intensity not in INTENSITIES:
        raise ValueError("unregistered intensity")


def redundant_signature(world: World) -> tuple[int, int, int, int]:
    _validate_world(world)
    broadband = 2 * world.intensity
    return (broadband, broadband, broadband, broadband)


def differentiated_signature(world: World) -> tuple[int, int, int, int]:
    _validate_world(world)
    s, m, l = SELECTIVE_PROFILES[world.spectral_class]
    intensity = world.intensity
    return (
        2 * intensity,
        s * intensity,
        m * intensity,
        l * intensity,
    )


def worlds_matching_signature(
    signature_fn: Callable[[World], tuple[int, int, int, int]],
    signature: tuple[int, int, int, int],
) -> tuple[World, ...]:
    return tuple(world for world in worlds() if signature_fn(world) == signature)


def worlds_matching_channel(
    signature_fn: Callable[[World], tuple[int, int, int, int]],
    channel_index: int,
    value: int,
) -> tuple[World, ...]:
    if channel_index not in (0, 1, 2, 3):
        raise ValueError("channel index must be 0..3")
    return tuple(
        world
        for world in worlds()
        if signature_fn(world)[channel_index] == value
    )


def signature_classes(
    signature_fn: Callable[[World], tuple[int, int, int, int]]
) -> dict[tuple[int, int, int, int], tuple[World, ...]]:
    classes: dict[tuple[int, int, int, int], list[World]] = {}
    for world in worlds():
        classes.setdefault(signature_fn(world), []).append(world)
    return {signature: tuple(group) for signature, group in classes.items()}


def _world_payload(world: World) -> dict:
    return {
        "spectral_class": world.spectral_class,
        "intensity": world.intensity,
    }


def _worlds_payload(group: tuple[World, ...]) -> list[dict]:
    return [_world_payload(world) for world in group]


def run(
    target: World = World(
        spectral_class=TARGET_CLASS,
        intensity=TARGET_INTENSITY,
    )
) -> dict:
    _validate_world(target)

    redundant = redundant_signature(target)
    differentiated = differentiated_signature(target)

    redundant_classes = signature_classes(redundant_signature)
    differentiated_classes = signature_classes(differentiated_signature)

    redundant_matches = worlds_matching_signature(
        redundant_signature, redundant
    )
    differentiated_matches = worlds_matching_signature(
        differentiated_signature, differentiated
    )

    individual_matches = tuple(
        worlds_matching_channel(
            differentiated_signature,
            channel_index,
            differentiated[channel_index],
        )
        for channel_index in range(4)
    )

    receipt = {
        "schema": SCHEMA,
        "registered_world_count": len(worlds()),
        "channel_count": {
            "redundant": 4,
            "differentiated": 4,
        },
        "target": _world_payload(target),
        "redundant_bank": {
            "signature": list(redundant),
            "unique_signature_count": len(redundant_classes),
            "matching_worlds": _worlds_payload(redundant_matches),
            "target_uniquely_identified": len(redundant_matches) == 1,
        },
        "differentiated_bank": {
            "signature": list(differentiated),
            "unique_signature_count": len(differentiated_classes),
            "matching_worlds": _worlds_payload(differentiated_matches),
            "target_uniquely_identified": len(differentiated_matches) == 1,
            "individual_channel_candidate_counts": [
                len(group) for group in individual_matches
            ],
            "every_individual_channel_ambiguous": all(
                len(group) > 1 for group in individual_matches
            ),
        },
        "refs": {
            "world_set_ref": _digest(
                "TranchNOSE-Channel001-WorldSet-v1|",
                [_world_payload(world) for world in worlds()],
            ),
            "redundant_bank_ref": _digest(
                "TranchNOSE-Channel001-RedundantBank-v1|",
                {"kind": "four-identical-broadband", "gain": 2},
            ),
            "differentiated_bank_ref": _digest(
                "TranchNOSE-Channel001-DifferentiatedBank-v1|",
                {
                    "broadband_gain": 2,
                    "selective_profiles": SELECTIVE_PROFILES,
                },
            ),
            "target_redundant_signature_ref": _digest(
                "TranchNOSE-Channel001-RedundantSignature-v1|",
                list(redundant),
            ),
            "target_differentiated_signature_ref": _digest(
                "TranchNOSE-Channel001-DifferentiatedSignature-v1|",
                list(differentiated),
            ),
        },
        "supports_specialization_distinguishability_in_registered_world": (
            len(redundant_classes) < len(worlds())
            and len(differentiated_classes) == len(worlds())
            and len(redundant_matches) > 1
            and len(differentiated_matches) == 1
            and all(len(group) > 1 for group in individual_matches)
        ),
        "non_claims": [
            "toy selective profiles are not biological cone sensitivity curves",
            "this experiment does not model rods, cones, retina, or perception",
            "redundancy may be valuable for noise tolerance and reliability",
            "registered-world distinguishability is not universal sensor optimality",
        ],
    }
    receipt["receipt_digest"] = _digest(
        "TranchNOSE-Channel001-Receipt-v1|", receipt
    )
    return receipt


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
