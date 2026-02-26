# 📘 Ecosystem Emergent Behavior Engine

## Architecture & State – End of Stage 2 (Controlled Ecological Dynamics)

---

# 1. Project Positioning

## 1.1 Objective

The Ecosystem Engine is a deterministic, reproducible multi-agent simulation framework designed to study:

* Energy-constrained reproduction
* Resource-coupled survival dynamics
* Spatial competition
* Controlled emergence under strict RNG isolation

The engine prioritizes:

* Determinism
* Canonical serialization
* Snapshot reproducibility
* Identity stability
* Explicit ecological coupling

---

# 2. Architectural Overview

## 2.1 System Decomposition

The system is composed of five primary modules:

```
Engine
├── World
├── Agents (dict[id → Agent])
├── Energy Model (EnergyParams)
├── RNG Infrastructure
└── Serialization Layer (Schema v2)
```

---

## 2.2 Engine Responsibilities

The `Engine` is the orchestrator and enforces global invariants.

Responsibilities:

* Own master SeedSequence
* Derive energy parameters from config ratios
* Manage agent lifecycle (birth & death)
* Enforce population cap
* Maintain identity monotonicity
* Control step ordering
* Provide snapshot and cloning
* Provide canonical state hashing

Invariant guarantees:

* 0 ≤ position < world_size
* id matches dict key
* next_agent_id strictly monotonic
* population ≤ max_agent_count

---

## 2.3 World Responsibilities

The `World` encapsulates environmental state:

* Toroidal topology (1D)
* Fertility scalar field
* Resource array
* Resource regeneration
* Harvest constraint (max_harvest)
* Independent world RNG

Topology:

```
position = position % world_size
```

Harvest rule:

```
harvest = min(available_resources, max_harvest)
```

---

## 2.4 Agent Responsibilities

Each Agent maintains:

* Unique ID
* Deterministic seed lineage
* Independent RNG streams:

  * movement RNG
  * reproduction RNG
  * energy initialization RNG
* Energy level
* Position
* Alive flag
* Spawn counter

Agent Step Order:

1. Deduct movement cost
2. Move ±1
3. Toroidal wrap
4. Death check
5. Harvest
6. Reproduction check

Reproduction is energy-gated:

```
energy ≥ reproduction_threshold
```

Reproduction cost deducted on success.

---

# 3. Energy System (Formal Model)

Energy parameters derived from ratios:

```
movement_cost           = α * max_harvest
reproduction_threshold  = γ * movement_cost
reproduction_cost       = β * reproduction_threshold
```

Ratios:

| Symbol | Meaning                | Interpretation                  |
| ------ | ---------------------- | ------------------------------- |
| α      | Metabolic pressure     | Movement sustainability         |
| β      | Reproductive depletion | Post-reproduction survival      |
| γ      | Energy maturity scale  | Energy accumulation requirement |

Design goal:
Control macroscopic dynamics through dimensionless ratios rather than absolute constants.

---

# 4. Determinism Infrastructure

## 4.1 RNG Architecture

Hierarchy:

```
Engine.master_ss
├── World seed
└── Agent seeds
     ├── move_ss
     ├── repro_ss
     └── energy_ss
```

Each stream is isolated.

RNG Isolation Test:
Movement trajectories must be identical even if reproduction probability changes.

---

## 4.2 Snapshot & Serialization

Schema Version: 2

Serialized components:

* Engine tick
* next_agent_id
* Rule environment
* World state
* RNG states
* Agents (sorted by ID)

State hash:

```
sha256(get_state_bytes(engine))
```

This defines canonical equivalence.

---

# 5. Lifecycle Mechanics (Current State)

### Implemented:

* Energy-constrained reproduction
* Starvation death
* Population cap enforcement
* Implicit competition (update-order based)

### Pending:

* Death classification system
* Aging
* Explicit spatial competition
* 2D topology

---

# 6. Testing Protocol

Test domains:

1. Determinism
2. Structural invariants
3. Dynamics sanity
4. RNG isolation
5. Reference hash

Development mode:
Core deterministic safety.

Validation mode:
Full system verification.

---

# 7. Current System Capabilities

The system now supports:

* Deterministic multi-agent simulation
* Reproducible cloning
* Energy-limited reproduction
* Resource regeneration
* Canonical state hashing
* Lightweight metrics instrumentation

This marks the transition from:

“Deterministic sandbox”
→
“Deterministic ecological system”

---

# 8. Known Limitations

* 1D topology
* No aging
* Implicit (not explicit) competition
* No trait variation
* No selection pressure modeling
* No strategy layer
* No migration preference

---

# 9. Stage 2 Completion Criteria

Stage 2 will be complete when:

* Reproduction is energy-constrained (✔)
* Death classification exists
* Aging implemented
* Explicit competition implemented
* RNG isolation verified post-expansion
* 2D topology implemented
* Population/resource oscillations observable

---

# 10. Stage 3 Preview

Stage 3 introduces:

* Spatial clustering
* Density waves
* Trait heterogeneity
* Strategy-driven movement
* Emergent ecological patterns

