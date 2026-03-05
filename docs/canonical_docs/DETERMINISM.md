# Determinism Guarantees

## Purpose
This document summarizes the current determinism guarantees, the validation coverage across test modes, and residual uncertainty.

## Determinism Contract
A run is expected to be reproducible for fixed:
- seed
- configuration
- code version
- runtime stack (especially NumPy RNG behavior)

State equivalence is defined by canonical hashing:

```text
sha256(get_state_bytes(engine))
```

## System Guarantees
### 1. Canonical state serialization
- Equality is hash-based (`Engine.__eq__` -> `get_state_hash()`).
- `state_schema.py` serializes deterministic fields in canonical order (agents sorted by ID).

### 2. Deterministic execution order
- Agent loop uses sorted IDs.
- Structural commits are ordered and stable: deaths -> births -> world regrowth.

### 3. RNG isolation
Independent RNG streams are maintained for:
- world randomness
- movement
- reproduction
- energy initialization

This isolates stochastic concerns and prevents cross-stream pollution.

### 4. Snapshot continuation reproducibility
- Snapshot includes agent/world RNG states and lineage metadata.
- `Engine.from_snapshot(...)` reconstructs a continuation-equivalent engine state.

### 5. Seed sensitivity
Different seeds produce different trajectories/hashes under the same config.

## Determinism Test Coverage
Entry point:

```bash
python -m engine_build.test.test_determinism --mode <dev|validate|full|reference>
```

### Suite inventory
- Determinism suite:
  - `test_same_seed_determinism`
  - `test_snapshot_equivalence`
  - `test_seed_sensitivity`
- Structural invariant suite:
  - `test_spatial_invariants`
  - `test_resource_bounds`
  - `test_identity_monotonicity`
- Dynamics sanity suite:
  - `test_population_variability`
  - `test_energy_boundedness`
- RNG isolation suite:
  - `test_movement_rng_isolated_from_reproduction`
- Reference baseline suite:
  - `test_reference_hash`

### Mode behavior
| Mode | Included checks | Purpose |
|---|---|---|
| `dev` | Determinism + Structural invariants | Fast core checks during development |
| `validate` | `dev` + Dynamics sanity + RNG isolation | Broader reproducibility and behavior checks |
| `full` | `validate` + Reference baseline hash | Drift detection against pinned baseline |
| `reference` | Prints current baseline candidate hash | Baseline refresh workflow support |

## Current Verified Status (March 5, 2026)
Latest run results:
- `dev`: PASS
- `validate`: PASS
- `full`: PASS

Pinned reference hash in `test_reference_hash`:
- `4d6b796776b544cf9f2328c7fbe9c50d0e192b0d204c0cc732a413e90bf8e0b6`

Interpretation:
- Relative determinism guarantees are validated.
- Baseline hash lock is currently consistent with implementation.

## Risk Assessment
### Medium risk
- Environment drift: NumPy/CPython/version differences can change RNG behavior or serialized values, breaking cross-environment hash comparability.
- Baseline governance risk: updating reference hashes without strict review can hide unintentional behavioral drift.

### Low-to-medium risk
- Seed lineage reconstruction is deterministic for this engine path but relies on an emulation pattern (`spawn_key + spawn_count`) because NumPy does not expose full `SeedSequence` child counter restoration.

### Low risk
- Ordering nondeterminism is currently well controlled by sorted iteration and explicit commit ordering.
- Snapshot continuation risk is currently mitigated by dedicated equivalence tests.

## Practical Conclusion
Current determinism guarantees are strong for same-code, same-environment reproducibility and for regression detection through the full-mode baseline hash. Remaining uncertainty is primarily operational: environment pinning and disciplined baseline management.
