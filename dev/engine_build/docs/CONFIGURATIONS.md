# Configuration Reference

This document describes the configurable parameters controlling the behavior of the **Ecosystem Emergent Behavior Simulator**.

The simulator is designed so that **all system behavior derives from explicit configuration**, ensuring reproducibility and transparency.

---

# Configuration Philosophy

The configuration system follows three principles:

1. **Explicit parameters**  
   All ecological dynamics derive from configuration values.

2. **Dimensionless ratios**  
   Core energy dynamics are controlled by ratios instead of absolute constants.

3. **Reproducibility**  
   A simulation is uniquely determined by:


        seed + configuration + code version


---

# Core Configuration Groups

Configuration parameters are grouped into four logical categories:

```bash
Simulation
World
Population
Energy Dynamics
```


---

# 1. Simulation Parameters

General parameters controlling experiment execution.

| Parameter | Description |
|----------|-------------|
| `seed` | Master random seed used to initialize the simulation |
| `ticks` | Number of simulation steps to execute |
| `runs` | Number of runs in a batch experiment |
| `mode` | Execution mode (`experiment` or `validation`) |

The seed initializes the **master SeedSequence**, from which all RNG streams derive.

---

# 2. World Parameters

Define the spatial environment and resource dynamics.

| Parameter | Description |
|----------|-------------|
| `world_size` | Number of spatial cells in the environment |
| `regen_rate` | Resource regeneration per tick |
| `max_harvest` | Maximum resources an agent can harvest per tick |
| `fertility_range` | Range used to generate the fertility field |

The world maintains two arrays:


fertility $x$ → maximum resource capacity
resources $x$ → current resource level


Resource update rule:


$$resources[x] = min(fertility[x], resources[x] + regen_rate)$$


---

# 3. Population Parameters

Define limits on population size and agent lifecycle.

| Parameter | Description |
|----------|-------------|
| `initial_agent_count` | Number of agents at simulation start |
| `max_agent_count` | Maximum allowed population |
| `spawn_energy_range` | Energy range for newly created agents |

Population cap rule:


population ≤ max_agent_count


If reproduction would exceed the cap, spawning is suppressed.

---

# 4. Energy Dynamics

Energy dynamics govern agent survival and reproduction.

Energy evolves according to:


$$ E(t+1) = E(t) - movement_cost + harvest $$


Where harvest depends on resource availability.

---

# 4.1 Dimensionless Energy Ratios

The engine uses **dimensionless ratios** to derive energy parameters.

| Symbol | Name | Meaning |
|------|------|---------|
| α | Metabolic pressure | Energy cost of movement |
| β | Reproductive depletion | Energy lost during reproduction |
| γ | Energy maturity scale | Energy required before reproduction |

Derived parameters:


$$movement\_cost = α * max\_harvest$$
$$reproduction\_threshold = γ * movement\_cost$$
$$reproduction\_cost = β * reproduction\_threshold$$


Using ratios instead of absolute constants allows ecological regimes to be tuned while maintaining stability.

---

# 5. Ecological Regimes

The simulator includes predefined **regime configurations**.

| Regime | Description |
|------|-------------|
| `extinction` | population collapses |
| `stable` | bounded population equilibrium |
| `saturated` | population approaches capacity ceiling |

Regimes modify parameters such as:

- regeneration rate
- energy ratios
- harvest limits

These presets allow consistent experimentation across known ecological dynamics.

---

# 6. Deterministic Constraints

The configuration system must preserve the engine's determinism guarantees.

Key rules:

- configuration objects must be **immutable during a run**
- parameters must not change mid-simulation
- random seeds must be defined explicitly

Violation of these rules can break reproducibility.

---

# 7. Example Configuration

Example parameter set for a stable regime:

```python
world_size = 200
initial_agent_count = 10
max_agent_count = 1000

regen_rate = 2
max_harvest = 5

alpha = 0.8
beta = 0.6
gamma = 6.0
```
These values create conditions where:

- agents can sustainably harvest resources

- reproduction occurs periodically

- population stabilizes near equilibrium.

# 8. Adding New Parameters

When adding new configuration values:

- Place them in the appropriate category

- Document them in this file

- Ensure they do not violate determinism guarantees

- Update regime presets if necessary

Configuration changes should remain explicit and reproducible.

---

# Summary

All simulation behavior derives from configuration parameters governing:


    environment
    population limits
    energy dynamics
    random seed initialization

This design ensures the simulator remains:

- reproducible

- transparent

- experimentally controllable