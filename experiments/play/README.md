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


## CHANNEL-001 — Differentiated Witnesses

A four-channel exact toy inspired by receptor differentiation.

Both banks receive the same registered 9-world set and expose exactly four scalar outputs:

- the **redundant** bank repeats one broadband response four times;
- the **differentiated** bank uses one broadband plus three overlapping selective response profiles.

For the registered fixture:

```text
4 redundant channels
-> 3 unique signatures across 9 worlds

4 differentiated channels
-> 9 unique signatures across 9 worlds
```

The target is ambiguous under every individual differentiated channel considered alone, but the complete differentiated response uniquely identifies it.

See [CHANNEL_001_DIFFERENTIATED_WITNESSES.md](./CHANNEL_001_DIFFERENTIATED_WITNESSES.md).

Candidate clue:

```text
witness count != independent information dimension
differentiation can create distinguishability
```

This remains play. The response profiles are toy weights, not biological cone-sensitivity measurements.
