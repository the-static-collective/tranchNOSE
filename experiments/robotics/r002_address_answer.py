"""R002 — deterministic ADDRESS / ANSWER challenge-response crucible.

R002 tests characteristic response under controlled interventions. It does not
treat response signatures as consciousness, personhood, or physical proof.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any

from r001_body_state import BODIES, Body, Controller, DT, validate


SCHEMA = "tranchNOSE.robotics.r002/0.1"
STEPS = 90
INITIAL_OBSERVABLE = {
    "position": 0.0,
    "velocity": 0.0,
    "spring_state": 0.0,
}

CHALLENGES = (
    {
        "id": "impulse_back",
        "kind": "velocity_impulse",
        "step": 20,
        "magnitude": -0.75,
    },
    {
        "id": "impulse_forward",
        "kind": "velocity_impulse",
        "step": 20,
        "magnitude": 0.55,
    },
    {
        "id": "load_window",
        "kind": "external_force_window",
        "step": 22,
        "end_step": 31,
        "magnitude": -0.65,
    },
    {
        "id": "traction_window",
        "kind": "traction_scale_window",
        "step": 22,
        "end_step": 35,
        "scale": 0.55,
    },
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _digest(domain: str, value: object) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def _body_particular(body: Body) -> dict[str, float]:
    """Physical/model parameters only. Human-readable name is non-causal metadata."""
    return {
        "mass": body.mass,
        "drag": body.drag,
        "traction": body.traction,
        "compliance": body.compliance,
    }


def _challenge_end(challenge: dict[str, Any]) -> int:
    return int(challenge.get("end_step", challenge["step"]))


def _validate_challenge(challenge: dict[str, Any]) -> None:
    required = {"id", "kind", "step"}
    if not required.issubset(challenge):
        raise ValueError("challenge missing identity/kind/step")
    if challenge["kind"] not in {
        "velocity_impulse",
        "external_force_window",
        "traction_scale_window",
    }:
        raise ValueError("unknown challenge kind")
    if not isinstance(challenge["step"], int) or challenge["step"] < 0:
        raise ValueError("invalid challenge step")
    end = _challenge_end(challenge)
    if end < challenge["step"] or end >= STEPS:
        raise ValueError("invalid challenge window")
    if challenge["kind"] == "traction_scale_window":
        scale = challenge.get("scale")
        if not isinstance(scale, (int, float)) or not 0 < scale <= 1:
            raise ValueError("traction scale must be in (0, 1]")
    else:
        magnitude = challenge.get("magnitude")
        if not isinstance(magnitude, (int, float)):
            raise ValueError("challenge magnitude required")


def _run_answer(
    body: Body,
    controller: Controller,
    challenge: dict[str, Any],
) -> dict[str, Any]:
    validate(controller, body)
    _validate_challenge(challenge)

    position = INITIAL_OBSERVABLE["position"]
    velocity = INITIAL_OBSERVABLE["velocity"]
    spring_state = INITIAL_OBSERVABLE["spring_state"]
    trajectory: list[dict[str, Any]] = []

    for step in range(STEPS):
        error = controller.target_velocity - velocity
        command = max(
            -controller.command_limit,
            min(controller.command_limit, controller.kp * error),
        )

        traction_scale = 1.0
        external_force = 0.0
        active_window = challenge["step"] <= step <= _challenge_end(challenge)

        if challenge["kind"] == "traction_scale_window" and active_window:
            traction_scale = float(challenge["scale"])
        elif challenge["kind"] == "external_force_window" and active_window:
            external_force = float(challenge["magnitude"])

        drive = command * body.traction * traction_scale
        compliant_force = -body.compliance * spring_state
        acceleration = (
            drive - body.drag * velocity + compliant_force + external_force
        ) / body.mass

        if challenge["kind"] == "velocity_impulse" and step == challenge["step"]:
            velocity += float(challenge["magnitude"])

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
                "traction_scale": round(traction_scale, 9),
                "external_force": round(external_force, 9),
            }
        )

    start = challenge["step"]
    post = trajectory[start:]
    recovery_step = None
    for row in trajectory[_challenge_end(challenge):]:
        if abs(row["velocity"] - controller.target_velocity) <= 0.05:
            recovery_step = row["step"]
            break

    integrated_error = round(
        sum(abs(row["velocity"] - controller.target_velocity) for row in post) * DT,
        9,
    )
    features = {
        "final_velocity": trajectory[-1]["velocity"],
        "min_post_velocity": round(min(row["velocity"] for row in post), 9),
        "max_post_velocity": round(max(row["velocity"] for row in post), 9),
        "integrated_abs_velocity_error": integrated_error,
        "recovery_step": recovery_step,
    }
    return {
        "challenge_id": challenge["id"],
        "challenge_ref": _digest("TranchNOSE-R002-Challenge-v1|", challenge),
        "features": features,
        "trajectory_digest": _digest(
            "TranchNOSE-R002-Answer-Trajectory-v1|", trajectory
        ),
    }


def address_answer(
    body: Body,
    controller: Controller = Controller(),
) -> dict[str, Any]:
    """Return a deterministic answer set for one body particular."""
    validate(controller, body)
    for challenge in CHALLENGES:
        _validate_challenge(challenge)

    particular = _body_particular(body)
    answers = [_run_answer(body, controller, challenge) for challenge in CHALLENGES]
    challenge_set_ref = _digest(
        "TranchNOSE-R002-Challenge-Set-v1|", list(CHALLENGES)
    )
    initial_observable_ref = _digest(
        "TranchNOSE-R002-Initial-Observable-v1|", INITIAL_OBSERVABLE
    )
    answer_set_digest = _digest(
        "TranchNOSE-R002-Answer-Set-v1|",
        {
            "challenge_set_ref": challenge_set_ref,
            "answers": answers,
        },
    )

    receipt = {
        "schema": SCHEMA,
        "body_label": body.name,
        "body_particular_ref": _digest(
            "TranchNOSE-R002-Body-Particular-v1|", particular
        ),
        "controller_ref": _digest(
            "TranchNOSE-R002-Controller-v1|", asdict(controller)
        ),
        "initial_observable_ref": initial_observable_ref,
        "challenge_set_ref": challenge_set_ref,
        "answers": answers,
        "answer_set_digest": answer_set_digest,
        "non_claims": [
            "answer signature is not consciousness or personhood evidence",
            "software response is not physical hardware proof",
            "body label is presentation metadata, not body identity",
        ],
    }
    receipt["receipt_digest"] = _digest("TranchNOSE-R002-Receipt-v1|", receipt)
    return receipt


def compare_answerability(
    first: str = "light_rigid",
    second: str = "heavy_compliant",
    controller: Controller = Controller(),
) -> dict[str, Any]:
    if first not in BODIES or second not in BODIES:
        raise ValueError("unknown body")

    a = address_answer(BODIES[first], controller)
    b = address_answer(BODIES[second], controller)

    same_controller = a["controller_ref"] == b["controller_ref"]
    same_initial_observable = (
        a["initial_observable_ref"] == b["initial_observable_ref"]
    )
    different_particular = a["body_particular_ref"] != b["body_particular_ref"]
    different_answers = a["answer_set_digest"] != b["answer_set_digest"]

    return {
        "schema": "tranchNOSE.robotics.r002-comparison/0.1",
        "first_receipt": a["receipt_digest"],
        "second_receipt": b["receipt_digest"],
        "same_controller": same_controller,
        "same_initial_observable": same_initial_observable,
        "different_body_particular": different_particular,
        "different_answer_set": different_answers,
        "supports_response_discriminability_in_model": (
            same_controller
            and same_initial_observable
            and different_particular
            and different_answers
        ),
        "non_claim": (
            "response discriminability in this model is not a personhood, "
            "consciousness, or physical-hardware claim"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(compare_answerability(), indent=2, sort_keys=True))
