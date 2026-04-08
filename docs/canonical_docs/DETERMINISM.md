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
sha256(get_state_bytes(engine)) → canonical_hash
```

`Engine.__eq__()` delegates to `get_state_hash()`, defined in [engine_build/core/snapshot/state_schema.py](engine_build/core/snapshot/state_schema.py).

The canonical schema is `SCHEMA_VERSION = 2`. Serialized state includes:

### Flags and Configuration
- `schema_version`
- `perf_flag` (performance instrumentation enabled?)
- `collect_world_view` (world-frame capture enabled?)
- `change_condition` (alternate reproduction probability active?)
- compiled regime parameters: `max_harvest`, `reproduction_probability`, etc.

### Simulation State
- `world.tick`
- `next_agent_id`
- `max_age`

### World
- dimensions: `width`, `height`
- `resource_regen_rate`
- `fertility[:]` array (int32)
- `resources[:]` array (int32)
- `world.rng_world` bit-generator state (PCG64 dict)

### All Agents (sorted by ID)
For each live agent:
  - `id`, `position` (x, y tuple)
  - `energy_level`, `age`, `alive` flag, `offspring_count`
  - `move_rng.bit_generator.state`
  - `repro_rng.bit_generator.state`
  - `energy_rng.bit_generator.state`

### Important Nuances

- **Flags affect hashing**: `perf_flag` and `collect_world_view` are part of the hash, so two runs that differ only in instrumentation flags will have different hashes
- **RNG states included**: Canonical equality is stricter than "same ecological outcome"—it includes RNG state, not just visible population counts
- **Determinism vs. outcome equivalence**: Two seeds will produce different trajectories, but the same seed always produces the same hash

## How Determinism Is Enforced

### Strict Phase Order

`Engine.step()` always executes phases in this order:

```
movement_phase() → interaction_phase() → biology_phase() → commit_phase() → tick += 1
```

No reordering, no conditional skipping. This is enforced in [engine_build/core/engine.py](engine_build/core/engine.py).

### Deterministic Traversal Order

At the core of determinism is **insertion-ordered dictionary traversal**. Python 3.7+ guarantees that `dict` insertion order is preserved.

#### Agent Dictionary Order

The agent dict (`engine.agents`) maintains:
1. **Founders** added in range order: `[0, initial_agent_count)`
2. **Children** appended at end in commit order
3. Dead agents removed (never re-added)
4. Result: **insertion order = genealogical order** (with founders first)

#### Movement Phase: Occupancy Index

```python
# engine_build/core/spatial/occupancy_index.py

@classmethod
def build_from_agents(cls, agents: dict[int, Agent]):
    index = OccupancyIndex()
    for agent in agents.values():  # iteration preserves insertion order
        if agent.alive:
            index.add(agent)
    return index
```

Agents are processed in encounter order (dictionary order), not re-sorted per tick. This is critical for determinism.

Within each cell, local agents are stored in a list in encounter order. Resource distribution remainder is allocated to the first $r$ agents in this list.

### Deterministic Structural Mutation

Commit phase is always:

```
1. Remove all queued deaths (in death_bucket order)
2. Create first N births (limited by remaining capacity)
3. Regrow resources
```

No birth re-ordering, no selective culling by cause. Death buckets track cause but don't affect order.

Births increment `next_agent_id` deterministically and sequentially.

### RNG Isolation

See [RNG_ARCHITECTURE.md](RNG_ARCHITECTURE.md) for details. In brief:

- `world.rng_world`: fertility generation only
- `agent.move_rng`: movement direction sampling
- `agent.repro_rng`: reproduction Bernoulli + child_entropy
- `agent.energy_rng`: initial energy sampling

Stream separation prevents one concern from perturbing another's randomness.

### Snapshot Continuation

Snapshots capture all state necessary for perfect execution continuation:

```
Snapshot contains:
  - regime_config (CompiledRegime)
  - world arrays (resources, fertility)
  - world RNG state (PCG64 bit-generator dict)
  - next_agent_id (counter)
  - for each agent:
    - all state fields
    - all RNG bit-generator states
    - master_ss metadata (entropy, spawn_key, pool_size)
```

Restore reconstructs:

```
engine_from_snapshot(snapshot)
  → rebuild world
  → rebuild agents + their RNGs via reconstruct_rng()
  → restore RNG states from snapshot
  → restart from snapshot tick
```

Result: **Continuation is byte-identical**. Resumed trajectory matches original.

**Snapshot restoration caveat**: NumPy's `SeedSequence` internal spawn counter cannot be preserved. This is acceptable because the runtime does not call `master_ss.spawn()` after initialization.

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

## Boundaries and Limitations

### Determinism Guarantee Scope

$$
\text{same seed} + \text{same regime} + \text{same code} + \text{same runtime}
\implies
\text{byte-identical state hashes}
$$

"Same runtime" means:
- Same Python version
- Same NumPy version
- Same CPU architecture (for floating-point rounding in smoothing kernel)
- Same operating system (for path-dependent floating-point differences, if any)

**Corollary**: Different Python/NumPy versions may produce different hashes even with the same seed.

### What Changed vs. What Stays Stable

**Determinism is maintained across:**
- Code refactors that preserve the phase order and RNG streams
- Regime parameter tuning
- Snapshot saves + restores within the same code version

**Determinism may break across:**
- Python version upgrades (PCG64 or NumPy internals may change)
- NumPy version upgrades
- Architecture changes affecting floating-point rounding

### Known Edges

- `change_condition`: This parameter is part of the runtime state and affects hashing, but is not exposed through the standard CLI (only used in tests)
- `world_frame_flag` in snapshots: Snapshot storage includes `world_frame_flag`, but `engine_from_snapshot()` currently forces `collect_world_view = False` on restore. This is a provisional edge and may change
- RNG restoration does not preserve NumPy's internal `SeedSequence.spawn()` counter, but this is irrelevant because the runtime never calls `spawn()` after initialization

### Canonical Hashing Does Not Replay RegimeSpec

The canonical hash is of the **runtime state**, not the source `RegimeSpec`:

```
RegimeSpec → compile_regime() → CompiledRegime → Engine → get_state_hash()
```

If two functionally identical `RegimeSpec` objects are compiled to the same `CompiledRegime`, all runs produce the same hash, even if the source specs differ.

## Practical Guidance

For deterministic comparisons:

- use explicit seeds
- compile regimes through `compile_regime(get_regime_spec(...))`
- compare canonical hashes rather than only aggregate outcomes
- use the verification CLI or full pytest run as the regression gate
