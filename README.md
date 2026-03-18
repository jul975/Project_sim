# Ecosystem Emergent Behavior Simulator

Deterministic multi-agent ecology simulator for reproducible experiments on a 2D toroidal resource landscape.

As of March 18, 2026, the project is in pre-Stage III / pre-`v0.3` stabilization. The 2D topology transition is complete, the deterministic core is in good shape, and current work is focused on validation alignment, CLI cleanup, spatial metrics, and Stage III interaction design.

## Current Status

- 2D world topology is live across engine state, snapshots, and canonical hashing
- deterministic execution remains a hard constraint
- the experiment lane is usable for batch runs and analysis
- verification coverage is strong
- behavioral validation and parts of the CLI surface are still being normalized

Current posture: a working experimental engine with strong reproducibility guarantees, active refactoring, and a few intentionally documented rough edges before the next stage freeze.

## What Works Today

- deterministic engine core with canonical state hashing
- 2D toroidal world with fertility and resource fields
- isolated RNG ownership across world, movement, reproduction, and energy
- snapshot and restore with continuation-equivalent behavior
- regime compiler pipeline:

```text
RegimeSpec -> compile_regime() -> CompiledRegime -> Runner -> Engine -> SimulationMetrics -> batch analytics
```

- batch experiment orchestration through `Runner`
- per-run and batch-level analytics
- optional plotting and performance profiling

## Current Limits

- validation contracts are still being recalibrated against current behavior
- the `validate` and `fertility` CLI lanes are not yet as cleanly integrated as the main experiment path
- spatial analytics lag behind the 2D engine
- Stage III interaction rules are not implemented yet

## Quickstart

```bash
git clone https://github.com/jul975/Poject_sim.git
cd Poject_sim
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

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running Experiments

Default baseline run:

```bash
python -m engine_build.main experiment --regime stable
```

Custom run:

```bash
python -m engine_build.main experiment --regime stable --seed 42 --runs 5 --ticks 500
```

With plots:

```bash
python -m engine_build.main experiment --regime stable --plot
```

With phase profiling:

```bash
python -m engine_build.main experiment --regime abundant --runs 10 --ticks 1000 --perf-flag
```

Current named regimes:

- `stable`
- `fragile`
- `extinction`
- `collapse`
- `saturated`
- `abundant`

Defaults are defined in `engine_build/execution/default.py`:

- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 300, "runs": 2}`

## Verification And Validation

Recommended verification entry points:

```bash
python -m engine_build.main verify --suite determinism
python -m engine_build.main verify --suite snapshots
python -m engine_build.main verify --suite rng
python -m engine_build.main verify --suite all
```

Direct pytest entry points:

```bash
python -m pytest tests/verification
python -m pytest tests/validation
```

Useful markers from `pytest.ini`:

- `dev`
- `validate`
- `slow`
- `rng`
- `invariant`
- `snapshot`
- `regime`

Note: the verification CLI is the cleaner lane today. The validation CLI surface is still being aligned with the underlying test suite names, so `pytest` is the more reliable way to run validation checks right now.

## Repository Map

- `engine_build/core/` - engine, world, transitions, snapshots, canonical state schema
- `engine_build/regimes/` - regime specs, compiled params, registry, compiler
- `engine_build/runner/` - batch orchestration
- `engine_build/metrics/` - per-tick metrics collection
- `engine_build/analytics/` - fingerprints, summaries, regime classification
- `engine_build/cli/` - parser, requests, dispatch, menu frontend
- `engine_build/visualisation/` - plots and development views
- `tests/verification/` - determinism, invariants, snapshots, RNG isolation
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

- stabilize the validation surface
- finish CLI normalization
- reintroduce 2D-aware spatial metrics
- document Stage III interaction rules before implementation
- freeze a clean pre-Stage III baseline
