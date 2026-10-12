# GHoT COMMONS HANDOFF 001 — Physical observation is not permission

**Date:** 2026-10-12
**Status:** Cross-repository incubation; NO LIVE SENSOR OR ACTUATOR CONNECTION
**GHoT companion:** [Commons Machine 001 draft PR #129](https://github.com/the-static-collective/GHoT/pull/129)
**Physical experiment:** [Hollow Copper Relational Field 001](../HOLLOW_COPPER_RELATIONAL_FIELD_001.md)

## Intent

Investigate how one local, attributable physical event can open multiple independently useful candidate actions across a local-first civic/household infrastructure network.

A lever may flush a toilet while a separately isolated sensor might observe supply flow, another node could propose a cooling assessment, and GHoT might offer computation. None of that authorizes routing wastewater into coolant or operating a pump.

## Current software scope

The GHoT branch contributes a synthetic, deterministic, no-network, no-actuation consequence simulator, a one-lever scenario fixture, YES/HOLD/REFUSE model decisions, and optional unsigned receipts tagged no_physical_observations_made=true.

The current GHoT parser REQUIRES source_event.synthetic=true. It cannot ingest real measurements. YES is admissible only as a synthetic model edge, never an execution authorization.

## Future physical observation contract — NOT IMPLEMENTED

A tranchNOSE owner must provide a bounded apparatus identity and geometry, configured stimuli, measured variable with unit and timestamps, calibration and uncertainty, environmental covariates, raw sample digest, observer cut, alternative hypotheses, null, and locally attributable authority.

Only a future explicit validated adapter could form a GHoT commons candidate. GHoT must independently check active offers, power state, liveness, lease policy, and authorization. reLATTE would own any crossing semantics where an owner boundary is crossed.

## Roles

- tranchNOSE: What physically occurred and with what evidence?
- GHoT: Which available computing or sensing capability could act on the observation?
- reLATTE: What was admitted across boundaries, with what receipts?
- Human operator: What physical actuation is allowed, if any?

Uncalibrated or unauthenticated signals, unsafe fluid-quality crossing, unclear authority, and apparatus faults remain HOLD or REFUSE. No automatic valve, pump, transformer, coil, or mains switching.

## Next specimen

Dry CT-001: isolated, current-limited low-voltage copper coil with separated turns, thermal limits, and calibrated response. Then CT-002: two-coil mutual coupling with blind topology checks. Neither requires coolant or actuation.

**Success right now:** An attributable bidirectional architectural seam, plus synthetic GHoT prototype code. Physical interoperability is a later separately testable stage.
