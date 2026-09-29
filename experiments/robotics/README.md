# Robotics experiments

This directory contains bounded software and, later, hardware experiments for the TranchNOSE robotics surface.

## R001 — Body State

Question:

> With controller state and challenge held fixed, can declared body/morphology parameters causally change the machine trajectory?

Run:

```bash
python experiments/robotics/r001_body_state.py
python -m unittest discover -s experiments/robotics -p "test_*.py" -v
```

The current model is deterministic and intentionally small. It compares two declared bodies under one controller and one pre-registered velocity impulse.

Acceptance for this slice:

1. controller references are identical across the A/B body comparison;
2. body references are different;
3. replay of the same inputs is exact;
4. trajectory digests differ when body parameters differ;
5. the receipt preserves the non-claim that simulation is not physical proof.

A positive R001 result demonstrates only that embodiment is causally relevant **inside the declared model**. It does not establish relational memory in hardware.

## R002 — Address / Answer

Question:

> Can machines with the same controller and initial observable state be distinguished by their characteristic responses to a fixed challenge set?

Run:

```bash
python experiments/robotics/r002_address_answer.py
python -m unittest discover -s experiments/robotics -p "test_*.py" -v
```

R002 registers four deterministic external challenges and records an answer set made of response trajectories and derived features. Human-readable body names are explicitly non-causal metadata: renaming an unchanged body must not change its physical-particular reference or answer-set digest.

See [R002_ADDRESS_ANSWER.md](./R002_ADDRESS_ANSWER.md).

## R003 — Counterfactual State / Morphology / History Swaps

Question:

> When controller, body, topology, observable state, latent embodied state, and history provenance are separately addressable, which imported component actually changes the next response?

Run:

```bash
python experiments/robotics/r003_counterfactual_swaps.py
python -m unittest discover -s experiments/robotics -p "test_*.py" -v
```

R003 constructs one-component counterfactual swaps. Controller, body, topology, and latent-state swaps are causally active in the model. A provenance-only history swap is recorded in the receipt but deliberately excluded from the dynamics and therefore must not alter the response.

The key negative control is:

```text
same operative state
+ different history receipt
-> same response
```

while:

```text
same visible snapshot
+ different latent embodied state
-> potentially different future
```

See [R003_COUNTERFACTUAL_SWAPS.md](./R003_COUNTERFACTUAL_SWAPS.md).

## Planned sequence

- **R004 — Bounded Relational Learning:** proposal-only topology adaptation with a separate authority crossing.

Do not skip forward by silently adding adaptive self-modification to R001, R002, or R003.
