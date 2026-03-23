# Determinism

## Contract

On March 23, 2026, the engine's determinism contract is:

For fixed:

- run seed or batch seed
- compiled regime
- runtime flags and conditions that affect state
- code version
- Python and NumPy runtime

the simulator is expected to produce:

- the same canonical state trajectory
- the same snapshot continuation behavior

Different seeds are expected to diverge.

## Canonical Equality

Engine equality is hash-based:

```text
sha256(get_state_bytes(engine))
```

`Engine.__eq__()` delegates to `get_state_hash()`.

The canonical schema is `SCHEMA_VERSION = 2` in `engine_build/core/state_schema.py`.

Current serialized state includes:

- schema version
- `change_condition`
- `world.tick`
- current agent count
- `next_agent_id`
- `max_age`
- `perf_flag`
- `collect_world_view`
- compiled rule-environment values used by the runtime
- world dimensions
- `max_harvest`
- `resource_regen_rate`
- resource array
- fertility array
- world RNG state
- every agent sorted by ID, including:
  - `id`
  - 2D position
  - energy
  - age
  - alive flag
  - offspring count
  - move RNG state
  - repro RNG state
  - energy RNG state

Important nuance:

- canonical equality is stricter than "same ecological outcome"
- it includes runtime flags and RNG state, not just visible population behavior

## How Determinism Is Enforced

### Stable phase order

`Engine.step()` always executes:

```text
movement -> interaction -> biology -> commit -> tick += 1
```

### Deterministic structural mutation

`commit_phase()` always applies:

```text
queued deaths -> committed births -> world regrowth
```

Births are sliced by remaining capacity before any newborn is materialized.

### Stable traversal semantics

The hot path does not sort agents each tick.

Current runtime stability comes from:

- Python's insertion-ordered dictionaries
- deterministic mutation order
- deterministic append order inside occupancy buckets

Canonical serialization then sorts agents by ID before hashing.

### RNG isolation

Randomness is partitioned into separate streams:

- `world.rng_world`
- `agent.move_rng`
- `agent.repro_rng`
- `agent.energy_rng`

This prevents movement, reproduction, world generation, and initial energy draws from perturbing each other.

### Monotonic identity allocation

`next_agent_id` only increments and committed births are the only place new IDs are allocated.

### Snapshot continuation

Snapshots preserve the runtime state needed for continuation:

- compiled config
- world arrays
- world RNG state
- per-agent RNG states
- structural counters
- enough `SeedSequence` metadata to reconstruct `master_ss`

## Verification Coverage

Current verification CLI:

```bash
python -m engine_build.main verify --suite <all|determinism|invariants|rng|snapshots>
```

Primary checked-in tests:

- `tests/verification/test_determinism.py`
  - same-seed determinism
  - snapshot equivalence
  - seed sensitivity
- `tests/verification/test_rng_isolation.py`
  - movement RNG remains stable when reproduction policy changes
- `tests/verification/test_snapshots.py`
  - snapshot shape
  - config roundtrip
  - world restore
  - agent restore
  - RNG restore
  - continuation after restore
- `tests/verification/test_invariants.py`
  - spatial bounds
  - resource bounds
  - monotonic ID allocation

The full repository test run passed on March 23, 2026 in the project virtual environment.

## Current Limits

- Reproducibility is a same-code, same-runtime guarantee. Python, NumPy, or PCG64 changes may change hashes.
- Snapshot restoration reconstructs `master_ss` from metadata and does not preserve NumPy's internal child counter. This is acceptable in the current engine because the runtime no longer depends on repeated `master_ss.spawn()` calls after world initialization.
- `change_condition` is part of the runtime model and the canonical hash, but it is not exposed through the current user-facing CLI.
- Snapshot objects store `world_frame_flag`, but `engine_from_snapshot()` currently forces `collect_world_view = False` after reconstruction. That is a real implementation quirk and should be treated as a provisional edge of the snapshot surface.
- Canonical hashing captures runtime state, not the original `RegimeSpec` source text.

## Practical Guidance

For deterministic comparisons:

- use explicit seeds
- compile regimes through `compile_regime(get_regime_spec(...))`
- compare canonical hashes rather than only aggregate outcomes
- use the verification CLI or full pytest run as the regression gate
