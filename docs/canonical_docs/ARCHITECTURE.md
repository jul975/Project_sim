# Ecosystem Engine Architecture

## Purpose

The Ecosystem Engine is a deterministic multi-agent simulation platform for controlled ecological experiments.

The architecture is optimized for:

- deterministic replay,
- explicit subsystem boundaries,
- snapshot/restore continuation,
- reproducible batch experimentation,
- and staged extension toward richer spatial interactions.

This document describes the **current implementation**, not a future target design.

## High-Level Structure

```text
CLI args / menu
-> typed request objects
-> dispatcher
-> execution lane

Execution lanes:
- experiment
- verification
- validation
- fertility/dev plotting

Experiment lane:
regime spec
-> compile_regime()
-> Runner
-> Engine
-> SimulationMetrics
-> batch analytics
-> summary / classification / reporting
```

## Runtime Core

### Regime compilation

Configuration is not owned by a legacy `core/config.py` layer.

The current path is:

```text
engine_build/regimes/spec.py
-> engine_build/regimes/registry.py
-> engine_build/regimes/compiler.py
-> CompiledRegime
-> Engine / World / Agent
```

The compiler converts anchors and ecological ratios into runtime parameters such as:

- `max_harvest`
- `movement_cost`
- `reproduction_threshold`
- `reproduction_cost`
- `regen_rate`
- `world_width`
- `world_height`

### Engine (`core/engineP4.py`)

`Engine` owns:

- the root `SeedSequence` (`master_ss`)
- compiled regime parameters
- the `World`
- live agents as `dict[id -> Agent]`
- the deterministic tick pipeline
- birth/death commit logic
- canonical hash generation
- snapshot/restore entry points

Important engine state:

- `next_agent_id`
- `max_agent_count`
- `max_age`
- `reproduction_probability`
- `perf_flag`
- `collect_world_view`

The engine currently creates newborns by deriving compact deterministic identity words, not by storing older seed-lineage scaffolding directly on each agent.

### World (`core/world.py`)

`World` is a 2D toroidal grid.

It owns:

- `fertility[y, x]`
- `resources[y, x]`
- `world_width`
- `world_height`
- `world_size`
- `rng_world`
- `resource_regen_rate`
- `max_harvest`

Current responsibilities:

- generate a spatially smoothed fertility field at initialization,
- harvest resources from occupied cells,
- regrow resources in place each tick,
- wrap positions on a 2D torus.

Current topology:

```text
(x + dx) mod world_width
(y + dy) mod world_height
```

### Agent (`core/agent.py`)

Current agent state is intentionally compact.

Each agent owns:

- `id`
- `engine`
- `position`
- `energy_level`
- `alive`
- `age`
- `offspring_count`
- `move_rng`
- `repro_rng`
- `energy_rng`

Current initialization is split into:

- `_init_identity()`
- `_init_rngs()`
- `_init_state()`

The current deterministic identity model works through `AgentSetup.identity_words`.

Three domain-specific RNGs are derived from those identity words using domain tags:

- movement
- reproduction
- energy

Current lifecycle actions:

- movement with energy cost
- resource harvest
- reproduction gate and stochastic reproduction
- aging and age death

### Transition context (`core/transitions.py`)

The step pipeline is mediated through `TransitionContext`, which holds per-tick transition state:

- `occupied_positions`
- `post_harvest_alive`
- `pending_deaths_by_cause`
- `reproducing_agents`

This allows the engine to evaluate transitions first and commit structural mutation afterward.

### Runner and metrics (`runner/regime_runner.py`)

`Runner` owns orchestration, not ecological logic.

Responsibilities:

- batch-seed spawning from a master seed
- per-run engine construction
- tick-loop execution
- metrics recording through `SimulationMetrics`
- optional phase profiling aggregation

The runner returns:

- `RunArtifacts`
- `BatchRunResults`

This keeps `Engine.step()` free of analytics policy.

## Tick Pipeline

The current authoritative step order is:

```text
1. movement_phase()
2. interaction_phase()
3. biology_phase()
4. commit_phase()
5. world.tick += 1
```

### 1. Movement phase

For each agent in dictionary iteration order:

- reject already-dead agents into the age-death bucket
- apply movement cost
- sample a 4-neighbor movement direction
- update and wrap position
- mark metabolic death if energy falls to zero or below
- register surviving agents into `occupied_positions`

Outputs:

- age deaths
- metabolic deaths
- occupancy map for interaction

### 2. Interaction phase

For each occupied cell:

- harvest resources from the world
- distribute harvest deterministically across local agents
- separate post-harvest survivors from starvation deaths

Outputs:

- post-harvest starvation deaths
- `post_harvest_alive`

### 3. Biology phase

For each post-harvest survivor:

- test reproduction threshold
- draw reproduction event
- enqueue reproducing agents
- mark post-reproduction death when energy is exhausted
- otherwise age the agent

