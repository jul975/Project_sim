# Ecosystem Engine Architecture

### Stage 2 — Controlled Ecological Dynamics

---

# 1. System Purpose

## 1.1 Objective

The **Ecosystem Engine** is a deterministic multi-agent simulation framework designed to study controlled ecological dynamics under strict reproducibility constraints.

The system models:

* energy-constrained reproduction
* resource-coupled survival
* spatial competition
* emergent population dynamics

while maintaining strict guarantees around:

* deterministic execution
* canonical state representation
* reproducible simulation snapshots
* RNG stream isolation
* identity stability

The engine is therefore both:

* a **simulation environment**
* and a **research-grade deterministic system**

for studying emergent behavior.

---

# 2. System Architecture

## 2.1 High-Level Decomposition

The engine is composed of five core subsystems:

```
Engine
├── World
├── Agents (dict[id → Agent])
├── Energy Model (EnergyParams)
├── RNG Infrastructure
└── Serialization Layer (Schema v2)
```

Each subsystem maintains clearly defined responsibilities to preserve determinism and architectural isolation.

---

# 3. Core Engine

## 3.1 Responsibilities

The **Engine** acts as the global orchestrator and enforces system-wide invariants.

Primary responsibilities include:

* ownership of the **master SeedSequence**
* derivation of **energy parameters** from dimensionless ratios
* management of **agent lifecycle**

  * birth
  * death
* enforcement of **population caps**
* maintenance of **identity monotonicity**
* execution of **simulation step ordering**
* provision of:

  * snapshot serialization
  * engine cloning
  * canonical state hashing

---

## 3.2 Engine Invariants

The engine enforces the following structural guarantees:

```
0 ≤ agent.position < world_size
agent.id == dict key
next_agent_id strictly monotonic
population ≤ max_agent_count
```

These invariants ensure that simulation state remains structurally valid across all ticks.

---

# 4. World Subsystem

## 4.1 Responsibilities

The **World** encapsulates environmental state and resource dynamics.

It manages:

* spatial topology
* fertility distribution
* resource availability
* resource regeneration
* harvesting constraints
* independent RNG state

---

## 4.2 Spatial Topology

Current implementation:

```
1D toroidal world
```

Wrap rule:

```
position = position % world_size
```

This ensures spatial continuity without boundary artifacts.

---

## 4.3 Resource Model

The world maintains two primary fields:

```
fertility → maximum resource capacity
resources → current resource levels
```

Regeneration model:

```
resources += regen_rate
resources = min(resources, fertility)
```

---

## 4.4 Harvest Rule

Agent harvesting is constrained:

```
harvest = min(available_resources, max_harvest)
```

This prevents instantaneous depletion and introduces natural competition.

---

# 5. Agent System

## 5.1 Agent State

Each agent maintains:

* unique identifier
* deterministic seed lineage
* position
* energy level
* alive status
* spawn counter

Agents also maintain **independent RNG streams**:

```
movement RNG
reproduction RNG
energy initialization RNG
```

These streams are isolated to preserve deterministic behavior.

---

## 5.2 Agent Step Order

Each simulation tick executes the following agent lifecycle:

```
1. Deduct movement cost
2. Move (±1)
3. Apply toroidal wrap
4. Death check (energy ≤ 0)
5. Harvest resources
6. Reproduction check
```

---

## 5.3 Reproduction Mechanism

Reproduction is **energy-gated**.

Condition:

```
energy ≥ reproduction_threshold
```

Upon successful reproduction:

```
energy -= reproduction_cost
```

A new agent is spawned using deterministic RNG lineage derived from the parent.

---

# 6. Energy System

## 6.1 Dimensionless Ratio Model

Energy dynamics are derived from **dimensionless ratios** rather than absolute constants.

```
movement_cost           = α * max_harvest
reproduction_threshold  = γ * movement_cost
reproduction_cost       = β * reproduction_threshold
```

---

## 6.2 Ratio Definitions

| Symbol | Name                   | Meaning                                          |
| ------ | ---------------------- | ------------------------------------------------ |
| α      | Metabolic pressure     | movement sustainability                          |
| β      | Reproductive depletion | post-reproduction survival                       |
| γ      | Energy maturity scale  | energy accumulation required before reproduction |

