Below is your text **cleaned and formatted as a proper GitHub-ready `.md` file**.
You can **paste this directly into a Markdown file** (for example `docs/core_architecture.md`).

I preserved the structure but converted all equations, lists, and headings into **valid Markdown + LaTeX math blocks** so it renders correctly on GitHub / Obsidian / Notion.

---

```markdown
# Core System Architecture

---

# LEVEL 0 — The Whole System

## System Definition

The simulator is a **deterministic discrete-time multi-agent dynamical system with controlled stochastic processes**.

The global system evolves according to a transition operator:

$S_{t+1} = T(S_t)$

Where:

- \(S_t\) is the full simulation state at tick \(t\)
- \(T\) is the deterministic transition function implemented by the **Engine**

State includes:

- World state
- Agent states
- RNG states
- Structural metadata (next IDs, spawn lineage)

Because RNG states are part of the state, **identical seeds and state produce identical trajectories**.

---

## System Components

The simulator consists of three main subsystems.

### 1. Core Dynamics

Responsible for system evolution.

Modules:

```

Engine
Agent
World
Config

```

---

### 2. Determinism Infrastructure

Responsible for **reproducibility guarantees**.

Modules:

```

state serialization
canonical hashing
snapshot / clone
RNG reconstruction
seed lineage tracking

```

---

### 3. Experimental Infrastructure

Responsible for **measurement, validation, and experimentation**.

Modules:

```

metrics collection
fingerprint computation
batch runner
validation pipeline

```

These layers observe the simulation but **do not modify engine state**.

---

# LEVEL 1 — Core Dynamics Subsystem

---

# 1.1 Engine — Global Transition Operator

## Purpose

The Engine implements the system transition operator:

\[
T(S_t)
\]

It is responsible for:

- deterministic iteration
- structural mutation
- constraint enforcement
- ordering guarantees

The Engine is the **only component allowed to modify global state**.

---

## Inputs / Outputs

**Input**

\[
S_t = (world, agents, RNG\ states)
\]

**Output**

\[
S_{t+1}
\]

---

## Internal Composing Subsystems

Engine maintains:

```

agents : dict[int → Agent]
world  : World
config : SimulationConfig

```

Runtime execution components:

```

sorted agent ordering
step evaluation loop
pending death buffer
pending birth buffer
capacity projection
commit phase
world tick update

````

---

## Tick Execution Order

Each tick executes the following phases.

---

### 1 — Agent Evaluation Phase

Agents are iterated in **sorted ID order**:

