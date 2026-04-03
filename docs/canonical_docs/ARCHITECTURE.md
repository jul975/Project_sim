# Ecosystem Engine Architecture

## Status

This document describes the implementation that is actually checked in on April 3, 2026.

Current baseline:

- Stage III freeze point on `0.3.0a0`
- `v0.2.5` remains the earlier pre-Stage III freeze artifact
- deterministic 2D toroidal ecology simulator
- CLI subcommands and the top-level menu both route into the same execution-context and dispatch layer
- validation currently needs repair before the Stage III freeze line can be called fully green again

## High-Level Structure

```text
CLI args or terminal menu
-> ExecutionContext
-> dispatch()
-> service

Execution lanes:
- experiment
- verification
- validation
- exploration
```

The public entrypoint is `engine_build.main`.

Current command surface:

- `python -m engine_build.main experiment ...`
- `python -m engine_build.main verify ...`
- `python -m engine_build.main validate ...`
- `python -m engine_build.main dynamic ...`
- `python -m engine_build.main menu`

Important nuance:

- the parser subcommands are `experiment`, `verify`, `validate`, and `dynamic`
- `menu` is a top-level shortcut handled directly in `engine_build.main` before `argparse` dispatch
- there is no live `fertility` request or fertility execution lane in the current CLI

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
BatchRunner
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

The typed execution layer currently centers on:

- `ExecutionContext`
- `ExecutionFeatures`
- `ExecutionMode`

`engine_build.main` and `engine_build/app/cli/menu.py` both ultimately build an `ExecutionContext`.

`engine_build/app/cli/dispatch.py` routes that context to:

- `run_experiment()`
- `run_verification()`
- `run_validation()`
- `run_exploration()`

Current reality:

- the experiment lane is still the main operational path
- the verification and validation lanes shell into checked-in pytest suites
- the exploration lane powers the `dynamic` command and runs a single animated batch with world-frame capture enabled
- older docs referring to `run_experiment_mode()`, `run_verification_mode()`, or `run_validation_mode()` are stale against the current tree

## Verified Current State

As of April 3, 2026:

- the 2D topology is live across engine state, hashing, and snapshots
- the execution-context -> dispatch -> service structure is live
- the parser subcommands are `experiment`, `verify`, `validate`, and `dynamic`
- the top-level `menu` shortcut is also live through `engine_build.main`
- under the project `.venv`, `python -m engine_build.main --help` succeeds and shows the expected parser surface

## Known Freeze-Relevant Limits

- the Stage III freeze point does not mean explicit crowding, collision, or richer local-competition rules are fully implemented
- there are no explicit agent-agent mechanics beyond shared-cell harvesting and population-cap competition
- `contrast` and `floor` remain unused in world generation
- the experiment context exposes `tail_fraction`, but `build_and_run_batch()` does not currently pass it into `AnalysisContext`, so experiment analysis still uses the default `0.25`
- validation currently regressed: `engine_build/validation/helpers.py` constructs `AnalysisContext(regime_label=...)` without the `n_runs` and `total_tics` values required by `analyze_batch()`, so `tests/validation` currently fail before the regime-contract assertions run
- snapshot objects store `world_frame_flag`, but `engine_from_snapshot()` currently forces `collect_world_view = False` after reconstruction
- world-frame analytics and dev plotting are useful support tools, not yet the most polished public surface

## Scope Boundary

Implemented and stable enough for the current Stage III freeze baseline:

- deterministic 2D world
- batch experimentation
- canonical hashing
- snapshot continuation model
- CLI, menu, dispatch, and exploration paths
- regime compilation and classification

Not yet implemented or not yet hardened:

- explicit crowding / collision rules
- trait variation and inheritance
- stronger Stage III interaction invariants and diagnostics
- full use of the landscape `contrast` and `floor` controls
- fully wired custom tail-fraction control in experiment analysis
- repaired validation helper wiring for the contract suites