Outputs:

- reproducing agents
- post-reproduction death bucket

### 4. Commit phase

The engine then:

- totals pending deaths
- computes effective population after queued deaths
- limits births by remaining capacity
- deletes dead agents
- creates newborn agents
- regrows world resources

Important current rule:

- deaths commit before births

This preserves hard population-cap enforcement without undershoot.

## Determinism Model

Determinism is a core architectural constraint.

The current contract is:

- same seed + same config + same code -> same state trajectory
- different seeds -> diverging trajectories
- RNG domains are isolated by subsystem ownership
- snapshots restore continuation-equivalent state

### RNG ownership

Current RNG ownership is:

- engine root seed sequence: `master_ss`
- world RNG: `rng_world`
- per-agent RNGs:
  - `move_rng`
  - `repro_rng`
  - `energy_rng`

Child identity is derived from:

- run entropy
- child entropy produced by parent reproduction RNG
- parent ID
- parent offspring count

This is the current replacement for the older heavier seed-lineage-per-agent approach.

## State, Snapshot, and Equivalence

### Canonical state hash

Canonical equivalence is defined as:

```text
sha256(get_state_bytes(engine))
```

The schema is currently `SCHEMA_VERSION = 2`.

### State schema (`core/state_schema.py`)

The canonical byte representation includes:

- schema version
- change-condition flag
- engine tick and structural counters
- rule environment parameters
- world dimensions and resource model
- world RNG state
- fertility and resource arrays
- agents sorted by ID
- per-agent:
  - ID
  - 2D position
  - energy
  - age
  - alive flag
  - offspring count
  - movement RNG state
  - reproduction RNG state
  - energy RNG state

### Snapshot layer (`core/snapshots.py`)

Snapshots persist the live runtime state needed for continuation:

- engine shell state
- compiled config
- world arrays and RNG state
- per-agent runtime state and RNG states

`Engine.from_snapshot()` reconstructs a running engine and validates reconstruction in debug mode by rebuilding and comparing snapshots.

## Observability and Performance

The engine supports an explicit profiling mode.

When `perf_flag` is enabled:

- `Engine._step_profiled()` records phase timing for:
  - movement
  - interaction
  - biology
  - commit
- `Engine._commit_profiled()` records commit subphase timing for:
  - setup
  - deaths
  - births
  - resource regrowth

The runner aggregates those into `PhaseProfile`, and batch analytics/reporting can summarize them for experiment output.

Current performance reality:

- births remain the dominant hotspot in high-growth regimes
- movement is the next visible hotspot
- movement currently scales roughly linearly with agent count

## Frontend and Execution Surface

### Main entrypoint (`main.py`)

`engine_build.main` currently selects between:

- menu mode
- parser-driven CLI mode

Then it dispatches typed request objects into execution lanes.

### Request/dispatch model

The current CLI design centers on typed request objects:

- `ExperimentRequest`
- `VerificationRequest`
- `ValidationRequest`
- `FertilityRequest`

`dispatch.py` routes them to:

- `run_experiment_mode()`
- `run_verification_mode()`
- `run_validation_mode()`
- fertility/dev plotting workflow

### Verification vs validation

The codebase now distinguishes:

- **verification**
  - determinism, invariants, RNG isolation, snapshots, regime separation
- **validation**
  - behavioral / contract-style regime checks

This is the right conceptual split, even though the validation lane is still being aligned.

## Current Boundaries and Known Drift

The architecture is stronger than earlier in March, but some boundaries are still being normalized.

### Stable current boundaries

- 2D toroidal world model
- deterministic engine core
- snapshot/restore pipeline
- request -> dispatch -> execution-lane pattern
- separate verification and validation concepts

### Known drift / incomplete areas

- `run_validation.py` still expects older suite names than the current validation request/parser layer exposes
- the fertility/dev plotting lane is still provisional and does not fully consume the `FertilityRequest`
- spatial analytics are behind the 2D engine
- explicit agent-agent interaction rules are not yet implemented
- landscape `contrast` and `floor` exist in the regime interface but are not yet used in fertility generation

## Current Scope

Implemented:

- 2D toroidal space
- resource-coupled survival and reproduction
- deterministic batch experimentation
- canonical state hashing
- snapshot continuation
- phase profiling
- verification/validation folder split
- request-based CLI architecture

Not yet implemented:

- explicit crowding / collision / local competition rules
- trait heterogeneity and inheritance
- mature spatial fingerprint metrics
- fully stabilized public CLI surface

## Related Documents

- `docs/canonical_docs/CONFIGURATION.md`
- `docs/canonical_docs/DETERMINISM.md`
- `docs/canonical_docs/EXPERIMENTS.md`
- `docs/canonical_docs/MATHEMATICAL_MODEL.md`
- `docs/canonical_docs/RNG_ARCHITECTURE.md`
- `docs/canonical_docs/SIMULATION_PIPELINE.md`
