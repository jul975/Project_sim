# Agent Energy Dynamics and Ratio Calibration

## Overview

Agent behavior in the simulation is governed by a **dimensionless energy system**.
Instead of relying on arbitrary absolute values, biological dynamics are controlled through **dimensionless ratios** derived from a small set of energy parameters.

This approach provides several advantages:

* **Scale invariance** — parameters remain meaningful regardless of numeric magnitude.
* **Predictable regime tuning** — survival, reproduction, and lifecycle dynamics can be adjusted systematically.
* **Reproducible experimentation** — behavioral regimes can be defined and reproduced through configuration.

These ratios define the **metabolic constraints and reproductive dynamics** of agents within the ecosystem.

---

# 1. Core Energy Parameters

The agent energy model is defined by four primary parameters:

| Parameter                | Description                                                       |
| ------------------------ | ----------------------------------------------------------------- |
| `movement_cost`          | Energy spent per tick for movement                                |
| `max_harvest`            | Maximum energy an agent can harvest from the environment per tick |
| `reproduction_threshold` | Energy level required before reproduction becomes possible        |
| `reproduction_cost`      | Energy lost when reproduction occurs                              |

These parameters determine the **energy balance** governing agent survival and population growth.

---

# 2. Dimensionless Control Ratios

Three key ratios define the biological regime of the system.

## 2.1 Metabolic Pressure (α)

$$\alpha = \frac{movement\_cost}{max\_harvest}$$

This ratio represents the **baseline difficulty of survival**.

| α Range     | Interpretation                                                             |
| ----------- | -------------------------------------------------------------------------- |
| α → 1       | Movement nearly consumes all harvested energy. Survival becomes difficult. |
| α ≈ 0.6–0.9 | Balanced regime. Agents must actively gather resources to survive.         |
| α ≪ 1       | Energy surplus. Population growth may become explosive.                    |

Recommended operating range:

```
0.6 ≤ α ≤ 0.9
```

---

## 2.2 Reproductive Depletion (β)

$$\beta = \frac{reproduction\_cost}{reproduction\_threshold}$$

This ratio determines the **post-reproduction recovery cost**.

| β Value     | Interpretation                            |
| ----------- | ----------------------------------------- |
| β < 0.5     | Reproduction has little energetic impact  |
| β ≈ 0.8–1.0 | Reproduction nearly depletes agent energy |

Recommended range:

```
0.8 ≤ β ≤ 1.0
```

High β values introduce **natural spacing between births** by forcing agents to recover energy before reproducing again.

---

## 2.3 Energy Maturity Scale (γ)


$$\gamma = \frac{reproduction\_threshold}{movement\_cost}$$


This ratio determines the **energy accumulation period required for reproduction**.

| γ Value | Interpretation                              |
| ------- | ------------------------------------------- |
| γ small | Agents reach maturity quickly               |
| γ large | Long accumulation phase before reproduction |

Recommended range:

```
5 ≤ γ ≤ 15
```

Rule of thumb:

```
reproduction_threshold = γ × movement_cost
```

---

# 3. Example Calibration

The following example demonstrates a stable parameter configuration.

### Step 1 — Environmental Constraints

```
movement_cost = 2
max_harvest   = 3
```

Result:

```
α = 2 / 3 ≈ 0.67
```

This creates moderate metabolic pressure.

---

### Step 2 — Lifecycle Parameters

Select lifecycle ratio:

```
γ = 10
```

Derive reproduction threshold:

```
reproduction_threshold = 20
```

Set reproduction depletion:

```
β = 0.9
reproduction_cost = 18
```

---

### Step 3 — Energy Accumulation Time

If the average net surplus per tick is:

```
S ≈ 1 energy / tick
```

Then expected accumulation time is:

```
T_energy ≈ reproduction_threshold / S
         ≈ 20 ticks
```

This determines the **typical reproductive cycle length**.

---

# 4. Population Stability

Population stability can be approximated using the **basic reproduction number**.

$$R_0 = L \times R$$

Where:

| Variable | Meaning                             |
| -------- | ----------------------------------- |
| (L)      | Expected agent lifespan             |
| (R)      | Expected reproduction rate per tick |

Interpretation:

| R₀ Range   | System Behavior     |
| ---------- | ------------------- |
| R₀ < 1     | Population collapse |
| R₀ ≈ 1–1.5 | Stable population   |
| R₀ ≫ 1     | Exponential growth  |

This metric is useful when evaluating simulation regimes during batch experiments.

---

# 5. Calibration Workflow

Recommended tuning procedure:

1. **Fix environmental parameters**

   ```
   movement_cost
   max_harvest
   ```

2. **Run exploratory simulations** to measure average energy gain

3. **Set lifecycle scale**

   ```
   reproduction_threshold = γ × movement_cost
   ```

4. **Set reproduction cost**

   ```
   reproduction_cost ≈ 0.9 × reproduction_threshold
   ```

5. **Run simulations and measure**

   * lifespan distribution
   * reproduction frequency
   * population trajectory

6. **Adjust one ratio at a time**

Maintaining controlled adjustments preserves **experimental interpretability**.

---

# 6. Design Rationale

The ratio-based approach provides several structural advantages:

### Scale Independence

Agent dynamics remain stable across different absolute energy scales.

### Systematic Regime Definition

Different ecological regimes can be created by modifying a small set of ratios.

### Extensibility

Future model expansions (multi-species ecosystems, genetic variation, adaptive behavior) can build upon the same energy framework.

---

# 7. Future Extensions

Possible extensions to the current energy model include:

* **genetic variation in metabolic ratios**
* **age-dependent energy efficiency**
* **species-specific parameter sets**
* **adaptive reproduction strategies**
* **energy storage constraints**

These extensions allow the system to evolve toward **heterogeneous ecological dynamics** while maintaining the same underlying ratio framework.

---
