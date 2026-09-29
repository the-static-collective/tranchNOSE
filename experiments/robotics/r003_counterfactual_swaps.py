"""R003 — deterministic counterfactual swap laboratory.

Separates controller, body, topology, observable state, latent embodied state,
and history provenance so counterfactual combinations can be tested without
turning provenance into a hidden physical input.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from r001_body_state import BODIES, Body, Controller, DT, validate


SCHEMA = "tranchNOSE.robotics.r003/0.1"
STEPS = 70
CHALLENGE = {
    "id": "registered_impulse_back",
    "kind": "velocity_impulse",
    "step": 12,
    "magnitude": -0.60,
}


@dataclass(frozen=True)
class Topology:
    name: str
    drive_gain: float
    compliance_gain: float
    damping_gain: float


@dataclass(frozen=True)
class PreparedState:
    position: float
    velocity: float
    spring_state: float


@dataclass(frozen=True)
class HistoryRecord:
    history_id: str
    preparation_ref: str
    note: str


CONTROLLER_A = Controller(target_velocity=1.0, kp=2.0, command_limit=2.5)
CONTROLLER_B = Controller(target_velocity=0.82, kp=2.35, command_limit=2.5)

TOPOLOGIES = {
    "direct": Topology(
        name="direct",
        drive_gain=1.0,
        compliance_gain=1.0,
        damping_gain=1.0,
    ),
    "soft_coupled": Topology(
        name="soft_coupled",
        drive_gain=0.88,
        compliance_gain=1.55,
        damping_gain=1.12,
    ),
}

STATE_A = PreparedState(position=0.0, velocity=0.0, spring_state=0.0)
STATE_B = PreparedState(position=0.0, velocity=0.0, spring_state=0.85)

HISTORY_A = HistoryRecord(
    history_id="history_A",
    preparation_ref="fixture:calm-preparation",
    note="baseline provenance record",
)
HISTORY_B = HistoryRecord(
    history_id="history_B",
    preparation_ref="fixture:loaded-preparation",
    note="alternate provenance record",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _digest(domain: str, value: object) -> str:
    return "sha256:" + sha256(domain.encode("utf-8") + _canonical(value)).hexdigest()


def _body_particular(body: Body) -> dict[str, float]:
    return {
        "mass": body.mass,
        "drag": body.drag,
        "traction": body.traction,
        "compliance": body.compliance,
    }


def _topology_particular(topology: Topology) -> dict[str, float]:
    return {
        "drive_gain": topology.drive_gain,
        "compliance_gain": topology.compliance_gain,
        "damping_gain": topology.damping_gain,
    }


def _observable_state(state: PreparedState) -> dict[str, float]:
    return {
        "position": state.position,
        "velocity": state.velocity,
    }


def _latent_state(state: PreparedState) -> dict[str, float]:
    return {"spring_state": state.spring_state}


def _validate_topology(topology: Topology) -> None:
    for name, value in _topology_particular(topology).items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{name} must be positive")


def _validate_state(state: PreparedState) -> None:
    for name, value in asdict(state).items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")


def run_counterfactual(
    *,
    controller: Controller,
    body: Body,
    topology: Topology,
    state: PreparedState,
    history: HistoryRecord,
) -> dict[str, Any]:
    """Run one registered challenge from an explicitly composed machine state.

    history is recorded in the receipt but is never consulted by the dynamics.
    """
    validate(controller, body)
    _validate_topology(topology)
    _validate_state(state)

    position = float(state.position)
    velocity = float(state.velocity)
    spring_state = float(state.spring_state)
    trajectory: list[dict[str, Any]] = []

    for step in range(STEPS):
        error = controller.target_velocity - velocity
        command = max(
            -controller.command_limit,
            min(controller.command_limit, controller.kp * error),
        )

        drive = command * body.traction * topology.drive_gain
        compliant_force = (
            -body.compliance * topology.compliance_gain * spring_state
        )
        damping_force = -body.drag * topology.damping_gain * velocity
        acceleration = (
            drive + compliant_force + damping_force
        ) / body.mass

        if step == CHALLENGE["step"]:
            velocity += float(CHALLENGE["magnitude"])

        velocity += acceleration * DT
        position += velocity * DT
        spring_state += (
            velocity - spring_state
        ) * min(1.0, body.compliance * topology.compliance_gain * DT)

        trajectory.append(
            {
                "step": step,
                "position": round(position, 9),
                "velocity": round(velocity, 9),
                "spring_state": round(spring_state, 9),
                "controller_command": round(command, 9),
            }
        )

    post = trajectory[CHALLENGE["step"]:]
    response = {
        "trajectory_digest": _digest(
            "TranchNOSE-R003-Trajectory-v1|", trajectory
        ),
        "final_position": trajectory[-1]["position"],
        "final_velocity": trajectory[-1]["velocity"],
        "min_post_velocity": round(min(x["velocity"] for x in post), 9),
        "max_post_velocity": round(max(x["velocity"] for x in post), 9),
        "integrated_abs_velocity_error": round(
            sum(
                abs(x["velocity"] - controller.target_velocity)
                for x in post
            ) * DT,
            9,
        ),
    }

    receipt = {
        "schema": SCHEMA,
        "controller_ref": _digest(
            "TranchNOSE-R003-Controller-v1|", asdict(controller)
        ),
        "body_label": body.name,
        "body_particular_ref": _digest(
            "TranchNOSE-R003-Body-v1|", _body_particular(body)
        ),
        "topology_label": topology.name,
        "topology_particular_ref": _digest(
            "TranchNOSE-R003-Topology-v1|", _topology_particular(topology)
        ),
        "observable_state_ref": _digest(
            "TranchNOSE-R003-Observable-v1|", _observable_state(state)
        ),
        "latent_state_ref": _digest(
            "TranchNOSE-R003-Latent-v1|", _latent_state(state)
        ),
        "history_ref": _digest(
            "TranchNOSE-R003-History-v1|", asdict(history)
        ),
        "challenge_ref": _digest(
            "TranchNOSE-R003-Challenge-v1|", CHALLENGE
        ),
        "response": response,
        "non_claims": [
            "history provenance is recorded but not a dynamics input",
            "latent spring state is a model variable, not proof of hidden physical memory",
            "software counterfactuals are not physical hardware proof",
        ],
    }
    receipt["receipt_digest"] = _digest("TranchNOSE-R003-Receipt-v1|", receipt)
    return receipt


def counterfactual_matrix() -> dict[str, Any]:
    """Return the baseline plus one-component swaps."""
    body_a = BODIES["light_rigid"]
    body_b = BODIES["heavy_compliant"]
    topology_a = TOPOLOGIES["direct"]
    topology_b = TOPOLOGIES["soft_coupled"]

    runs = {
        "baseline_A": run_counterfactual(
            controller=CONTROLLER_A,
            body=body_a,
            topology=topology_a,
            state=STATE_A,
            history=HISTORY_A,
        ),
        "controller_swap": run_counterfactual(
            controller=CONTROLLER_B,
            body=body_a,
            topology=topology_a,
            state=STATE_A,
            history=HISTORY_A,
        ),
        "body_swap": run_counterfactual(
            controller=CONTROLLER_A,
            body=body_b,
            topology=topology_a,
            state=STATE_A,
            history=HISTORY_A,
        ),
        "topology_swap": run_counterfactual(
            controller=CONTROLLER_A,
            body=body_a,
            topology=topology_b,
            state=STATE_A,
            history=HISTORY_A,
        ),
        "latent_state_swap": run_counterfactual(
            controller=CONTROLLER_A,
            body=body_a,
            topology=topology_a,
            state=STATE_B,
            history=HISTORY_B,
        ),
        "provenance_only_swap": run_counterfactual(
            controller=CONTROLLER_A,
            body=body_a,
            topology=topology_a,
            state=STATE_A,
            history=HISTORY_B,
        ),
    }

    baseline = runs["baseline_A"]
    baseline_response = baseline["response"]["trajectory_digest"]
    summary = {}

    for name, receipt in runs.items():
        summary[name] = {
            "receipt_digest": receipt["receipt_digest"],
            "response_digest": receipt["response"]["trajectory_digest"],
            "response_changed_from_baseline": (
                receipt["response"]["trajectory_digest"] != baseline_response
            ),
            "same_observable_as_baseline": (
                receipt["observable_state_ref"] == baseline["observable_state_ref"]
            ),
            "same_latent_as_baseline": (
                receipt["latent_state_ref"] == baseline["latent_state_ref"]
            ),
            "same_history_as_baseline": (
                receipt["history_ref"] == baseline["history_ref"]
            ),
        }

    return {
        "schema": "tranchNOSE.robotics.r003-matrix/0.1",
        "runs": summary,
        "supports_declared_separation_in_model": (
            summary["controller_swap"]["response_changed_from_baseline"]
            and summary["body_swap"]["response_changed_from_baseline"]
            and summary["topology_swap"]["response_changed_from_baseline"]
            and summary["latent_state_swap"]["response_changed_from_baseline"]
            and summary["latent_state_swap"]["same_observable_as_baseline"]
            and not summary["latent_state_swap"]["same_latent_as_baseline"]
            and not summary["provenance_only_swap"]["same_history_as_baseline"]
            and not summary["provenance_only_swap"]["response_changed_from_baseline"]
        ),
        "non_claim": (
            "this matrix validates separation inside the declared model; "
            "it does not establish physical-hardware memory or metaphysical identity"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(counterfactual_matrix(), indent=2, sort_keys=True))
