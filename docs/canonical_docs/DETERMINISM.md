# Determinism

## Purpose

This document defines the determinism contract implemented by the current engine.

## Contract

For a fixed:

- run seed or batch seed
- compiled regime
- execution flags that affect runtime state (`change_condition`, `perf_flag`)
- code version
- Python and NumPy runtime

the engine is expected to produce the same canonical state trajectory and the same snapshot continuation behavior.

The codebase also expects different seeds to diverge under the same regime.

## Canonical Equality

Engine equality is hash-based:

```text
sha256(get_state_bytes(engine))
```

`Engine.__eq__()` delegates to `get_state_hash()`.

The current canonical schema is `SCHEMA_VERSION = 2` in `engine_build/core/state_schema.py`. It includes:

- engine tick and structural counters
- execution flags and rule-environment values
- world dimensions, fertility, resources, and world RNG state
- all agents sorted by ID for serialization
- each agent's position, energy, age, alive flag, offspring count, and RNG states

Important: canonical equality is stricter than "same ecological outcome". It includes runtime flags and RNG state, not just visible world state.

## How Determinism Is Enforced

### Stable step pipeline

`Engine.step()` always executes the same phase order:

```text
movement -> interaction -> biology -> commit -> tick += 1
```

### Deterministic structural mutation

`commit_phase()` always applies:

```text
deaths -> births -> world resource regrowth
```

Births are capacity-limited after queued deaths are counted, and agent IDs are allocated monotonically through `next_agent_id`.

### Stable traversal semantics

The live simulation does not sort agents every tick. Runtime traversal currently depends on:

- Python's stable dictionary insertion order
- deterministic append order inside each phase
- deterministic encounter order for local harvest sharing

Canonical hashing then sorts agents by ID so that equality checks do not depend on dictionary layout.

### RNG isolation

Randomness is partitioned across independent domains:

- `world.rng_world`
- `agent.move_rng`
- `agent.repro_rng`
- `agent.energy_rng`

This prevents movement, reproduction, and initialization draws from polluting each other.

### Snapshot continuation

`Engine.get_snapshot()` and `Engine.from_snapshot()` preserve:

- compiled regime data
- structural counters
- world arrays
- world and agent RNG bit-generator state
- master seed metadata needed by the current runtime path

Continuation equivalence is tested directly in the verification suite.

## Verification Coverage

The current CLI entry point for determinism-oriented checks is:

```bash
python -m engine_build.main verify --suite <determinism|rng|snapshots|invariants|all>
```

Primary checked-in tests:

- `tests/verification/test_determinism.py`
  - `test_same_seed_determinism`
  - `test_snapshot_equivalence`
  - `test_seed_sensitivity`
- `tests/verification/test_rng_isolation.py`
  - `test_movement_rng_isolated_from_reproduction`
- `tests/verification/test_snapshots.py`
  - round-trip, world restore, agent restore, RNG restore, and continuation checks
- `tests/verification/test_invariants.py`
  - spatial bounds, resource bounds, and monotonic ID allocation

## Current Limits

- Reproducibility is a same-code, same-runtime guarantee. Changes in Python, NumPy, or PCG64 behavior can change hashes.
- Snapshot restoration rebuilds `master_ss` from `entropy`, `spawn_key`, and `pool_size`, but it does not restore NumPy's internal child counter. This is acceptable for the current engine because post-initialization logic no longer depends on repeated `master_ss.spawn()` calls.
- The canonical hash captures runtime state, not the original `RegimeSpec` source text.

## Practical Guidance

For deterministic runs:

- use explicit seeds
- compile regimes through `compile_regime(get_regime_spec(...))`
- compare canonical hashes when testing equivalence
- use the verification CLI as the authoritative regression check
