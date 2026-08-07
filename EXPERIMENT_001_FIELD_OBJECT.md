# Experiment 001 — Field Object Test

## Question

Can a distributed optical state possess reconstructible identity that survives partial destruction when the coordination plane is physically incapable of carrying the missing pattern?

## Machine

Start with **8 nodes**.

Each node has:

- an electronic controller;
- optical amplitude/phase modulation (I/Q or equivalent);
- photodetection;
- an independent, physically rate-limited coordination link.

The optical fabric provides passive + reconfigurable mixing and a recurrent closed loop. Prefer a global heterodyne or otherwise phase-resolved tap in addition to local node measurements.

## Dynamics

Use the minimal model

\[
F_{t+1}=f(U(G_t)F_t+B s_t)
\]

where:

- `F_t` is the optical field state;
- `U(G_t)` is the recurrent/reconfigurable transformation defined by the field graph;
- `f` is the required nonlinearity supplied by detection/electronic response/remodulation;
- `s_t` is a temporary write stimulus.

Define exactly four candidate attractors for the first proof:

- `F_A`
- `F_B`
- `F_C`
- `F_D`

## No-cheating boundary

`G_local` may carry only:

- clock / phase-reference information;
- health telemetry;
- slow coupling settings;
- commands that reconfigure `G_field`.

It must not carry:

- `F` payloads;
- object labels during completion;
- full reconstruction coefficients;
- node-state traffic at sufficient bandwidth to reconstruct the optical object electronically.

Enforce this with a hardware bandwidth ceiling, not only software policy. The chosen carrier is secondary; the auditable information-capacity limit is what matters.

## Primary observable

For target object `F_j`, measure normalized overlap

\[
C_j(t)=\frac{|\langle F_j,F(t)\rangle|^2}{\|F_j\|^2\|F(t)\|^2}.
\]

Pre-register the recognition threshold before running destructive tests.

## Experimental contract

A candidate field object is tested for:

1. **Write** — seed the field from a known stimulus.
2. **Recognize** — recover repeatable target overlap above threshold.
3. **Partial destruction** — remove phase information, modes, wavelengths, nodes, or paths.
4. **Pattern completion** — reconstruct the correct attractor from an incomplete cue.
5. **Basin separation** — distinguish nearby candidate objects reliably.
6. **Controlled transformation** — intentionally drive `F_A -> F_B` through explicit changes in dynamics/topology.
7. **Membership tolerance** — retain recognizable identity while nodes enter or leave.
8. **Reinstantiation** — extinguish the optical field completely and determine which persistent variables are sufficient to regenerate the object.

Items 1–5 are the minimum bar for claiming a physical representation primitive.

## Comparison conditions

Run the same hardware under three conditions:

| Condition | Optical recurrence | Electronic reconstruction |
|---|---:|---:|
| A | No | No |
| B | Yes | No |
| C | Yes | Allowed |

**Condition B is the architecture under test.**

A meaningful positive result requires B to show material pattern-completion behavior beyond A while bandwidth accounting and instrumentation show that no electronic subsystem possessed enough information to recreate the target directly.

## Destruction sweep

Measure correct-basin recovery while perturbing:

- 10%, 20%, 30%, 40%, 50% of phase information;
- node removal;
- wavelength/mode removal;
- coupling perturbation;
- path interruption;
- injected noise.

Record at minimum:

- basin volume;
- convergence time;
- attractor lifetime;
- inter-attractor distance;
- perturbation tolerance;
- node-loss tolerance;
- energy per settle;
- local-vs-global information sufficiency.

## Strong extinction test

After demonstrating completion, set the optical field to zero long enough that optical coherence or cavity persistence cannot bridge the interval.

On restart from a partial cue, classify any recovered identity as one or more of:

- **transient field memory** — identity exists only while the field persists;
- **structural/topological memory** — identity survives in `G_field` configuration;
- **electronic memory** — identity survives in `X`;
- **relational memory** — neither `X` nor `G_field` alone is sufficient, but their coupled relation regenerates the object.

Do not describe reappearance after extinction as proof that memory lived only in circulating light.

## Information-insufficiency target

The strongest result is not merely

\[
F \neq \sum_i x_i.
\]

Instead test whether individual nodes, and preferably small coalitions, are informationally insufficient to reconstruct the full object while the coupled machine succeeds.

Conceptually:

\[
I(X_k;F_{object}) \ll H(F_{object})
\]

and for selected coalitions `S`,

\[
I(X_S;F_{object}) < H(F_{object}).
\]

The practical burden is to demonstrate insufficiency through controlled state access, bandwidth accounting, ablation, and reconstruction tests rather than assuming it from architecture.

## Failure interpretation

A negative result does not identify a single cause. Distinguish among at least:

- insufficient recurrence;
- insufficient/non-useful nonlinearity;
- poor SNR;
- phase drift;
- badly separated basins;
- unstable loop gain;
- O-E-O latency;
- quantization;
- unsuitable representation;
- inadequate measurement.

The experiment should produce enough instrumentation to discriminate among these where possible.

## Stop condition

Do **not** proceed to adaptive topology learning until Experiment 001 establishes field objects under the no-cheating condition.

The follow-up loop is intentionally deferred:

\[
field\ dynamics \rightarrow local\ observation \rightarrow topology\ modification \rightarrow new\ field\ dynamics.
\]

Only after Experiment 001 succeeds should TranchNOSE test whether a machine can learn which physical relationships should exist.