---

## 6.3 Design Principle

Using ratios instead of absolute values allows ecological regimes to be tuned while maintaining system stability.

This enables:

* reproducible regime configuration
* scale-independent parameterization
* controlled macro-dynamics.

---

# 7. Determinism Infrastructure

Determinism is a first-class architectural constraint.

---

## 7.1 RNG Hierarchy

The system uses hierarchical RNG lineage.

```
Engine.master_ss
├── World seed
└── Agent seeds
     ├── movement_rng
     ├── reproduction_rng
     └── energy_rng
```

Each stochastic subsystem operates on its own independent RNG stream.

---

## 7.2 RNG Isolation Guarantee

A core invariant of the system:

> Changing reproduction outcomes must **not change movement trajectories**.

This ensures:

* reproducibility
* causal isolation
* stable debugging.

---

# 8. Serialization System

## 8.1 Snapshot Schema

Current version:

```
Schema v2
```

Serialized components include:

```
engine tick
next_agent_id
energy parameters
world state
RNG states
agent states (sorted by ID)
```

---

## 8.2 Canonical State Hash

Simulation equivalence is defined through canonical hashing.

```
sha256(get_state_bytes(engine))
```

Two simulations are considered identical if their hashes match.

---

# 9. Lifecycle Mechanics

## 9.1 Implemented Features

Current system capabilities include:

* energy-constrained reproduction
* starvation death
* population cap enforcement
* implicit competition through update ordering
* resource regeneration
* deterministic cloning
* canonical state hashing

These features mark the transition from:

```
deterministic sandbox
→ deterministic ecological system
```

---

# 10. Testing Framework

The engine includes a structured validation system.

Test domains:

1. **Determinism**
2. **Structural invariants**
3. **Dynamics sanity**
4. **RNG isolation**
5. **Reference state hashing**

---

## 10.1 Execution Modes

Two operational modes exist.

### Development Mode

Focus:

```
rapid iteration
deterministic safety checks
```

---

### Validation Mode

Focus:

```
full system verification
reproducibility assurance
regime validation
```

---

# 11. Known Limitations

Current system limitations:

* 1D spatial topology
* no aging system
* implicit competition only
* no trait variation
* no evolutionary pressure
* no strategic behavior layer
* no migration preference

---

# 12. Stage 2 Completion Criteria

Stage 2 is considered complete once the following are implemented:

* energy-constrained reproduction ✔
* death classification system
* aging mechanics
* explicit spatial competition
* RNG isolation verified after expansion
* 2D spatial topology
* observable population/resource oscillations

---

# 13. Stage 3 Preview

Stage 3 will introduce higher-order ecological dynamics:

* spatial clustering
* density waves
* trait heterogeneity
* strategy-driven movement
* emergent ecosystem patterns

These features transition the engine toward a **fully emergent ecological simulation platform**.

---

## Architectural Position

The system now occupies the boundary between:

```
deterministic simulation framework
+
controlled ecological dynamics engine
```

forming the foundation for future **emergent behavior research.**

---


# 14. Simulation Execution Model

The Ecosystem Engine operates on a **deterministic discrete-time simulation loop**.

Each tick represents one atomic ecological update across the entire system.

## 14.1 Engine Step Pipeline

Each simulation step follows a strict execution order:

```
Engine.step()

1. Resource regeneration
2. Agent update loop
3. Agent birth registration
4. Agent death cleanup
5. Population cap enforcement
6. Metrics collection
7. Tick increment
```

This ordering ensures:

* deterministic execution
* consistent state transitions
* reproducible simulation trajectories.

---

## 14.2 Expanded Execution Flow

