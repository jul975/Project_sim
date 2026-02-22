
---

# Ecosystem Emergent Behavior Simulator

A deterministic multi-agent simulation engine for studying emergent behavior in stochastic systems.

The simulator is designed as a **deterministic state machine with explicit entropy control**, enabling:

* Bit-for-bit reproducibility
* Snapshot branching
* Controlled evolutionary experiments
* Deterministic replay of stochastic dynamics

---

# Core Design Goal

> Given identical initial seed and state, the simulation must evolve identically — at the hash level.

Determinism is not treated as a convenience feature.
It is treated as a formal invariant.

---

# Current Architecture

## 1. Engine

**Location:** `engineP4.py`

### Responsibilities

* Maintains global simulation state
* Owns world instance
* Owns agent registry (`dict[id → Agent]`)
* Enforces invariants
* Handles reproduction and death ordering
* Produces canonical state hash
* Creates snapshots
* Reconstructs from snapshot

### Engine Invariants

1. **Spatial invariant**

```python
0 <= position < world_size
```

Enforced via toroidal wrapping.

2. **Identity invariant**
   Agent ID equals dictionary key.

3. **Population invariant**

```python
len(agents) <= max_agent_count
```

4. **Deterministic stepping invariant**
   Agents are stepped in sorted ID order.

---

## 2. Agent

**Location:** `agent.py`

Each agent contains:

* Stable ID
* Position
* Energy level
* Alive state
* Spawn lineage metadata
* Independent RNG streams:

  * `move_rng`
  * `repro_rng`
  * `energy_rng`

### RNG Design

Each agent:

* Receives a `SeedSequence`
* Spawns 3 child streams
* Stores spawn lineage data manually
* Restores full RNG state during snapshot reconstruction

RNG reconstruction uses:

* `bit_generator.state` restore
* Custom seed sequence reconstruction

No global RNG is ever used.

---

## 3. World

**Location:** `world.py`

Minimal world state:

* `tick`
* `world_size`
* `change_condition`

Implements toroidal topology:

```python
position = position % world_size
```

---

## 4. Configuration

**Location:** `config.py`

Frozen dataclass defining:

* Population limits
* Energy parameters
* Reproduction parameters
* World size
* Future resource parameters

All engine behavior derives from configuration.

---

## 5. Canonical State Schema

**Location:** `state_schema.py`

State Schema v1:

```text
schema_version
world.tick
agent_count
for each agent (sorted):
    id
    position
    energy
    alive
```

Serialized to bytes → hashed via SHA256.

This is the backbone of determinism validation.

---

## 6. Metrics Layer

**Location:** `metrics.py`

Collected per tick:

* Population
* Mean energy
* Births
* Deaths

Metrics recording never mutates engine state.

---

# Deterministic Testing Framework

**Location:** `test_engine.py`

The engine is validated against six invariants:

---

## 1. Same Seed Determinism

Two engines with identical seed → identical world.

---

## 2. Canonical Determinism (Primary Test)

Procedure:

1. Run engine to `T_mid`
2. Snapshot
3. Clone from snapshot
4. Continue both

Must satisfy:

```python
eng1 == clone
```

Optional full-trajectory check:

```python
eng_full == eng_interrupted
```

---

## 3. Snapshot Idempotence

Snapshot and immediate reconstruction must preserve state exactly.

---

## 4. Multi-Clone Consistency

Multiple clones from identical snapshot must be identical.

---

## 5. Seed Sensitivity

Different seeds must produce different state hashes.

---

## 6. Agent Health Test

Ensures population dynamics vary over time.

---

# Current Stage Status

## Stage 1 — Deterministic Core

**Status: ~90% complete**

### Completed

* Explicit RNG streams
* Deterministic ordering
* Snapshot/restore
* Canonical hashing
* Agent dict refactor
* World separation
* Metrics separation
* Population capacity logic

### Remaining

* Removal of remaining SeedSequence lineage coupling
* Final ID monotonicity formalization
* Formal RNG independence test
* Death-stability identity test
* Schema v2 planning

---

# Execution Model

Per tick:

1. Agents step (sorted order)
2. Deaths recorded
3. Reproduction candidates recorded
4. Capacity computed
5. Deaths committed
6. Births committed
7. World tick increments

Death occurs before birth.
This ordering is deterministic and intentional.

---

# Installation

```bash
git clone https://github.com/<username>/ecosystem-emergent-simulator.git
cd ecosystem-emergent-simulator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

# Running Tests

```bash
python -m engine_build.test.test_engine
```

Primary determinism test:

```python
test_canonical_determinism_suite(42, full_trajectory=True)
```

---

# Design Philosophy

* Determinism > Convenience
* Explicit entropy > Hidden randomness
* State machine > simulation script
* Reproducibility > speed
* Invariants > assumptions

---

# Future Stages

## Stage 2 — Ecology Layer

* Resource fields
* Energy harvesting
* Predator/prey interactions

## Stage 3 — Evolution

* Heritable traits
* Mutation
* Selection pressure

## Stage 4 — Machine Learning

* Policy-driven agents
* Reinforcement learning hooks
* Deterministic training replay

## Stage 5 — Research Platform

* Batch runner
* Parameter sweeps
* Statistical analysis
* Visualization

---

# Why This Engine Is Different

Most ABM frameworks:

* Leak entropy
* Cannot replay exact trajectories
* Do not hash canonical state

This engine treats stochastic simulation as a formally verifiable deterministic process.

---

# Author

Jules Lowette
