# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent simulation engine for studying emergent ecological dynamics under controlled stochasticity.

$$S_{t+1} = T(S_t)$$

## Overview
The project models population dynamics from local rules:
- movement
- energy expenditure
- resource harvesting
- stochastic reproduction

Despite stochastic events, trajectories are reproducible under fixed `(seed, configuration, code version, runtime)`.

## Core Capabilities
### Deterministic simulation
- isolated RNG streams
- canonical state serialization and SHA256 state hashing
- snapshot -> clone -> continuation consistency
- reference-hash regression checks

### Ecological dynamics
- 1D toroidal world
- fertility/resource fields with bounded regeneration
- energy-gated reproduction and death pathways
- regime-driven behavior (`extinction`, `stable`, `saturated`)

### Experiment tooling
- batch runner for multi-run experiments
- validation contracts per regime
- aggregate metrics and fingerprint analytics

## Quickstart
### Setup
```bash
git clone https://github.com/jul975/Poject_sim.git
cd Poject_sim
python -m venv .venv
```

Activate environment:

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
pip install -r requirements.txt
```

### Run experiments
Default experiment:
```bash
python -m engine_build.main --mode experiment --regime stable
```

Custom experiment:
```bash
python -m engine_build.main --mode experiment --regime stable --seed 42 --runs 10 --ticks 1000 --plot
```

### Run validation
Single regime:
```bash
python -m engine_build.main --mode validation --regime stable
```

All regimes:
```bash
python -m engine_build.main --mode validation --regime all
```

### Run determinism suite
```bash
python -m engine_build.test.test_determinism --mode full
```

Modes:
- `dev`: core determinism + structural invariants
- `validate`: `dev` + dynamics sanity + RNG isolation
- `full`: `validate` + reference baseline hash
- `reference`: print current baseline candidate hash

## Regimes
- `extinction`: collapse-dominant behavior
- `stable`: bounded population dynamics
- `saturated`: near-capacity occupancy dynamics

## Example Regimes

The simulator can produce several characteristic ecological regimes depending on parameter configuration.

### Stable Regime

![Stable Regime](docs/images/regime_stable.png)

Population fluctuates around a stable equilibrium.

---

### Extinction Regime

![Extinction Regime](docs/images/regime_extinction.png)

Energy constraints lead to population collapse.

---

### Saturated Regime

![Saturated Regime](docs/images/regime_saturated.png)

Population approaches the configured capacity ceiling.

## Documentation
### Canonical technical docs
- [Architecture](docs/canonical_docs/ARCHITECTURE.md)
- [Simulation Pipeline](docs/canonical_docs/SIMULATION_PIPELINE.md)
- [Mathematical Model](docs/canonical_docs/MATHEMATICAL_MODEL.md)
- [RNG Architecture](docs/canonical_docs/RNG_ARCHITECTURE.md)
- [Determinism](docs/canonical_docs/DETERMINISM.md)
- [Configuration](docs/canonical_docs/CONFIGURATION.md)
- [Experiments and Regime Validation](docs/canonical_docs/EXPERIMENTS.md)
- [Agent/Energy Notes](docs/canonical_docs/Agent.md)

### Project status and release
- [Current Stage Status](docs/Project_Status/CURRENT.md)
- [Roadmap](docs/Project_Status/ROADMAP.md)
- [Release Note v0.2](docs/releases/v0.2.md)

## Current Stage
Current baseline: **Stage II / beta0.2**.

Implemented focus:
- deterministic ecological core
- reproducible validation pipeline
- canonical regime validation for `extinction`, `stable`, `saturated`

Next focus (Stage III / v0.3):
- explicit interaction and competition mechanics
- stronger spatial structure
- validation expansion while preserving determinism guarantees

## Design Principles
- determinism over convenience
- explicit entropy over hidden randomness
- invariants before features
- reproducibility before optimization

## Author
Jules Lowette




