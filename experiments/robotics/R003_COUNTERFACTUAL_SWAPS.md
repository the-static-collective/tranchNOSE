# R003 — Counterfactual State / Morphology / History Swaps

Status: deterministic software counterfactual crucible.

## Question

When a robot's controller, body, topology, observable state, latent embodied state, and history record are separately addressable, which imported component actually changes the next response?

R003 exists to prevent a dangerous collapse:

    where something came from
    !=
    what is causally active now

A receipt can preserve provenance without implying that provenance itself exerts physical force.

## State decomposition

R003 treats one modeled machine state as:

    M = {
      X,          controller
      B,          body particular
      G_body,     body/mechanical topology
      O,          current observable kinematic state
      L,          latent embodied state
      H           attributable history record
    }

The terms are separately content-addressed.

### Observable state

For v0.1:

- position;
- velocity.

### Latent embodied state

For v0.1:

- compliant/spring state.

The latent state can be counterfactually swapped while the visible position and velocity remain identical.

### History record

The history record is provenance: an attributable statement about preparation lineage.

It is deliberately **not** passed into the dynamics.

This permits a negative control:

    same X + B + G_body + O + L
    different H
    -> same physical answer

If changing only the history record changed the modeled trajectory, the simulator would be smuggling narration into physics.

## Registered counterfactuals

Starting from baseline A, R003 constructs:

1. controller swap;
2. body swap;
3. topology swap;
4. latent-state swap with observable state held fixed;
5. provenance-only history swap.

The first four are causally active model components and are expected to be capable of changing response.

The fifth is an evidence-only change and must not change the response trajectory.

## Core distinctions

    observable state != complete operative state
    history receipt   != latent memory
    provenance        != causal sufficiency
    same snapshot     != same future
    same future       != same provenance

## Acceptance

R003 v0.1 passes when:

- exact replay is deterministic;
- all component references are independently addressable;
- the latent-state swap preserves the observable-state reference while changing the latent-state reference;
- controller/body/topology/latent swaps each change the registered response in the current fixture;
- provenance-only swap changes the receipt/history reference but not the response digest;
- no result is promoted to a physical-hardware or metaphysical claim.

## Non-claims

R003 does not establish that real robots contain hidden "history fields," that provenance is physically causal, or that a software spring variable is a complete model of embodiment.

It establishes only whether the declared simulator correctly separates causal state from evidence about state.
