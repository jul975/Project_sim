# Current Stage - Version `beta0.2`

## Snapshot
**Date:** March 5, 2026  
**Roadmap stage:** Stage II - Controlled Ecological Dynamics  
**Version state:** `beta0.2` baseline

This stage represents a deterministic ecological engine where population dynamics emerge from resource-energy coupling, while reproducibility remains a hard engineering constraint.

## Stage Goal (What `beta0.2` Is)
`beta0.2` is the point where the project has moved beyond a deterministic sandbox into a validated ecological simulation baseline.

Core objective achieved:
- deterministic simulation core + ecological feedback loop + validation pipeline

## Implemented Scope
### Deterministic core
- canonical state hashing (`sha256(get_state_bytes(engine))`)
- deterministic sorted agent iteration
- deterministic commit order (deaths -> births -> regrowth)
- snapshot/restore continuation support
- RNG stream isolation (world, movement, reproduction, energy-init)

### Ecological dynamics
- 1D toroidal world
- fertility and bounded resource regeneration
- movement energy cost and harvest-based recovery
- energy-gated stochastic reproduction
- death paths: metabolic, post-harvest, post-reproduction, old-age
- population cap with capacity-aware birth commits

### Experiment and validation infrastructure
- regime presets: `extinction`, `stable`, `saturated`
- batch runner and per-run metrics collection
- aggregate fingerprint analytics
- regime-specific validation thresholds
- determinism suite with reference baseline hash check

## Verification Evidence (Current)
### Determinism suite
`python -m engine_build.test.test_determinism --mode full`  
Result: **PASS** (all suites, including reference baseline)

Pinned reference hash:
- `4d6b796776b544cf9f2328c7fbe9c50d0e192b0d204c0cc732a413e90bf8e0b6`

### Regime validation
Executed via validation module:
- `extinction`: PASS
- `stable`: PASS
- `saturated`: PASS

## Known Limits in `beta0.2`
- spatial model is 1D only
- no explicit agent-agent interaction layer yet (competition is mostly implicit via shared resources/order)
- no trait heterogeneity, inheritance, or mutation
- SeedSequence child-counter restoration is emulated (engine-level deterministic, but not full NumPy internal continuation)

## Operational Caveat
The CLI entry `python -m engine_build.main --mode validation --regime all` currently depends on importing plotting-related modules through `main.py` startup path. In this environment, that import path can fail before validation dispatch.

Impact:
- validation logic itself is functional
- direct invocation through validation module works and passes

## Readiness Assessment
`beta0.2` is a stable baseline suitable for:
- deterministic experimentation
- controlled regime analysis
- regression testing against a pinned reference state

It is the correct freeze point before Stage III work.

## Next Stage Entry (Roadmap Alignment)
Stage III (`v0.3`) starts from this baseline with focus on:
1. explicit interaction and competition mechanics
2. stronger spatial structure (including optional 2D path)
3. new invariants and validation extensions while preserving determinism
