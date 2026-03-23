# Ecosystem Engine Architecture

## Status

This document describes the implementation that is actually checked in on March 23, 2026.

Current baseline:

- pre-Stage III / pre-`v0.3` freeze candidate
- package version `0.3.0a0`
- deterministic 2D toroidal ecology simulator
- CLI and menu both route into the same typed request and dispatch layer
- full local test run in the project virtual environment passed on March 23, 2026: `31 passed`

## High-Level Structure

```text
CLI args or terminal menu
-> typed request objects
-> dispatcher
-> execution lane

Execution lanes:
- experiment
- verification
- validation
```

The public entrypoint is `engine_build.main`.

Current command surface:

- `python -m engine_build.main experiment ...`
- `python -m engine_build.main verify ...`
- `python -m engine_build.main validate ...`
- `python -m engine_build.main menu`

There is no live `fertility` request or fertility execution lane in the current CLI.

## Runtime Core

### Regime compilation

Configuration is authored in `engine_build/regimes/spec.py`, registered in `engine_build/regimes/registry.py`, and compiled in `engine_build/regimes/compiler.py`.

Authoritative path:

```text
RegimeSpec
-> compile_regime()
-> CompiledRegime
-> Engine / World / Agent / Runner
```

The named regime registry currently exposes:

- `stable`
- `fragile`
- `abundant`
- `saturated`
- `collapse`
- `extinction`

### Engine

`engine_build/core/engine.py` owns:

- the run-level `SeedSequence` (`master_ss`)
- one spawned world seed for `World`
- the compiled regime
- the live `World`
- the live `agents: dict[int, Agent]`
- `next_agent_id`
- `max_agent_count`
- `max_age`
- the effective `reproduction_probability`
- instrumentation flags:
  - `perf_flag`
  - `collect_world_view`

Important current behavior:

- founders are created immediately at engine construction
- newborns are created only during commit
- deaths commit before births
- `Engine.step()` chooses a fast path or an instrumented path depending on flags

### World

`engine_build/core/world.py` implements a 2D toroidal grid with:

- `fertility[y, x]`
- `resources[y, x]`
- `world_width`
- `world_height`
- `world_size`
- `rng_world`
- `resource_regen_rate`
- `max_harvest`

Current responsibilities:

- generate the fertility landscape once at initialization
- keep resources bounded by fertility
- harvest resources deterministically for all agents on a cell
- regrow resources in place after commit
- wrap positions on a torus

Landscape generation currently uses a smoothed random field derived from `landscape_params.correlation`.

Current limitation:

- `contrast` and `floor` are carried through the regime model but are not yet applied inside fertility generation

### Agent

`engine_build/core/agent.py` keeps the runtime agent intentionally small.

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

Identity is no longer a stored `SeedSequence` lineage tree. The current engine derives RNGs from compact deterministic `identity_words`.

### Transition layer

`engine_build/core/transitions.py` separates evaluation from structural mutation.

`TransitionContext` holds:

- `occupied_positions`
- `post_harvest_alive`
- `pending_deaths_by_cause`
- `reproducing_agents`

Current death buckets:

- `age_deaths`
- `metabolic_deaths`
- `post_harvest_starvation`
- `post_reproduction_death`

### Runner and analytics

`engine_build/runner/regime_runner.py` owns orchestration, not ecological logic.

Responsibilities:

- derive per-run `SeedSequence` objects from a batch seed
- build engines
- run tick loops
- record `SimulationMetrics`
- optionally aggregate profiling data

The experiment lane then analyzes those runs through:

```text
Runner
-> BatchRunResults
-> analyze_batch()
-> summarise_regime()
-> classify_regime()
-> report / optional plots
```

## Tick Pipeline

The authoritative runtime order is:

```text
movement
-> interaction
-> biology
-> commit
-> world.tick += 1
```

The details are documented in `docs/canonical_docs/SIMULATION_PIPELINE.md`.

## Determinism Model

Determinism is still a hard project constraint.

The live code enforces:

- fixed phase order
- stable Python dictionary encounter order in the runtime loop
- separate RNG streams for world, movement, reproduction, and initial energy
- canonical state hashing through `engine_build/core/state_schema.py`
- snapshot/restore continuation through `engine_build/core/snapshots.py`

Important nuance:

- runtime traversal is not sorted every tick
- canonical hashing sorts agents by ID for serialization
- world-view packaging also sorts by ID before exporting arrays

## Observability

### Profiling

When `perf_flag=True`, `Engine.step()` records:

- movement time
- interaction time
- biology time
- commit time

Commit profiling is split into:

- setup
- deaths
- births
- resource regrowth

### World frames

When `world_frame_flag=True`, `Engine.step()` builds a `WorldView` sample every 10 ticks.

The sampled frame contains:

- sorted agent positions
- sorted agent energies
- a copy of the resource grid

This feeds the optional world-frame analytics path. It is useful, but still secondary to the core experiment lane.

## CLI and Execution Surface

The typed request layer currently consists of:

- `ExperimentRequest`
- `VerificationRequest`
- `ValidationRequest`

`engine_build/cli/dispatch.py` routes them to:

- `run_experiment_mode()`
- `run_verification_mode()`
- `run_validation_mode()`

Current reality:

- the experiment lane is the main operational path
- the verification and validation lanes shell into checked-in pytest suites
- the old fertility/dev-lane documentation is stale against the current tree

## Verified Current State

As of March 23, 2026:

- the 2D topology is live across engine state, hashing, and snapshots
- the request -> dispatch -> execution-lane structure is live
- verification and validation are both wired through the CLI
- the full local pytest run passed in the project virtual environment

## Known Freeze-Relevant Limits

- Stage III interaction rules are not implemented yet
- there are no explicit agent-agent mechanics beyond shared-cell harvesting and population-cap competition
- `contrast` and `floor` remain unused in world generation
- the experiment request exposes `tail_fraction`, but `run_experiment_mode()` currently does not forward it into `AnalysisConfig`, so experiment analysis still uses the default `0.25`
- snapshot objects store `world_frame_flag`, but `engine_from_snapshot()` currently forces `collect_world_view = False` after reconstruction
- world-frame analytics and dev plotting are useful support tools, not yet the most polished public surface

## Scope Boundary

Implemented and stable enough for a pre-Stage III baseline:

- deterministic 2D world
- batch experimentation
- canonical hashing
- snapshot continuation
- pytest-backed verification and validation lanes
- regime compilation and classification

Not yet implemented or not yet frozen:

- explicit crowding / collision rules
- trait variation and inheritance
- mature Stage III interaction semantics
- full use of the landscape `contrast` and `floor` controls
- fully wired custom tail-fraction control in the experiment CLI
