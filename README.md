# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent ecology simulator for running reproducible experiments on a wrapped 2D resource landscape. The project evolves from a foundational deterministic kernel toward a research-grade experimentation platform with explicit interactions, trait heterogeneity, and advanced analytics.

$$S_{t+1} = T(S_t)$$

## Project Status

**Current Stage:** Stage II (beta v0.2) — Controlled Ecological Dynamics  
**Target Version:** v0.3 (Stage III) — Explicit Interaction and Spatial Competition

See [ROADMAP](docs/Project_Status/ROADMAP.md) for strategic goals, staged milestones, and version targets.

## Overview

The project is structured around a clear execution pipeline:

`regime spec → regime compiler → runner → engine → metrics → batch analytics`

**Package Layout:**

- `engine_build/regimes/` — Human-authored regime presets and compilation to runtime parameters
- `engine_build/runner/` — Batch orchestration and seed spawning
- `engine_build/core/` — Deterministic simulation state and tick transitions
- `engine_build/metrics/` — Per-tick observability without embedding analysis logic
- `engine_build/analytics/` — Tail-window fingerprints and batch summaries
- `tests/` — Validation workflow (pytest-based)

## Strategic Goals

1. **Preserve deterministic reproducibility** — Non-negotiable system invariant for all simulation logic
2. **Increase ecological realism** — Move toward explicit interactions and spatial structure
3. **Introduce trait heterogeneity** — Enable selection dynamics and adaptive evolution
4. **Build robust analytics stack** — Reproducible research-grade experimentation workflow
5. **Release with verification gates** — All releases pass determinism, invariants, and validation suites

## Current Capabilities (Stage II)

### Deterministic simulation core

- hierarchical RNG setup based on `SeedSequence`
- canonical state hashing
- snapshot -> restore -> continuation equivalence
- isolated stochastic domains for world, movement, reproduction, and energy initialization

### Ecological model

- wrapped 2D world compiled from regime anchors
- fertility/resource fields with bounded regeneration
- energy-gated movement, harvesting, reproduction, and death pathways
- four regime presets: `stable`, `test_stable`, `fragile`, `abundant`

### Experiment and analysis workflow

- batched multi-run orchestration through `Runner`
- per-tick observability via `SimulationMetrics`
- aggregate regime fingerprints over the tail window of each run
- plotting utilities for experiment summaries and development inspection

### Validation coverage

- **deterministic replay:** verify identical seed produces identical state sequences
- **snapshot round-trip:** save state, restore, check equivalence
- **RNG isolation:** verify separate RNG domains don't cross-contaminate
- **structural invariants:** position bounds, agent ID consistency, population caps
- **regime-level tests:** behavioral validation for `stable`, `fragile`, and `abundant` regimes

## Quickstart

### Setup

```bash
git clone https://github.com/jul975/Poject_sim.git
cd Poject_sim
python -m venv .venv
```

Activate the environment:

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running Experiments

Run a default experiment:

```bash
python -m engine_build.main experiment --regime stable
```

Custom batch run with specific seed, run count, and tick count:

```bash
python -m engine_build.main experiment --regime stable --seed 42 --runs 10 --ticks 1000
```

Available regimes: `stable`, `test_stable`, `fragile`, `abundant`

Experiment defaults (when no arguments specified) are set in [engine_build/execution/default.py](engine_build/execution/default.py) and default to `10` runs over `1000` ticks.

**With plotting:**

```bash
python -m engine_build.main experiment --regime stable --runs 10 --ticks 1000 --plot
```

**With verbose development plots:**

```bash
python -m engine_build.main experiment --regime stable --runs 10 --ticks 1000 --plot-dev
```

**Fertility exploration workflow:**

```bash
python -m engine_build.main fertility --seed 42
```

**Experiment CLI Output** includes batch summaries with:
- final population mean and standard deviation
- extinction rate
- capacity-hit rate
- birth/death ratio
- time-series coefficient of variation over tail window

## Validation

All validation workflows are pytest-based and live in [tests/](tests/).

**Run the full test suite:**

```bash
python -m pytest
```

**Run by marker:**

```bash
python -m pytest -m dev        # fast checks
python -m pytest -m validate   # broader validation
python -m pytest -m slow       # full suite including slow tests
```

**Run specific domains:**

```bash
python -m pytest tests/test_determinism.py      # deterministic execution
python -m pytest tests/test_snapshots.py         # snapshot/restore
python -m pytest tests/test_rng_isolation.py     # RNG domain separation
python -m pytest tests/test_invariants.py        # structural consistency
python -m pytest tests/test_regime_validation.py # regime-specific behavior
```

