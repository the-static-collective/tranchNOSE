# FIELD LAB 001 — Relational Perturbation Instrument

FIELD LAB is a bounded TranchNOSE instrument for asking:

> What changes when one declared relation/configuration changes while declared invariants remain fixed?

It is not a generic causal oracle. The founding executable carrier is the already-established robotics R001 software model.

```text
PARTICULAR PACKET
+ CURRENT FIELD
+ DECLARED INVARIANTS
+ ONE DECLARED PERTURBATION
        ↓
     FIELD LAB
        ↓
BEFORE / AFTER FIELD
INVARIANT CHECKS
TRAJECTORY DELTA
COUNTERFACTUAL CANDIDATE
CAUSAL-EVIDENCE SCOPE
NON-CLAIMS
RECEIPT
```

## Founding experiment

`robotics.r001.body-morphology`

The current implementation holds these quantities fixed:

- controller;
- challenge;
- integration timestep;
- step count.

It changes the declared body/morphology condition and compares the resulting deterministic trajectories.

The first accepted bodies are the exact R001 bodies already owned by TranchNOSE:

- `light_rigid`;
- `heavy_compliant`.

FIELD LAB refuses an undeclared invariant set or a no-op body perturbation.

## Laws

```text
RELATIONAL DIFFERENCE != CAUSATION
CONTROLLED PERTURBATION -> CAUSAL EVIDENCE
CAUSAL EVIDENCE != UNIVERSAL LAW
COUNTERFACTUAL != HISTORY
OBSERVE != AUTHORIZE != MUTATE
```

The arrow in `CONTROLLED PERTURBATION -> CAUSAL EVIDENCE` means that a properly bounded intervention can contribute evidence about causal relevance inside the declared model. It does not promote the result into a universal law or physical proof.

## Authority boundary

FIELD LAB can:

- observe a deterministic before/after experiment;
- report which declared invariants held;
- report trajectory differences;
- produce a bounded counterfactual candidate;
- return a content-addressed receipt.

FIELD LAB cannot:

- admit an artifact;
- select a life decision;
- mutate external state;
- rewrite a witnessed occurrence;
- claim physical proof from the software crucible.

## Rack aperture

TranchNOSE opts this instrument into GHoT through:

`integrations/ghot/adapter-manifest.json`

Capability:

`analysis.tranchnose.field-lab`

The adapter uses the existing GHoT stdin-JSON/stdout-JSON contract.

This means the GHoT Instrument Rack may project FIELD LAB as a proposal-only card when the human explicitly supplies the manifest path. TranchNOSE retains instrument semantics.

```text
RACK DISCOVERY != EXECUTION
GHOT CARD != TRANCHNOSE AUTHORITY
FIELD LAB RESULT != HUMAN SELECTION
```

No STATIC OS boot dependency is created by this aperture.

## Example

```json
{
  "experiment": "robotics.r001.body-morphology",
  "particular_packet": {
    "packet_id": "example:001"
  },
  "current_field": {
    "body": "light_rigid"
  },
  "perturbation": {
    "body": "heavy_compliant"
  },
  "declared_invariants": [
    "controller",
    "challenge",
    "dt",
    "steps"
  ]
}
```

Run directly:

```bash
printf '%s' '<request-json>' | python3 integrations/ghot/field_lab_adapter.py
```

Or expose it to GHoT:

```bash
export GHOT_ADAPTER_MANIFESTS=/path/to/tranchNOSE/integrations/ghot/adapter-manifest.json
```

The card remains proposal-only until GHoT receives a separate explicit dispatch.
