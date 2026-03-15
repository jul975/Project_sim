# Ecosystem Engine Architecture

## 1. Purpose
The Ecosystem Engine is a deterministic multi-agent simulation platform for controlled ecological experiments.

Design goals:
- deterministic execution and replay
- isolated stochastic subsystems
- canonical state representation
- reproducible snapshot and clone behavior
- clear subsystem boundaries for extension

The system is intended for research workflows where repeatability is a first-class requirement.

## 2. High-Level Structure
```text
Engine
+- World
+- Agents (dict[id -> Agent])
+- Energy Model (EnergyParams)
+- RNG Infrastructure (SeedSequence + per-domain generators)
+- State Serialization (Schema v2)
+- Runner/Metrics Layer (outside Engine.step)
```

## 3. Core Subsystems

### 3.1 Engine (`core/engineP4.py`)
Responsibilities:
- owns `master_ss` (root RNG seed sequence)
- derives runtime energy parameters from configured ratios
- creates world and initial population
- executes deterministic tick pipeline
- commits births/deaths with capacity guarantees
- exposes snapshot/restore and canonical hash

Structural invariants enforced in debug mode:
- `0 <= agent.position[0] < world_width` and `0 <= agent.position[1] < world_height` (2D bounds)
- `agent.id == dict key`
- `len(agents) <= max_agent_count`

### 3.2 World (`core/world.py`)
Responsibilities:
- stores 2D fertility and resource fields (2D numpy arrays)
- applies harvest constraints
- regrows resources each tick
- wraps positions on a 2D toroidal topology (height × width grid)
- owns `rng_world`
- generates spatially-correlated fertility landscapes

Resource fields:
- `fertility[y, x]` — maximum sustainable resource level (static, generated at init)
- `resources[y, x]` — current resources (updated each tick)
- `world_width`, `world_height` — grid dimensions
- `world_size` — total cells (width × height)

Resource update per cell:
```text
harvest = min(resources[y, x], max_harvest)
resources[y, x] = min(resources[y, x] + resource_regen_rate, fertility[y, x])
```

Toroidal wrapping (2D):
```text
(x + dx) mod world_width
(y + dy) mod world_height
```

### 3.3 Agent (`core/agent.py`)
Agent state:
- `id`, `position` (now `(x, y)` tuple), `energy_level`, `alive`, `age`
- seed lineage metadata (`entropy`, `spawn_key`, `pool_size`)
- deterministic local spawn counter (`agent_spawn_count`)

Agent initialization (newly refactored into phases):
- `_init_identity()` — ID, entropy, lineage setup
- `_init_lineage()` — RNG seed sequence restoration/creation
- `_init_rngs()` — spawn domain-specific RandomGenerators
- `_init_state()` — energy, position, and lifecycle initialization

Per-agent RNG streams:
- `move_rng` — movement direction and distance
- `repro_rng` — reproduction draw and child survival
- `energy_rng` — initial energy randomization

Lifecycle actions per tick:
- movement cost and directional movement (4-neighbor in 2D grid)
- harvest from current cell
- reproduction eligibility and stochastic reproduction draw
- age progression and max-age death marking

### 3.4 Configuration and Energy Model (`core/config.py`)
Config is immutable (`dataclass(frozen=True)`) and includes:
- population config (`initial_agent_count`, `max_agent_count`, `max_age`)
- world parameters (`world_width`, `world_height`, `max_resource_level`, `resource_regen_rate`)
- reproduction probabilities (`normal` and `change_condition`)
- energy configuration

Derived energy parameters:
```text
movement_cost = int(alpha * max_harvest)
reproduction_threshold = int(gamma * movement_cost)
reproduction_cost = int(beta * reproduction_threshold)
```

### 3.5 Agent Creation and Factory Pattern (`core/agent_factory.py`)

Agent creation is decoupled from engine orchestration via factory functions:

**Initial Population:**
```python
create_initial_agent(engine, agent_id, agent_seed, perf=None)
```
- Called during engine initialization
- Creates agents at random positions in 2D world
- Spawns child RNG lineage from master agent seed

**Newborn Agents:**
```python
create_newborn_agent(engine, agent_id, child_seed, position, perf=None)
```
- Called during reproduction commit
- Places newborn at parent's current position
- Inherits energy and age from parent (in future, traits)

