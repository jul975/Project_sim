# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent ecology simulator for running reproducible experiments on a wrapped 2D resource landscape. The project evolves from a foundational deterministic kernel toward a research-grade experimentation platform with explicit interactions, trait heterogeneity, and advanced analytics.

$$S_{t+1} = T(S_t)$$

## Project Status

**Current Stage:** Pre-Stage III (beta v0.2.1) — Actively Developed  
**Development Velocity:** 100+ commits in ~4 weeks (rapid iteration & optimization phase)  
**Recent Work:** 2D world implementation, energy system decoupling, performance profiling infrastructure  
**Target Version:** v0.3 (Stage III) — Explicit Interaction and Spatial Competition  

**Note:** This project is under active development with frequent refactoring. High commit frequency indicates iterative problem-solving and optimization, not instability. All changes maintain deterministic reproducibility as a non-negotiable constraint.

See [ROADMAP](docs/Project_Status/ROADMAP.md) for strategic goals and [CURRENT_STATE](docs/Project_Status/CURRENT_STATE.md) for detailed development status.

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

## Current Capabilities (Pre-Stage III)

### Deterministic simulation core

- hierarchical RNG setup based on `SeedSequence`
- canonical state hashing verified across 2D refactoring
- snapshot → restore → continuation equivalence maintained
- isolated stochastic domains for world, movement, reproduction, and energy initialization
- performance profiling framework for bottleneck identification

### Ecological model with 2D spatial structure

- **2D toroidal world** with configurable width × height grid (newly completed)
- 2D fertility and resource fields with spatially-correlated generation
- agent positions as `(x, y)` coordinates enabling neighborhood queries
- energy-gated movement, harvesting, reproduction, and death pathways
- decoupled energy initialization supporting future trait heterogeneity
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

The project follows a staged development plan with clear exit criteria and validation gates. See [ROADMAP.md](docs/Project_Status/ROADMAP.md) and [CURRENT_STATE.md](docs/Project_Status/CURRENT_STATE.md) for complete details.

**Current Stage:** Pre-Stage III (beta v0.2.1) — 2D refactoring complete, performance optimization in progress

**Near-term priorities** (subject to iteration based on discoveries):
1. Complete regime validation test refactoring (align with current regime names)
2. Define validation thresholds for fragile/abundant regimes via empirical runs
3. Optimize agent initialization performance (reduce batch runtime from ~15-20min to <5min)
4. Extend metrics for 2D spatial patterns (clustering, occupancy)
5. Design Stage III spatial interaction mechanics before implementation

**Provisional version targets** (timelines may shift during active optimization):
- **v0.3** (Stage III) — Explicit Interaction and Spatial Competition (foundation complete, feature development pending)
- **v0.4–v0.6** (Stage IV) — Trait Variation and Selection  
- **v1.0** (Stage V) — Research Platform maturity

**Development Approach:** Given the active optimization and rapid iteration pace (100+ commits/4 weeks), version timelines are estimates subject to adjustment as performance work and design iterations emerge.

All releases require:
- Passing determinism, invariant, and regime validation suites
- Updated baseline artifacts and documentation
- Clear change notes when baseline hashes update
- Determinism verification across all refactoring changes

## Repository Guide

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

## Recent Refactoring Notes (March 8-15, 2026)

Major systems restructuring completed to prepare for Stage III spatial interactions:

- **2D world topology:** Transitioned from 1D wrapped array to 2D height×width grid with proper toroidal semantics
- **Energy system decoupling:** Agent initialization broken into four independent phases (`_init_identity`, `_init_lineage`, `_init_rngs`, `_init_state`) enabling modular customization and performance profiling
- **Agent factory pattern:** Extracted agent creation into dedicated module with separate code paths for initial vs. newborn agents
- **Performance infrastructure:** Added `PerfSink` framework for bottleneck measurement; agent initialization identified as critical path
- **State schema updates:** Snapshots and serialization refactored to handle 2D positions; determinism verified throughout
- **Metrics pipeline refinement:** Restructured for performance data integration while maintaining fingerprint analysis capabilities

**Determinism Impact:** All changes verified to maintain bit-exact reproducibility with fixed seeds. State hashes unchanged (refactoring is transparent to validation).

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

**Pre-Stage III (beta v0.2.1) Status — Actively Under Development:**
- ✅ 2D world model implementation completed and determinism-verified
- ✅ Energy system decoupled into modular initialization phases
- ✅ Agent factory pattern extracted for cleaner creation paths
- ✅ Performance profiling framework integrated and generating insights (PerfSink)
- ✅ Deterministic execution verified across all refactoring changes  
- ✅ Snapshot/restore continuation equivalence maintained through topology transition
- ✅ Isolated RNG domains (world, movement, reproduction, energy)
- ✅ Canonical state hashing verified unchanged (determinism preserved)
- ✅ Comprehensive pytest-based validation suite (extended for 2D features)
- ✅ Batch orchestration with metrics collection
- 🔄 Regime validation tests refactoring (code cleanup ongoing)
- 🔄 Performance optimization of agent initialization (identified as bottleneck ~70% of runtime, optimization in progress)
- 🔄 Extend metrics for 2D spatial patterns (in queue for Stage III)

**Development Notes:**
- High commit frequency reflects active problem-solving and iterative refinement
- All changes validated against determinism suites before integration
- Performance improvements underway while maintaining reproducibility
- Timeline projections for Stage III and beyond are provisional pending optimization completion

**Quality Gates (Required for All Releases):**
- Deterministic behavior required across all simulation logic refactoring
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
