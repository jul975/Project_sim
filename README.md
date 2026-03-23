# Ecosystem Emergent Behavior Simulator

Deterministic multi-agent ecology simulator for reproducible experiments on a 2D toroidal resource landscape.

As of March 23, 2026, the repository is at package version `0.3.0a0` and represents the current pre-Stage III / pre-`v0.3` freeze candidate. The 2D engine transition is live, determinism is still a hard constraint, and the main public surface is a small CLI for experiments plus suite-based verification and validation.

## Pre-Stage III Freeze Snapshot

- 2D toroidal world with 2D fertility and resource fields
- deterministic execution with canonical state hashing
- snapshot and restore support with continuation-equivalent behavior
- isolated RNG ownership across world, movement, reproduction, and energy
- phase-structured engine loop: movement -> interaction -> biology -> commit
- batch runner plus per-run and batch-level analytics
- optional plotting, performance profiling, and world-frame capture
- CLI lanes for `experiment`, `verify`, and `validate`
- explicit interactive menu entrypoint via `python -m engine_build.main menu`

Checked on March 23, 2026 in the project `.venv`:

- `tests/verification`: `25 passed`
- `tests/validation`: `6 passed`

## What This Version Is Not Yet

- explicit Stage III crowding, collision, and local-competition rules are not implemented yet
- spatial diagnostics exist, but the current 2D analytics surface is still lighter than the planned Stage III metrics stack
- the CLI is usable but still intentionally small and pre-freeze
- plotting dependencies are imported during CLI startup, so dependencies should be installed before running any CLI command, including `--help`

## Current Regimes

The live regime registry is:

- `stable`
- `fragile`
- `abundant`
- `saturated`
- `collapse`
- `extinction`

Current defaults from `engine_build/execution/default.py`:

- `DEFAULT_MASTER_SEED = 20250302`
- experiment defaults: `runs = 10`, `ticks = 1000`
- experiment tail window default: `--tail-fraction 0.25`

## Quickstart

```bash
git clone https://github.com/jul975/Project_sim.git
cd Project_sim
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux or macOS:

```bash
source .venv/bin/activate
```

Install dependencies before running the CLI:

```bash
python -m pip install -r requirements.txt
```

Python requirement from `pyproject.toml`: `>=3.11`

## Running Experiments

Baseline run:

```bash
python -m engine_build.main experiment --regime stable
```

Custom run:

```bash
python -m engine_build.main experiment --regime stable --seed 42 --runs 5 --ticks 500
```

Batch plots:

```bash
python -m engine_build.main experiment --regime stable --plot
```

Performance profiling:

```bash
python -m engine_build.main experiment --regime abundant --runs 10 --ticks 1000 --perf-flag
```

World-frame capture plus dev plots:

```bash
python -m engine_build.main experiment --regime stable --runs 3 --ticks 200 --world-frame-flag --plot-dev
```

Interactive menu:

```bash
python -m engine_build.main menu
```

## Verification And Validation

Verification suites:

- `all`
- `determinism`
- `invariants`
- `rng`
- `snapshots`

Validation suites:

- `all`
- `contracts`
- `separation`

Run via the project CLI:

```bash
python -m engine_build.main verify --suite all
python -m engine_build.main validate --suite all
```

Direct pytest entry points:

```bash
python -m pytest tests/verification
python -m pytest tests/validation
```

Useful markers from `pytest.ini`:

- `dev`
- `validate`
- `verify`
- `regime`
- `full`
- `slow`
- `rng`
- `invariant`
- `snapshot`

## Repository Map

- `engine_build/core/` - engine, world, transitions, snapshots, canonical state schema
- `engine_build/regimes/` - regime specs, compiled params, registry, compiler
- `engine_build/runner/` - batch orchestration and run lifecycle
- `engine_build/metrics/` - per-tick metrics collection
- `engine_build/analytics/` - fingerprints, summaries, classification, world-frame analytics
- `engine_build/experiments/` - experiment-mode entrypoints and output formatting
- `engine_build/cli/` - parser, requests, dispatch, and menu frontend
- `engine_build/visualisation/` - batch plots, single-run plots, world-view plots
- `tests/verification/` - determinism, invariants, snapshots, RNG isolation, CLI smoke
- `tests/validation/` - regime contracts and regime separation checks
- `docs/canonical_docs/` - architecture and behavior references
- `docs/Project_Status/` - roadmap, current status, performance notes

## Documentation

- [Architecture](docs/canonical_docs/ARCHITECTURE.md)
- [Simulation Pipeline](docs/canonical_docs/SIMULATION_PIPELINE.md)
- [Mathematical Model](docs/canonical_docs/MATHEMATICAL_MODEL.md)
- [Configuration](docs/canonical_docs/CONFIGURATION.md)
- [Determinism](docs/canonical_docs/DETERMINISM.md)
- [RNG Architecture](docs/canonical_docs/RNG_ARCHITECTURE.md)
- [Experiments](docs/canonical_docs/EXPERIMENTS.md)
- [Current State](docs/Project_Status/CURRENT_STATE.md)
- [Roadmap](docs/Project_Status/ROADMAP.md)

## Near-Term Priorities

- keep the current verification and validation surface green while freezing docs and CLI behavior
- expand 2D-aware spatial diagnostics on top of the existing world-frame analytics
- document Stage III interaction rules before implementing them
- freeze a clean pre-Stage III baseline that matches code, tests, and docs
