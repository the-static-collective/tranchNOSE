# R002 — Address / Answer

Status: software protocol crucible.

## Question

Can two machines that begin with the same controller state and the same observable kinematic state be distinguished by their characteristic responses to a fixed, pre-registered challenge set?

R002 does **not** define personhood, consciousness, identity in a metaphysical sense, or a physical robotics result. It defines one narrow dynamical observable:

> characteristic response under controlled intervention.

## Why R002 exists

R001 established, inside the declared software model, that identical controller settings can produce different trajectories when body parameters differ.

R002 strengthens the test:

```text
same controller
+ same initial observable state
+ same challenge set
+ different body particular
-> compare answer signatures
```

The goal is to distinguish **state resemblance** from **response identity**.

## Vocabulary

### ADDRESS

An `ADDRESS` is a registered external challenge. It is not semantic language.

R002 v0.1 uses four deterministic challenge classes:

- negative velocity impulse;
- positive velocity impulse;
- bounded external-force window;
- bounded traction-loss window.

### ANSWER

An `ANSWER` is the measured response trajectory and derived response features for one challenge.

The answer contains:

- trajectory digest;
- final velocity;
- minimum/maximum post-address velocity;
- integrated absolute velocity error;
- recovery step.

### ANSWER SET

An `ANSWER SET` is the ordered set of answers to the complete registered challenge set.

Its digest is a compact address for the modeled characteristic response.

## Critical non-collapse

```text
body label != body particular
state snapshot != response identity
answer signature != consciousness
simulation result != hardware result
```

A body's human-readable `name` is excluded from the physical-particular address. Renaming an otherwise identical body must not change its answer set.

## Acceptance

R002 v0.1 passes when:

1. the challenge set is content-addressed and deterministic;
2. identical inputs replay exactly;
3. two body particulars start from the same observable state and controller reference;
4. the two body particulars produce different answer-set digests under the registered challenges;
5. renaming one unchanged body leaves its physical-particular reference and answer-set digest unchanged;
6. receipts preserve explicit non-claims.

A positive result establishes only that, in the declared model, challenge-response behavior contains information not supplied by the body label or controller reference alone.