**Available pytest markers** (see [pytest.ini](pytest.ini)):
- `dev` — unit checks
- `validate` — validation suite
- `slow` — long-running tests
- `rng` — RNG-specific tests
- `invariant` — structural invariant checks
- `snapshot` — snapshot/restore tests
- `regime` — regime-specific behavior

## Built-In Regimes

The system includes four canonical ecological regimes, configurable via energy, reproduction, and resource parameters:

- **`stable`** — Bounded population dynamics with sustainable growth and low extinction pressure. Standard baseline for general experiments.
- **`fragile`** — Tight energy constraints with reduced resource regeneration. Population more vulnerable to collapse.
- **`abundant`** — High resource availability and reduced energy requirements. Population can grow toward capacity constraints.
- **`test_stable`** — Variant of `stable` with tighter initial energy budgets, useful for rapid validation checks.

See [engine_build/regimes/registry.py](engine_build/regimes/registry.py) for regime parameter details.

## Roadmap & Next Steps

The project follows a staged development plan with clear exit criteria and validation gates. See [ROADMAP.md](docs/Project_Status/ROADMAP.md) for complete details.

**Current Stage:** Stage II (beta v0.2) — stabilizing baseline quality

**Near-term priorities:**
1. Freeze and maintain Stage II baseline (tests + docs + release hygiene)
2. Implement Stage III interaction model with minimal deterministic surface area
3. Extend validation analytics to cover new interaction-specific invariants

**Version targets:**
- **v0.3** (Stage III) — Explicit Interaction and Spatial Competition
- **v0.4–v0.6** (Stage IV) — Trait Variation and Selection  
- **v1.0** (Stage V) — Research Platform maturity

All releases require:
- Passing determinism, invariant, and regime validation suites
- Updated baseline artifacts and documentation
- Clear change notes when baseline hashes update

## Repository Guide

- `engine_build/main.py`: experiment entry point
- `engine_build/execution/default.py`: default run counts, tick counts, and master seed
- `engine_build/regimes/`: regime presets, specs, and compiler
- `engine_build/runner/regime_runner.py`: batch orchestration and seed spawning
- `engine_build/core/`: engine, world, transitions, snapshots, and state schema
- `engine_build/metrics/`: per-run metrics collection
- `engine_build/analytics/`: fingerprints and batch-level analysis
- `engine_build/visualisation/`: experiment and development plotting helpers
- `tests/`: deterministic, snapshot, invariant, RNG-isolation, and regime validation suites

## Refactor Notes

Recent changes reflected in this README:

- validation has been moved into a dedicated pytest suite under `tests/`
- batch execution is now centered on `Runner` instead of ad hoc experiment loops
- regime handling is split into declarative specs plus a compiler step
- metrics collection and analytics/fingerprinting are separated from the engine core
- top-level experiment runs now expose plotting and fertility exploration flags through `engine_build.main`

## Documentation

For deeper design notes and model background, see:

- [Architecture](docs/canonical_docs/ARCHITECTURE.md)
- [Simulation Pipeline](docs/canonical_docs/SIMULATION_PIPELINE.md)
- [Mathematical Model](docs/canonical_docs/MATHEMATICAL_MODEL.md)
- [RNG Architecture](docs/canonical_docs/RNG_ARCHITECTURE.md)
- [Determinism](docs/canonical_docs/DETERMINISM.md)
- [Configuration](docs/canonical_docs/CONFIGURATION.md)
- [Experiments](docs/canonical_docs/EXPERIMENTS.md)
- [Agent Notes](docs/canonical_docs/Agent.md)

## Current Status & Quality Gates

**Stage II (beta v0.2) Status:**
- ✅ Deterministic execution and replay
- ✅ Snapshot/restore continuation equivalence  
- ✅ Isolated RNG domains (world, movement, reproduction, energy)
- ✅ Canonical state hashing and validation
- ✅ Comprehensive pytest-based validation suite
- ✅ Batch orchestration and metrics collection

**Quality Gates (Required for All Releases):**
- Deterministic behavior required for all simulation logic changes
- No unordered state transitions in core pipeline
- All new features must define invariants and validation checks
- Documentation must track actual code behavior, not intended behavior
- Release tags require passing validation suites and baseline artifacts

**Code Organization Principles:**
- Determinism over convenience
- Explicit entropy over hidden randomness
- Invariants before new features
- Reproducibility constraints are non-negotiable

## Author

Jules Lowette
