# DIFFERENCE-001 — Relational Witness Play

Status: **play / executable intuition probe**

This experiment is inspired by binocular disparity, but it is not a model of the retina, rods/cones, or human perception.

## Question

Can two observations each be insufficient to recover a hidden variable while their relation is sufficient?

The deliberately narrow target is **depth** in an idealized two-view pinhole geometry.

## Registered geometry

Two witnesses occupy a fixed horizontal baseline:

```text
LEFT <------ baseline ------> RIGHT
             |
             |
           target
```

A candidate world contains:

- lateral target position `x`;
- target depth `z`.

Each witness records only one projected coordinate.

For the exact rational toy geometry:

```text
left  = (x + b/2) / z
right = (x - b/2) / z
```

Therefore:

```text
disparity = left - right = b / z
```

and, when disparity is nonzero:

```text
z = b / disparity
```

## Strong fixture

The registered candidate-world set is constructed so that the target fixture has:

```text
LEFT observation alone
-> multiple possible depths

RIGHT observation alone
-> multiple possible depths

(LEFT, RIGHT) pair
-> one registered world

LEFT - RIGHT
-> exact target depth
```

This is stronger than merely showing that two sensors are more accurate than one. Each individual witness is **structurally ambiguous** over the declared candidate set.

## Candidate distinction

```text
WITNESS_A != WITNESS_B
WITNESS != WORLD
PAIR != EITHER PART
RELATION(A, B) MAY CARRY A RECOVERABLE VARIABLE
```

The executable claim is only about this registered geometry.

## Why this belongs in play

This experiment does not prove that "relation is a substance" or that every relational representation contains information absent from its members.

It gives us a small, exact counterexample to a simpler assumption:

> every recoverable variable must already be recoverable from one participating observation considered alone.

Here, it is not.

## Future mutations

Possible follow-on play:

- add noise and ask when relational recovery fails;
- change baseline and measure depth resolution;
- quantize each witness before computing disparity;
- add three wavelength-sensitive channels as a rods/cones-inspired differentiation test;
- port the same insufficiency criterion to two robot contact sensors or two optical field taps.
