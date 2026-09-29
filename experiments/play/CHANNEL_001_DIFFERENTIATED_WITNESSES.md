# CHANNEL-001 — Differentiated Witnesses Play

Status: **play / executable intuition probe**

This experiment is inspired by the fact that biological vision uses multiple differentiated receptor classes, but it is **not** a retina model and does not claim biological fidelity.

## Question

With the same number of scalar sensor channels, can differentiated response profiles make more of a registered world set distinguishable than redundant copies of one broadband measurement?

The hidden world has exactly two variables:

- intensity: 1, 2, or 3;
- spectral class: blue, green, or red.

There are therefore 9 registered worlds.

## Two four-channel banks

### Redundant bank

All four channels report the same broadband intensity measure.

```text
R1 = 2 * intensity
R2 = 2 * intensity
R3 = 2 * intensity
R4 = 2 * intensity
```

This bank has four witnesses but only one response profile.

### Differentiated bank

The first channel is broadband. The other three have different overlapping response profiles.

```text
BROAD = 2 * intensity

          S   M   L
blue      3   1   0
green     0   3   1
red       0   1   3
```

Each selective response is multiplied by intensity.

These weights are a toy encoding. They are not measured human cone sensitivities.

## Acceptance

CHANNEL-001 passes its registered play fixture when:

1. both banks have exactly four scalar channels;
2. neither bank receives the spectral label directly;
3. the redundant bank produces fewer unique signatures than registered worlds;
4. the differentiated bank produces a unique signature for every registered world;
5. the target fixture is ambiguous under each individual differentiated channel considered alone;
6. the complete differentiated signature uniquely identifies the target;
7. exact replay is deterministic.

The target fixture is:

```text
spectral class = red
intensity      = 1
```

For that target, no single channel is sufficient over the registered world set.

## Candidate clue

```text
MORE CHANNELS != MORE DISTINCT INFORMATION

DIFFERENTIATION OF RESPONSE
can matter more than redundant witness count.
```

A stronger candidate:

```text
DISTINCTION BETWEEN WITNESSES
can increase distinguishability of the world.
```

## Non-claims

This experiment does not establish that biological rods/cones are optimized by this toy objective, that redundancy is generally inferior, or that specialized channels always improve sensing.

Real sensory systems use redundancy, overlap, adaptation, noise handling, spatial organization, temporal dynamics, and many other mechanisms absent here.

This is only a small exact counterexample to the idea that four nominal sensors necessarily provide four independent dimensions of information.
