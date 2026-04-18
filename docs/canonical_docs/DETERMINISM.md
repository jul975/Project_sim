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

`Engine.__eq__()` delegates to `get_state_hash()`, defined in [FestinaLente/core/snapshot/state_schema.py](FestinaLente/core/snapshot/state_schema.py).

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

No reordering, no conditional skipping. This is enforced in [FestinaLente/core/engine.py](FestinaLente/core/engine.py).

### World / OccupancyIndex / TransitionContext Contract: State Freezing

The simulator uses the **State Freezing** pattern to separate phase evaluation from state mutation. This is essential for both determinism and testability.

#### Contract Definition

**Three-layer separation:**

1. **World** (`FestinaLente/core/domains/world.py`)
   - Owns: spatial grid dimensions, resource arrays, fertility arrays, world RNG
   - Provides: read-only access to resource/fertility state, harvest distribution logic
   - Invariant: resources always ≤ fertility, both arrays are int32

2. **OccupancyIndex** (`FestinaLente/core/spatial/occupancy_index.py`)
   - Owns: spatial lookup structure mapping (x, y) → ordered list of agents
   - Scope: **read-only** during phases; **rebuilt at start of each tick** (movement phase)
   - Construction: iterates `agents.dict.values()` to preserve encounter order
   - Invariant: agent order within each cell is genealogical (insertion order)

3. **TransitionContext** (`FestinaLente/core/transitions/transitions.py`)
   - Owns: intermediate computation state **only during a single step**
   - Fields:
     - `occupancy`: OccupancyIndex (frozen after movement phase, used for rest of step)
     - `pending_deaths_by_cause`: buckets of agent IDs queued for removal
     - `post_harvest_alive`: agents surviving harvest check
     - `reproducing_agents`: agents queued for birth
   - Invariant: cleared at end of each tick, never persisted
   - Scope: **local to one tick**, not accessible outside step logic

#### Why This Separation Matters

- **Phase isolation**: Each phase computes outcomes independently without cascading mutations
- **Death tracking**: Deaths are categorized by cause (age, metabolic, starvation, reproduction) before commit
- **Deterministic ordering**: Commit order is fixed regardless of phase outcomes
  1. Apply all deaths (in bucket order)
  2. Create births (in queue order, limited by capacity)
  3. Regrow resources
  4. Increment tick
- **Observability**: Full audit trail of what happened and why

#### The Occupancy Freeze Point

At the **start of the interaction phase**, the `OccupancyIndex` is frozen:

```python
# Movement phase
current_occupancy = OccupancyIndex.build_from_agents(agents)  # built here
for position, local_agents in occupied_cells:
    for agent in local_agents:
        agent.move_agent(...)
        context.occupancy.add(agent)  # updated in-place as agents move

# Interaction + Biology phases use context.occupancy (that's what was built + updated during movement)
# No new movement occurs; occupancy index is stable
```

Once the interaction phase begins, **no agent positions change**. The frozen occupancy index is reused for:
- Harvest distribution (all agents on a cell get processed together)
- Neighborhood lookups
- Spatial interaction logic

This freeze is critical: it ensures harvest order is deterministic and matches encounter order.

#### Snapshot Implications

When snapshotting, the `OccupancyIndex` **is not serialized** because it is reconstructed at engine startup:

```python
# From snapshot
agents = { agent.id: agent for agent in snapshot.agents }
occupancy_at_restore = OccupancyIndex.build_from_agents(agents)
# Result: same encounter order, same occupancy structure
```

### Explicit Local Ordering Guarantee

Determinism relies on **three independent local ordering guarantees**, each documented below.

#### 1. Agent Dictionary Order (Global)

The `engine.agents` dict (`dict[int, Agent]`) maintains insertion order:

```python
# Founders added during Engine.__init__
agents[0], agents[1], ..., agents[initial_count-1]  # insertion order preserved

# Children added during each commit_phase, in birth queue order
agents[initial_count], agents[initial_count+1], ...  # appended to end

# Dead agents removed (never re-added)
# Result: no memory reuse, no ID reuse, no out-of-order births
```

