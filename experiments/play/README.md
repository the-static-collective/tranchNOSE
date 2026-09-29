# Play experiments

This directory is for executable intuition probes that are deliberately weaker than promoted TranchNOSE experiments.

A play result may expose a useful distinction, counterexample, or measurement shape. It does **not** become repository law merely because the code passes.

## DIFFERENCE-001 — Relational Witness

A two-view exact-geometry toy inspired by binocular disparity.

The registered fixture is constructed so:

- left witness alone is ambiguous over multiple depths;
- right witness alone is ambiguous over multiple depths;
- the paired observations identify one registered world;
- the signed disparity relation recovers the target depth exactly.

See [DIFFERENCE_001_RELATIONAL_WITNESS.md](./DIFFERENCE_001_RELATIONAL_WITNESS.md).

Candidate clue:

```text
recoverable-from-relation
!=
recoverable-from-either-part-alone
```

Keep it a clue until another carrier or experiment needs the same primitive.