```
┌──────────────────────────────┐
│ Engine.step()                │
└───────────────┬──────────────┘
                │
                ▼
     ┌──────────────────────┐
     │ World.regenerate()   │
     └──────────────┬───────┘
                    │
                    ▼
       ┌────────────────────────┐
       │ Agent update loop      │
       │ for agent in agents    │
       └──────────────┬─────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Agent.step()        │
           └──────────┬──────────┘
                      │
          ┌───────────▼───────────┐
          │ Movement              │
          │ Energy deduction      │
          │ Harvest               │
          │ Reproduction check    │
          │ Death check           │
          └───────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │ Birth registration     │
         └──────────────┬─────────┘
                        │
                        ▼
         ┌────────────────────────┐
         │ Death cleanup          │
         └──────────────┬─────────┘
                        │
                        ▼
         ┌────────────────────────┐
         │ Population cap check   │
         └──────────────┬─────────┘
                        │
                        ▼
         ┌────────────────────────┐
         │ Metrics collection     │
         └──────────────┬─────────┘
                        │
                        ▼
                 Tick += 1
```

---

# 15. Data Flow Architecture

The engine follows a **top-down state flow model**.

```
Config
   │
   ▼
Engine
   │
   ├── World
   │      ├── fertility field
   │      ├── resource field
   │      └── world RNG
   │
   ├── Agents
   │      ├── position
   │      ├── energy
   │      ├── RNG streams
   │      └── lifecycle state
   │
   └── EnergyParams
```

The engine orchestrates updates but **does not store ecological logic directly**.

Subsystems remain modular.

---

# 16. State Dependency Graph

The system's state update dependencies can be expressed as:

```
resources(t)
    │
    ▼
agent harvest
    │
    ▼
agent energy
    │
    ├────► reproduction
    │
    └────► death
```

Full dependency chain:

```
World.resources(t)
        │
        ▼
Agent.harvest()
        │
        ▼
Agent.energy(t)
        │
        ├────► reproduction
        │
        └────► death
        │
        ▼
Agent population(t+1)
```

This dependency chain is the **core ecological feedback loop**.

---

# 17. Determinism Contract

The engine is designed around strict **deterministic guarantees**.

A simulation run is fully determined by:

```
(seed, config, code_version)
```

If these remain constant:

```
simulation_state(t) is identical across runs
```

---

## 17.1 Determinism Requirements

The engine enforces the following constraints:

### Stable iteration order

Agents are processed in deterministic order.

```
sorted(agent_ids)
```

### RNG isolation

Independent streams are used for:

```
movement RNG
reproduction RNG
energy RNG
world RNG
```

This prevents stochastic cross-contamination.

---

### Canonical serialization

Snapshots must produce identical byte representations.

```
sha256(state_bytes)
```

Used for determinism verification.

---

# 18. Agent Lifecycle Model

Agents follow a simple deterministic lifecycle.

```
         ┌───────────┐
         │  Spawn    │
         └─────┬─────┘
               │
               ▼
        ┌────────────┐
        │  Alive     │
        │ (active)   │
        └─────┬──────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
Move      Reproduce    Die
```

---

## 18.1 Lifecycle State Machine

```
SPAWN
  │
  ▼
ALIVE
  │
  ├── energy <= 0 ─────► DEAD
  │
  └── energy ≥ threshold ─► REPRODUCE
```

After reproduction:

```
energy -= reproduction_cost
```

Agent returns to **ALIVE** state.

---

# 19. System Complexity Scaling

The architecture is intentionally designed to scale across multiple complexity stages.

| Stage   | Focus                  | System Complexity |
| ------- | ---------------------- | ----------------- |
| Stage 1 | Deterministic core     | low               |
| Stage 2 | Ecological coupling    | medium            |
| Stage 3 | Emergent behaviors     | high              |
| Stage 4 | Event-driven ecosystem | very high         |

Stage 2 establishes the **minimal ecological feedback loop** required for emergent dynamics.

---

# 20. Research Design Philosophy

The engine follows several core design principles:

### Determinism first

Reproducibility is more important than raw performance.

---

### Explicit ecological coupling

All population dynamics must derive from:

```
energy
resources
movement
```

No hidden forces.

---

### Ratio-based parameterization

Dimensionless ratios control system regimes.

This ensures:

* stable scaling
* interpretable dynamics
* easier parameter sweeps.

---

### Canonical state representation

Every simulation state must be:

```
serializable
hashable
comparable
```

This enables rigorous experimentation.

---

# 21. Architectural Summary

The current engine provides:

```
Deterministic execution
+
Resource-energy coupling
+
Spatial competition
+
Canonical simulation states
```

This forms a **stable experimental platform** for studying emergent ecological systems.

---