**Guarantee**: Agent ID `i` is always processed before ID `j` if `i < j` (with rare exception for founders added out of sequence, which is not the current case).

**Why it matters**: When `OccupancyIndex.build_from_agents(agents)` iterates `agents.values()`, the iteration order is genealogical. This ensures:
- Ancestors processed before descendants
- Harvest remainder allocation is deterministic (first `r` agents in encounter order)
- Resource distribution differs predictably between seeds

**Python version**: Guaranteed by Python 3.7+ dict semantics. See [PEP 468](https://www.python.org/dev/peps/pep-0468/).

#### 2. Local Cell Order (Occupancy Index)

Within each cell, agents are stored in a list (not a set) in encounter order:

```python
# OccupancyIndex.add(agent)
self.cells[agent.position].append(agent)  # list preserves order

# During harvest
for position, local_agents in occupied_index.occupied_items():
    for agent in local_agents:  # iteration is encounter order
        # distribute harvest remainder to first r agents
```

**Guarantee**: Within a cell, agents are processed in the order they arrived during movement.

**Why it matters**:
- First `r` agents in harvest remainder always get the `+1` share
- This gives small but measurable advantage to agents that moved first
- Determinism requires this partial ordering to be stable

**Note**: The first agent to move to a cell is not globally first; it's the first to move to that specific cell in this tick's movement phase.

#### 3. Cell Iteration Order (Dict Insertion Order)

When iterating occupied cells (`occupancy.occupied_items()`), cells are processed in the order they were first populated:

```python
# Movement phase: agents move to cells in encounter order
agent 0 → cell (5, 3)    # cell (5, 3) created first in cells dict
agent 1 → cell (5, 3)    # same cell, not re-inserted
agent 2 → cell (1, 7)    # cell (1, 7) created second in cells dict
...

# Interaction phase: cells are iterated in creation order
for position, agents in index.cells.items():  # (5, 3) before (1, 7)
```

**Guarantee**: Cells are processed in order of first occupancy during movement.

**Why it matters**: This ensures deterministic per-cell processing order in harvest, interaction, etc., even though agents may be distributed unevenly across cells.

#### Consequences for Code Changes

If you modify ordering anywhere in this chain, determinism breaks:

| Component | Change | Impact |
|-----------|--------|--------|
| Agent dict insertion order | Re-sort agents per tick | Harvest remainder order changes; hashes differ |
| Agent dict insertion order | Reuse dead agent IDs | Genealogical order broken; RNG streams collide |
| Local cell list order | Use set instead of list | Cell iteration order randomized; outcomes change |
| Cell dict iteration order | Sort cells per tick | Cell processing order changes; harvest changes |

#### Verification

The following tests verify this contract:

- `tests/verification/test_determinism.py`: Same-seed trajectories remain identical
- `tests/verification/test_invariants.py`: Agent count, resource bounds, occupancy consistency
- `tests/verification/test_rng_isolation.py`: RNG streams are isolated, not perturbed by ordering changes
- Manual snapshot tests: Restore produces byte-identical trajectory

### Deterministic Traversal Order

At the core of determinism is **insertion-ordered dictionary traversal**, which is guaranteed by Python 3.7+.

**Key insight**: We do not re-sort agents or cells on every tick. Instead, we rely on the ordering established during the previous mutation (births, deaths, movement). This avoids per-tick computational overhead while maintaining determinism.

See **Explicit Local Ordering Guarantee** (above) for the formal three-layer contract and consequences of violating it.

The agent dict maintains encounter order across:
- Initial founders (added in range order)
- Children (appended at end per commit)
- Removals (never re-inserted)

When `OccupancyIndex.build_from_agents(agents)` iterates `agents.values()`, the encounter order is preserved, ensuring harvest distributions are deterministic.

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
python -m FestinaLente.main verify --suite <all|determinism|invariants|rng|snapshots>
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
