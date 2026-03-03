# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent simulation engine for studying emergent behavior under controlled stochasticity.

$$S_{t+1} = T(S_t)$$

**Core idea:** the simulator is a deterministic state machine with explicit entropy control.

It provides:

* Bit-for-bit reproducibility (hash-level)
* Snapshot → clone → continuation equivalence
* Controlled regime experiments (extinction / stable / saturated)
* Deterministic replay of stochastic dynamics

---

## Determinism Contract

> Given identical seed + configuration + initial state, the simulation evolves identically — at the canonical state hash.

Determinism is treated as a formal invariant, not a convenience feature.

---

## Current Status

**Stage II — Controlled Ecological Dynamics (operational)**

Implemented:

* Engine / World / Agent separation
* Independent RNG streams per agent
* Energy → harvest → reproduction coupling
* Resource field with regeneration
* Deterministic birth/death commit ordering
* Batch runner with regime presets
* Determinism test suite (same-seed, snapshot continuation, seed sensitivity)
* Regime validation pipeline (extinction / stable / saturated)
* CLI control for seed, runs, ticks, plotting

In progress:

* Documentation consolidation
* Metric semantics refinement
* Naming cleanup and freeze polish

---

## Quickstart

### Setup

```bash
git clone https://github.com/jul975/Poject_sim.git
cd Poject_sim
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Experiments

Run a default experiment (stable regime):

```bash
python -m engine_build.main --mode experiment --regime stable
```

Override experiment parameters:

```bash
python -m engine_build.main \
    --mode experiment \
    --regime stable \
    --seed 42 \
    --runs 10 \
    --ticks 1000 \
    --plot
```

Parameters:

* `--regime` → stable | extinction | saturated
* `--seed` → master seed (optional; default is canonical seed)
* `--runs` → number of runs in batch
* `--ticks` → ticks per run
* `--plot` → show ensemble + dispersion plots

Experiment mode is flexible and exploration-oriented.

---

## Running Validation

Validate a single regime:

```bash
python -m engine_build.main --mode validation --regime stable
```

Validate all regimes:

```bash
python -m engine_build.main --mode validation --regime all
```

Validation mode:

* Uses canonical defaults
* Is deterministic by design
* Enforces regime-specific invariant contracts

---

## Determinism Test Suite

Run system tests:

```bash
python -m engine_build.test.test_determinism --mode dev
```

Modes:

* `dev` → fast core checks
* `validate` → full system verification
* `full` → includes baseline reference hash checks

Core tests include:

* Same-seed determinism
* Snapshot → clone → continuation equivalence
* Seed sensitivity
* Structural invariants
* RNG stream isolation

---

## Architecture Overview

### Core

* `engine_build/core/engineP4.py`
  Global state machine, birth/death ordering, snapshot, state hash.

* `engine_build/core/agent.py`
  Agent state + independent RNG streams:

  * `move_rng`
  * `repro_rng`
  * `energy_rng`

* `engine_build/core/world.py`
  Resource field, regeneration, toroidal topology.

* `engine_build/core/config.py`
  Frozen dataclasses; all behavior derives from configuration.

---

### Execution & Pipelines

* `engine_build/runner/regime_runner.py`
  Batch orchestration: seed → runs → metrics → fingerprints.

* `engine_build/regimes/registry.py`
  Declarative regime presets.

* `engine_build/experiments/`
  Experiment pipeline + plotting.

* `engine_build/test/validation.py`
  Regime validation matrix.

* `engine_build/test/test_determinism.py`
  Determinism + invariant suites.

---

### Analytics

* `engine_build/analytics/fingerprint.py`

Pure transformations:

* Per-run fingerprints (tail-window metrics)
* Aggregated fingerprints (across-run dispersion + within-run stability)

Clear separation:

* Within-run volatility (temporal CV)
* Across-run dispersion (mean-of-means STD)

---

## State Hash & Snapshot Model

Canonical state hashing is the ground truth of determinism.

Snapshot includes:

* Engine seed lineage metadata
* Config + derived parameters
* World state (resources, fertility, RNG state)
* Agent state (id, position, energy, alive, age, RNG states)

State is serialized deterministically and hashed via SHA256.

---

## Regimes

The engine currently supports three canonical ecological regimes:

* **Extinction** → population collapse
* **Stable** → bounded fluctuation around equilibrium
* **Saturated** → population near capacity ceiling

Each regime has a dedicated validation contract.

---

## Design Principles

* Determinism > convenience
* Explicit entropy > hidden randomness
* Invariants > assumptions
* Snapshot/replay > ad-hoc scripts
* Validation > visual intuition

---

## Roadmap 

### Stage II — Controlled Ecology (current)

* Finalize validation semantics
* Harden metric definitions
* Documentation freeze

### Stage III — Stronger Interaction

* Enhanced spatial competition mechanics
* Optional 2D topology
* Parameter sweep tooling

### Stage IV — Evolution

* Heritable traits
* Mutation
* Selection pressure
* Lineage constraints

### Stage V — Research Platform

* Batch sweeps + dashboards
* Reproducible experiment artifacts
* Deterministic replay hooks for ML

---

## Author

Jules Lowette
