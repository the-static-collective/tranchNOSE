# Experiment 001A — Receipt Contract v0.1

Experiment 001A is receipt-first. Simulator implementations are conforming only when a run can be reconstructed from its receipt plus content-addressed inputs without consulting hidden process state.

## Invariants

1. **A receipt is evidence, not narration.** Every field required to interpret a result is explicit and machine-readable.
2. **Determinism is an acceptance condition.** Replaying the same receipt inputs under the same implementation version must reproduce the same deterministic outputs and transcript digest.
3. **Wall-clock time is not an input.** Timestamps may describe publication, but MUST NOT affect simulation state, IDs, schedules, random choices, or results.
4. **Randomness is named and seeded.** Every pseudorandom stream has an algorithm identifier, seed, and stream name. No ambient RNG is permitted.
5. **Conditions A/B/C are mechanically distinct.** The receipt records which pathways are enabled, not merely a condition label.
6. **Observed state and interventions are separate.** A measurement never silently mutates the machine. Scrub/replay/shuffle/swap actions are recorded as interventions.
7. **Coordination traffic is auditable.** The complete modeled `G_local` transcript is represented by a digest plus deterministic accounting sufficient to reproduce capacity and leakage tests.
8. **Predictability is not causal sufficiency.** Decoder results and intervention results occupy separate receipt fields.
9. **Attribution is derived, never assumed.** `field-supported`, `electronic-supported`, `topology-supported`, `relational`, or `unresolved` must be justified from recorded controls.
10. **Failures remain specific.** If instrumentation can distinguish a measured failure cause, it must not be collapsed into generic non-convergence.

## Deterministic identity

A run has two identities:

- `run_id`: stable semantic identity derived from canonical run inputs;
- `receipt_digest`: digest of the complete canonical receipt after deterministic outputs are populated.

For v0.1, implementations SHOULD canonicalize JSON using RFC 8785 JCS and digest UTF-8 canonical bytes with SHA-256.

Recommended domains:

- `run_id = sha256("TranchNOSE-001A-Run-v1|" || JCS(run_identity_input))`
- `receipt_digest = sha256("TranchNOSE-001A-Receipt-v1|" || JCS(receipt_without_receipt_digest))`

`run_identity_input` contains only variables that can causally affect the run:

- schema and experiment version;
- simulator implementation identifier;
- condition mechanics;
- PRNG algorithm + seeds/streams;
- target object definition/address;
- initial field/electronic/topology state addresses;
- nonlinearity and dynamics parameters;
- intervention schedule;
- step/termination policy.

It MUST NOT contain publication timestamps, machine hostname, process ID, filesystem path, or other ambient metadata.

## Replay contract

A conforming replay command receives exactly:

1. a receipt or replay manifest;
2. all content-addressed referenced inputs;
3. the simulator implementation named by the receipt.

Replay succeeds only if it reproduces, bit-for-bit where specified:

- final field digest;
- final electronic-state digest;
- final topology digest;
- complete `G_local` transcript digest;
- overlap vector;
- winning basin;
- convergence classification and step;
- information-budget totals;
- deterministic failure classification;
- receipt digest.

Floating-point implementations MUST define numeric encoding and comparison policy before results are accepted. Prefer deterministic fixed-point or explicitly quantized numeric serialization for cross-runtime fixtures. Until cross-runtime parity exists, the receipt records the runtime/math backend and replay is required on that declared backend.

## Receipt sections

### `identity`
Schema, experiment, implementation, run ID, and receipt digest.

### `randomness`
Named PRNG algorithm plus independent deterministic streams. Every stochastic operation must name its stream.

### `condition`
Mechanically records whether field recurrence and electronic reconstruction are enabled, plus permitted `G_local` message classes and hard information ceiling.

### `inputs`
Content-addressed initial state and model configuration: candidate attractors, target, field/electronic states, `G_field`, `G_local`, nonlinearity, seed stimulus, and termination policy.

### `interventions`
Ordered, step-addressed mutations such as `phase_corrupt`, `node_remove`, `field_scrub`, `electronic_scrub`, `trace_replay`, `trace_shuffle`, `state_swap`, and `topology_swap`.

Interventions with the same step execute in ascending `order`.

### `observations`
Measured results only: overlap time series or summary, convergence, basin winner, lifetime, perturbation outcome, state digests, and instrumentation.

### `coordination_audit`
Exact transcript digest, message/bit counts, ceiling compliance, leakage decoder result, and replay/shuffle causal-control results.

### `causal_attribution`
Results from the 2x2 ablation matrix and state-swap controls. This section distinguishes evidence from the final attribution label.

### `failure`
`null` for a successful run. Otherwise contains a specific class plus measured evidence and the step where failure became terminal.

## Initial failure vocabulary

Use the narrowest supported class:

- `insufficient_recurrence`
- `nonlinearity_not_useful`
- `snr_below_floor`
- `phase_drift`
- `basins_not_separated`
- `unstable_loop_gain`
- `oeo_latency_instability`
- `quantization_instability`
- `representation_unsuitable`
- `measurement_inadequate`
- `coordination_budget_exceeded`
- `electronic_reconstruction_detected`
- `target_identity_leakage`
- `did_not_converge_unresolved`

The generic unresolved class is last resort only.

## First implementation slice

Before implementing full dynamics, build a receipt harness that can:

1. validate `receipt.schema.json`;
2. canonicalize deterministic run identity inputs;
3. derive `run_id`;
4. record named seeded PRNG streams;
5. record a deterministic intervention schedule;
6. record and hash a synthetic `G_local` transcript;
7. finalize `receipt_digest`;
8. replay the synthetic fixture and assert exact equality.

Only after this fixture passes should the recurrent field simulator be attached to the receipt producer.
