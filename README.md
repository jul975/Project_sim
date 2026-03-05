# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent simulation engine for studying **emergent ecological dynamics under controlled stochasticity**.


$$S_{t+1} = T(S_t)$$

The simulator treats the environment as a **deterministic state machine with explicit entropy control**, enabling reproducible exploration of stochastic ecological systems.

---

# Project Overview

The Ecosystem Engine provides a controlled environment for exploring how population dynamics emerge from simple local interactions such as:

- movement
- energy consumption
- resource harvesting
- reproduction

Despite stochastic agent behavior, the engine guarantees **bit-level reproducibility**.

Given identical seed, configuration, and initial state:


same inputs → identical simulation trajectory → identical state hash


This makes the engine suitable for:

- deterministic simulation research
- controlled regime experimentation
- reproducible ecological modeling
- emergent behavior studies

---

# Key Features

### Deterministic Simulation Core

- Explicit RNG stream separation
- Canonical state serialization
- SHA256 state hashing
- Snapshot → clone → continuation equivalence

### Ecological Dynamics

- Energy-driven survival and reproduction
- Resource fields with regeneration
- Spatial competition
- Configurable ecological regimes

### Experiment Infrastructure

- Batch runner for ensemble experiments
- Regime presets (extinction / stable / saturated)
- Determinism and invariant validation suites
- Metrics and fingerprint analytics

---

# Quickstart

## Setup

```bash
git clone https://github.com/jul975/Poject_sim.git
cd Poject_sim

python -m venv .venv 
```

# Windows
```bash
.venv\Scripts\activate
```

# Linux/macOS
```bash
source .venv/bin/activate

pip install -r requirements.txt
Running Experiments

Run a default experiment:

python -m engine_build.main --mode experiment --regime stable
```

### Custom run:

```bash
python -m engine_build.main \
    --mode experiment \
    --regime stable \
    --seed 42 \
    --runs 10 \
    --ticks 1000 \
    --plot
Parameters
Parameter	Description
--regime	stable | extinction | saturated
--seed	master RNG seed
--runs	number of runs in batch
--ticks	ticks per run
--plot	show ensemble plots
```

Experiment mode is designed for exploration and regime analysis.

### Running Validation

Validate a specific regime:

```bash
python -m engine_build.main --mode validation --regime stable

Validate all regimes:

python -m engine_build.main --mode validation --regime all

```

Validation mode:

- uses canonical configurations

- verifies deterministic guarantees

- checks regime-specific invariants

### Determinism Test Suite

Run deterministic system tests:

```bash
python -m engine_build.test.test_determinism --mode dev

```

Modes:

```bash
  Mode	    -> Purpose
  dev	    -> fast core checks
  validate	-> full deterministic verification
  full	    -> includes reference state hash checks
```

Core tests include:

- same-seed determinism

- snapshot → clone → continuation equivalence
 - seed sensitivity

- structural invariants

- RNG stream isolation

## Architecture (High Level)

The engine is composed of four main subsystems.
```bash
Engine
├── World
├── Agents
├── RNG Infrastructure
└── Analytics / Experiments
```

###  Engine

**Global simulation orchestrator.**

Responsible for:
- tick progression

- deterministic update ordering

- birth/death commit

- snapshot and state hashing

### World

Environmental state.

Contains:

- resource field

- fertility limits

- regeneration mechanics

- toroidal topology

### Agents

Autonomous entities with independent stochastic behavior.

Each agent owns three RNG streams:

1. movement RNG

2. reproduction RNG

3. energy initialization RNG

### Experiment Pipeline

Supports:

1. batch experiments

2. regime validation

3. metrics aggregation

4. fingerprint analytics

### Ecological Regimes

Three canonical regimes are currently supported.

```bash
Regime	Behavior
Extinction   ->   population collapse
Stable       ->   bounded equilibrium dynamics
Saturated    ->   population near capacity ceiling
```

Each regime includes a validation contract to verify expected system behavior.

Documentation

Detailed documentation is located in /docs.

```bash
Document	              Description
ARCHITECTURE.md	          System architecture
DETERMINISM.md	          Determinism guarantees
MATHEMATICAL_MODEL.md	  Formal model of system dynamics
SIMULATION_PIPELINE.md	  Execution order of simulation steps
RNG_ARCHITECTURE.md	      RNG lineage and isolation
Current                   Status
```

## Stage II — Controlled Ecological Dynamics

**Implemented:**

- deterministic engine core

- resource-energy coupling

- regime experiment pipeline

- validation and determinism tests

**Next stage:**

## Stage III — Stronger Interaction

**Planned:**

- enhanced spatial competition

- optional 2D topology

- expanded parameter sweep tooling

## Design Principles

The system follows several core engineering principles.

- Determinism over convenience

- Explicit entropy over hidden randomness

- Formal invariants over assumptions

- Snapshot/replay over ad-hoc scripts

- Validation over visual intuition

## Author

Jules Lowette