Both paths support optional performance measurement via `PerfSink` for profiling initialization bottlenecks.

### 3.6 Performance Profiling Infrastructure (`dev/perf.py`)

Framework for measuring execution time without embedding timing logic into core algorithms:

**PerfSink Interface:**
```python
class PerfSink:
    def add_time(self, key: str, dt: float) -> None: ...
```

**Measurement Utility:**
```python
measure_block(perf: PerfSink, key: str, fn) -> result
```
- Times function execution
- Records to PerfSink with hierarchical keys (e.g., `"agent.__init__.rngs"`)
- Returns original result (transparent to logic)

**Bottleneck Identification:**
Agent initialization identified as critical path:
- `agent.__init__.identity` — seed/ID setup
- `agent.__init__.lineage` — RNG lineage restoration
- `agent.__init__.rngs` — RandomGenerator spawning
- `agent.__init__.state` — energy/position/age initialization

Performance metrics integrated into batch analytics for regression testing (Stage III+).

## 4. Tick Execution Model

Authoritative step behavior is implemented in `Engine.step()`.

```text
1. Iterate agents in sorted ID order
2. Evaluate transitions (no structural mutation)
3. Compute available capacity from pending deaths
4. Commit deaths
5. Commit births (capacity-limited)
6. Regrow world resources
7. Increment world tick
8. Return tick events (births, deaths, death buckets)
```

Death events are classified into:
- `old_age`
- `metabolic_starvation`
- `post_harvest_starvation`
- `post_reproduction_death`

Important ordering rule:
- death commit occurs before birth commit

## 5. RNG Architecture and Determinism
The engine uses hierarchical `SeedSequence` lineage with `default_rng` (PCG64).

```text
master_ss
+- world_ss -> rng_world
+- agent_ss[i]
   +- move_ss   -> move_rng
   +- repro_ss  -> repro_rng
   +- energy_ss -> energy_rng
```

Determinism contract:
- same `(seed, config, code)` => same state trajectory
- different seeds => divergent trajectories
- reproduction RNG changes must not alter movement RNG trajectories for shared surviving IDs

Child lineage is deterministic via spawn-key extension with `agent_spawn_count`.

## 6. State, Snapshot, and Equivalence
### 6.1 Canonical State Hash
State equivalence is defined by:
```text
sha256(get_state_bytes(engine))
```

### 6.2 Schema v2 (`core/state_schema.py`)
Canonical bytes include:
- schema version and condition flag
- engine fields (`tick`, `agent_count`, `next_agent_id`, `max_age`)
- rule environment parameters
- world fields (`world_size`, resource model arrays, world RNG state)
- agent records sorted by ID
- each agent RNG state and lineage metadata

### 6.3 Snapshot/Restore
`get_snapshot()` persists engine/world/agent state and RNG states.
`Engine.from_snapshot()` reconstructs a running equivalent state, including RNG continuation.

## 7. Orchestration and Metrics Boundary
The runner layer (`runner/regime_runner.py`) handles:
- run-seed generation from a batch master seed
- tick loop execution
- metrics recording per tick
- batch aggregation and regime fingerprints

`Engine.step()` does not collect metrics directly; it returns event data consumed by `SimulationMetrics`.

## 8. Validation Strategy
Primary validation domains (`test/test_determinism.py`):
1. Determinism
2. Structural invariants
3. Dynamics sanity
4. RNG stream isolation
5. Reference hash baseline

This test structure protects reproducibility and regression safety during model evolution.

## 9. Current Scope and Known Limits
Current scope:
- 1D toroidal spatial model
- single agent type
- deterministic seed lineage and canonical serialization
- energy/resource-coupled reproduction and survival

Known limits:
- no trait heterogeneity or strategy layer
- no explicit spatial interaction beyond shared resource competition
- `SeedSequence.n_children_spawned` is not directly restorable; lineage uses engine-level spawn-count emulation

## 10. Related Documents
- `docs/simulation_pipeline.md`: step-order contract
- `docs/RNG_ARCHITECTURE.md`: RNG topology and isolation contract
- `docs/Agent.md`: agent energy and behavioral calibration
