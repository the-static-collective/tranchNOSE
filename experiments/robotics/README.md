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

## Planned sequence

- **R002 — Address / Answer:** characteristic challenge-response identity.
- **R003 — Morphology / State Swaps:** controller/body/topology/history counterfactuals.
- **R004 — Bounded Relational Learning:** proposal-only topology adaptation with a separate authority crossing.

Do not skip forward by silently adding adaptive self-modification to R001.
