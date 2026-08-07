# TranchNOSE

**TranchNode Optical State Experiments**

TranchNOSE is an experimental repository for testing whether mutable physical relation/topology can itself carry reconstructible computational state.

It is adjacent to TranchNode, but it is **not** the TranchNode kernel and it is **not** a Project0 semantic-floor change. It must be free to fail without changing either project's governing laws.

## Core machine model

We model the machine as

\[
M(t)=\{G_{field}(t), G_{local}(t), X(t)\}
\]

with the architectural requirement

\[
G_{field}(t) \neq G_{local}(t)
\]

and with both graphs allowed to change over time.

- **`X(t)` — electronic plane:** persistent memory, identity, gain/nonlinearity, irreversible decisions.
- **`G_local(t)` — coordination plane:** timing, health, slow configuration, repair, topology-change commands. It is physically bandwidth-limited so it cannot carry field-object payloads.
- **`G_field(t)` — field plane:** optical relation, superposition, projection, transformation, recurrence, and resonance.

The hypothesis under test is stronger than "optics can accelerate computation":

\[
State(M) \neq X
\]

That is, the complete computational state of the machine may not be recoverable from electronic memory alone.

## First primitive: a field object

A **field object** `F` is a distributed optical state whose identity is expressed through recurrent participation in the shared field rather than by an authoritative copy held at one node.

Minimal dynamics:

\[
F_{t+1}=f(U(G_t)F_t + B s_t)
\]

where `U(G_t)` is the recurrent/reconfigurable field transformation, `f` supplies required nonlinearity, and `s_t` is a temporary seed.

The first experiment asks one question:

> Can a distributed optical state possess reconstructible identity that survives partial destruction when the coordination plane is physically incapable of carrying the missing pattern?

See [`EXPERIMENT_001_FIELD_OBJECT.md`](./EXPERIMENT_001_FIELD_OBJECT.md).

## Research posture

TranchNOSE distinguishes measured behavior from metaphor.

Do not claim consciousness, mystical holographic memory, or that an object lives "only in light." If an optical field is extinguished and later reconstructed, information necessarily persisted in electronics, topology, material configuration, or their relation.

Useful categories are:

- transient field memory
- structural/topological memory
- electronic memory
- relational memory

The strongest target is **relational memory**: no individual part (or sufficiently small coalition) contains enough information to reconstruct an object directly, while the coupled machine can.

## Lineage

The seed was incubated in `the-static-collective/tranchnode` issue #30, then extracted here so the physical experiment has an independent failure boundary.
