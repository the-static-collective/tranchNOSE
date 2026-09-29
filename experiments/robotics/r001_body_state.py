"""R001 — deterministic embodied-state protocol crucible.

This is a software model, not physical proof of robotic embodiment or relational
memory. It asks one narrow question: with controller and challenge held fixed,
can declared body/morphology parameters causally change the trajectory?
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Iterable


SCHEMA = "tranchNOSE.robotics.r001/0.1"
DT = 0.05
STEPS = 80
CHALLENGE_STEP = 20
CHALLENGE_IMPULSE = -0.75


@dataclass(frozen=True)
class Controller:
    target_velocity: float = 1.0
    kp: float = 2.0
    command_limit: float = 2.5


@dataclass(frozen=True)
class Body:
    name: str
    mass: float
    drag: float
    traction: float
    compliance: float


BODIES = {
    "light_rigid": Body(
        name="light_rigid", mass=1.0, drag=0.18, traction=1.0, compliance=0.05
    ),
    "heavy_compliant": Body(
        name="heavy_compliant", mass=1.8, drag=0.28, traction=0.82, compliance=0.32
    ),
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _digest(domain: str, value: object) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def _finite_positive(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be positive")


def validate(controller: Controller, body: Body) -> None:
    _finite_positive("kp", controller.kp)
    _finite_positive("command_limit", controller.command_limit)
    _finite_positive("mass", body.mass)
    _finite_positive("traction", body.traction)
    if body.drag < 0 or body.compliance < 0:
        raise ValueError("drag and compliance must be non-negative")


def simulate(
    body: Body,
    controller: Controller = Controller(),
    *,
    steps: int = STEPS,
) -> dict:
    """Run one deterministic 1-D embodied response.

    Controller parameters and update law are identical across body conditions.
    The body contributes mass, drag, traction and compliance. A fixed external
    impulse at CHALLENGE_STEP is the pre-registered ADDRESS/challenge.
    """
    validate(controller, body)
    if steps <= CHALLENGE_STEP + 1:
        raise ValueError("steps must extend beyond the challenge")

    position = 0.0
    velocity = 0.0
    spring_state = 0.0
    trajectory = []

    for step in range(steps):
        error = controller.target_velocity - velocity
        command = max(
            -controller.command_limit,
            min(controller.command_limit, controller.kp * error),
        )

        # Same controller command enters different declared body dynamics.
        drive = command * body.traction
        compliant_force = -body.compliance * spring_state
        acceleration = (drive - body.drag * velocity + compliant_force) / body.mass

        if step == CHALLENGE_STEP:
            velocity += CHALLENGE_IMPULSE

        velocity += acceleration * DT
        position += velocity * DT
        spring_state += (velocity - spring_state) * min(1.0, body.compliance * DT)

        trajectory.append(
            {
                "step": step,
                "position": round(position, 9),
                "velocity": round(velocity, 9),
                "controller_command": round(command, 9),
                "spring_state": round(spring_state, 9),
            }
        )

    final = trajectory[-1]
    post = trajectory[CHALLENGE_STEP:]
    recovery_step = None
    for row in post:
        if abs(row["velocity"] - controller.target_velocity) <= 0.05:
            recovery_step = row["step"]
            break

    inputs = {
        "controller": asdict(controller),
        "body": asdict(body),
        "dt": DT,
        "steps": steps,
        "challenge": {
            "type": "velocity_impulse",
            "step": CHALLENGE_STEP,
            "magnitude": CHALLENGE_IMPULSE,
        },
    }
    trajectory_digest = _digest("TranchNOSE-R001-Trajectory-v1|", trajectory)

    receipt = {
        "schema": SCHEMA,
        "controller_ref": _digest("TranchNOSE-R001-Controller-v1|", asdict(controller)),
        "body_ref": _digest("TranchNOSE-R001-Body-v1|", asdict(body)),
        "input_ref": _digest("TranchNOSE-R001-Input-v1|", inputs),
        "challenge": inputs["challenge"],
        "observations": {
            "final_position": final["position"],
            "final_velocity": final["velocity"],
            "recovery_step": recovery_step,
            "trajectory_digest": trajectory_digest,
        },
        "non_claims": [
            "software dynamics are not physical proof",
            "trajectory difference is not consciousness or personhood evidence",
            "controller equality does not imply complete machine-state equality",
        ],
    }
    receipt["receipt_digest"] = _digest("TranchNOSE-R001-Receipt-v1|", receipt)
    return {"receipt": receipt, "trajectory": trajectory}


def compare_bodies(
    first: str = "light_rigid",
    second: str = "heavy_compliant",
    controller: Controller = Controller(),
) -> dict:
    """Run the registered A/B morphology comparison with one controller."""
    if first not in BODIES or second not in BODIES:
        raise ValueError("unknown body")
    a = simulate(BODIES[first], controller)
    b = simulate(BODIES[second], controller)
    same_controller = a["receipt"]["controller_ref"] == b["receipt"]["controller_ref"]
    different_body = a["receipt"]["body_ref"] != b["receipt"]["body_ref"]
    different_trajectory = (
        a["receipt"]["observations"]["trajectory_digest"]
        != b["receipt"]["observations"]["trajectory_digest"]
    )
    return {
        "schema": "tranchNOSE.robotics.r001-comparison/0.1",
        "first_receipt": a["receipt"]["receipt_digest"],
        "second_receipt": b["receipt"]["receipt_digest"],
        "same_controller": same_controller,
        "different_body": different_body,
        "different_trajectory": different_trajectory,
        "supports_body_causal_relevance_in_model": (
            same_controller and different_body and different_trajectory
        ),
        "non_claim": "model result does not establish the same effect in physical hardware",
    }


if __name__ == "__main__":
    print(json.dumps(compare_bodies(), indent=2, sort_keys=True))