```python
for id in sorted(agents):
    agent.step()
````

Each agent produces:

```
birth_event
death_event
```

Events are buffered.

No container mutation occurs in this phase.

---

### 2 — Death Set Construction

Agents whose energy is ≤ 0 become death candidates.

[
D = { i \mid E_i \le 0 }
]

---

### 3 — Birth Candidate Buffer

Agents may produce child seed sequences during evaluation.

Birth candidates are stored in evaluation order.

[
B = [b_1, b_2, \dots]
]

---

### 4 — Capacity Projection

Let:

* (N_t) = current population
* (D) = death set
* (N_{max}) = maximum allowed population

Effective population after deaths:

[
N_{eff} = N_t - |D|
]

Remaining capacity:

[
slots = N_{max} - N_{eff}
]

Births are truncated:

[
B_{commit} = B[:slots]
]

---

### 5 — Commit Phase

Structural mutation occurs only here.

Deaths applied:

[
A' = A_t \setminus D
]

Births applied:

[
A_{t+1} = A' \cup new_agents(B_{commit})
]

Agent IDs are assigned sequentially using:

```
next_agent_id
```

---

### 6 — World Tick Update

Finally:

```python
world.tick += 1
```

---

## Engine Invariants

The following invariants must always hold.

### Deterministic Ordering

Agents must always be evaluated in sorted ID order.

---

### No Mid-Loop Mutation

The agent container cannot be modified during evaluation.

All structural changes occur in the commit phase.

---

### Population Bound

[
|A_t| \le N_{max}
]

---

### ID Monotonicity

Agent IDs are never reused.

```
next_agent_id strictly increases
```

---

# 1.2 Agent — Local State and Dynamics

## Purpose

Agents define **local state and local update operators**.

They are responsible for:

* movement
* energy decay
* reproduction decision
* child seed creation
* death condition

Agents **never mutate global state directly**.

---

## Agent State

Each agent contains:

```
id
position
energy_level
alive
age (optional extension)
```

Lineage tracking:

```
agent_seed
agent_spawn_key
spawn_count
```

---

## RNG Streams

Each agent owns independent RNG streams:

```
move_rng
repro_rng
```

These streams are derived deterministically from the agent seed.

This guarantees **RNG stream independence**.

---

## Local State Representation

Agent state at time (t):

[
a_i(t) =
(x_i(t), E_i(t), alive_i(t), rng_i^m, rng_i^r, lineage_i)
]

---

## Local Update Operators

### Movement

Agent displacement is drawn from movement RNG.

[
\Delta_i(t) \in {-1, +1}
]

[
x_i(t+1) = wrap(x_i(t) + \Delta_i)
]

World topology is **toroidal**.

---

### Energy Dynamics

Movement costs energy.

[
E_i(t+1) = E_i(t) - c_{move}
]

Agents may also gain energy through harvesting
(in future resource subsystem).

---

### Death Condition

Agent dies when energy reaches zero.

[
alive_i(t+1) =
\begin{cases}
0 & E_i \le 0 \
1 & otherwise
\end{cases}
]

---

### Reproduction Decision

Reproduction occurs only if energy exceeds a threshold.

[
E_i \ge threshold
]

Probability:

[
reproduce \sim Bernoulli(p)
]

If reproduction occurs:

[
E_i \leftarrow E_i - reproduction_cost
]

---

### Child Seed Creation

Child agents derive RNG lineage deterministically.

Spawn key extension:

[
spawn_key_{child} =
spawn_key_{parent} \oplus spawn_count
]

Child seed:

[
SS_{child} =
SeedSequence(entropy, spawn_key_{child})
]

This guarantees **reproducible lineage**.

---

## Agent Invariants

* Reproduction cannot occur if the agent dies in the same tick
* RNG streams must never be shared between agents
* Movement RNG must remain independent of reproduction RNG

---

# 1.3 World — Global Environment Container

## Purpose

The World object stores global environment state.

Currently it contains:

```
tick
world_size
change_condition
```

---

## Mathematical Representation

[
W_t = (t, \theta_t)
]

Where:

* (t) is the tick counter
* (\theta_t) represents regime conditions

---

## Topology

The world uses **1-D toroidal topology**:

[
x_{t+1} = (x_t + \Delta) \mod L
]

Where:

* (L) is world size

---

## World Invariants

* Tick increments exactly once per `Engine.step()`
* World state must be included in canonical hashing

---

# 1.4 Configuration — Model Specification

## Purpose

Configuration defines all model parameters.

It represents the **model specification**, not simulation state.

---

## Parameter Categories

### Population Parameters

```
initial_agent_count
max_agent_count
```

---

### Energy Parameters

```
initial_energy_range
movement_cost
reproduction_threshold
reproduction_cost
```

---

### Reproduction Parameters

```
reproduction_probability
```

---

### World Parameters

```
world_size
```

---

## Mathematical Role

The transition operator depends on configuration:

[
S_{t+1} = T_{config}(S_t)
]

Configuration is **immutable during runtime**.

---

# LEVEL 2 — Determinism Infrastructure

This subsystem ensures **bit-level reproducibility**.

---

# 2.1 Canonical State Serialization

The engine state is serialized into deterministic byte format.

Schema includes:

```
schema_version
world.tick
agent_count
sorted agent states
```

Agent serialization includes:

```
id
position
energy
alive
```

Sorting ensures deterministic ordering.

---

# 2.2 State Hashing

State hashes are computed via:

[
H_t = SHA256(serialize(S_t))
]

Used for:

```
determinism testing
snapshot verification
trajectory equivalence
```

---

# 2.3 Snapshot / Clone System

Snapshots capture full reconstructible state.

[
snapshot(S_t) \rightarrow \hat{S}_t
]

[
restore(\hat{S}_t) \rightarrow S_t
]

Snapshot contents include:

```
world state
agent states
RNG bit states
seed lineage metadata
next_agent_id
config
```

---

# 2.4 RNG Reconstruction

RNGs are restored using stored bit generator states.

This guarantees identical random streams after cloning.

---

# 2.5 SeedSequence Lineage Tracking

Agent lineage is preserved by storing:

```
entropy
spawn_key
pool_size
spawn_count
```

Reconstruction rebuilds the original `SeedSequence`.

---

# LEVEL 3 — Experimental Infrastructure

---

# 3.1 Metrics System

Metrics observe system state **without modifying it**.

Recorded per tick:

```
population
births
deaths
death causes
```

Formally:

[
M_t = M(S_t)
]

---

# 3.2 Fingerprint Analytics

Simulation runs are summarized using **tail statistics**.

Fingerprint metrics include:

```
mean population
population variance
extinction events
birth/death ratios
cap hit rate
```

These provide **statistical summaries of system regimes**.

---

# 3.3 Batch Runner

The `BatchRunner` executes multiple deterministic runs.

Input:

```
regime config
master seed
number of runs
ticks
```

Process:

```
spawn run seeds
run engines
collect metrics
compute fingerprints
aggregate results
```

Output:

```
RegimeBatchResults
```

---

# 3.4 Validation Pipeline

Validation ensures system behavior matches expected regimes.

Current regimes:

```
stable
extinction
saturated
```

Each regime defines constraints such as:

```
population bounds
extinction rate
birth/death ratio
stability CV
```

---

# LEVEL 4 — Planned Future Subsystems

The following components will extend system complexity.

---

## Resource Field Dynamics

Introduce spatial resource distribution:

[
R_t(x)
]

Agents harvest resources from the environment.

---

## Multi-Dimensional Topology

Extend world topology to **2-D toroidal grid**.

[
(x,y) \rightarrow (x \pm 1, y \pm 1)
]

---

## Inter-Agent Interactions

Future dynamics include:

```
competition
predator-prey dynamics
territorial interactions
```

---

## Evolutionary Traits

Agents may inherit traits via deterministic lineage.

Example traits:

```
max_energy
movement efficiency
harvest efficiency
```

Traits will evolve through **bounded mutation**.

---

# Summary

The simulator implements a **deterministic stochastic dynamical system**.

Core design principles:

```
explicit entropy control
deterministic ordering
structural mutation isolation
canonical state hashing
reproducible lineage
```

This architecture allows the system to function as a **reproducible research framework for emergent multi-agent dynamics**.

```

---

If you want, I can also next show you a **clean documentation structure for the repo** (what files to create like `docs/core.md`, `docs/determinism.md`, `docs/validation.md`, etc.). That will make the repo look **very professional for beta0.2** and easy for other engineers to navigate.
```
