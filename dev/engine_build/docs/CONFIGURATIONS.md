# Configuration Reference

## Purpose
This document defines all configuration surfaces used by the ecosystem engine and experiment runner.

Determinism depends on:
- seed
- configuration values
- code version

## 1. Configuration Model
Core simulation settings are defined as immutable dataclasses in `core/config.py`:

```text
SimulationConfig
+- population_config: PopulationConfig
+- world_size: int
+- energy_init_range: tuple[int, int]
+- reproduction_probability: float
+- reproduction_probability_change_condition: float
+- resource_regen_rate: int
+- energy_config: EnergyConfig
+- max_resource_level: int

PopulationConfig
+- max_agent_count: int
+- initial_agent_count: int
+- max_age: int

EnergyConfig
+- max_harvest: int
+- ratios: EnergyRatios(alpha, beta, gamma)
```

All config dataclasses are `frozen=True`.

## 2. Default Values (Current)
### 2.1 `SimulationConfig`
| Field | Default | Meaning |
|---|---:|---|
| `world_size` | `200` | Number of cells in the 1D toroidal world |
| `energy_init_range` | `(30, 60)` | Spawn energy sampling range, high-exclusive |
| `reproduction_probability` | `0.25` | Reproduction probability in normal condition |
| `reproduction_probability_change_condition` | `0.50` | Reproduction probability when `change_condition=True` |
| `resource_regen_rate` | `2` | Resource regeneration per tick |
| `max_resource_level` | `80` | Upper bound used for fertility initialization (`[0, 79]`) |

### 2.2 `PopulationConfig`
| Field | Default | Meaning |
|---|---:|---|
| `initial_agent_count` | `10` | Population at tick 0 |
| `max_agent_count` | `1000` | Hard population cap |
| `max_age` | `200` | Age threshold that marks agents dead |

### 2.3 `EnergyConfig` / `EnergyRatios`
| Field | Default | Meaning |
|---|---:|---|
| `max_harvest` | `5` | Max resources harvestable per agent per tick |
| `alpha` | `0.6` | Metabolic pressure |
| `beta` | `0.8` | Reproductive depletion |
| `gamma` | `10.0` | Energy maturity scale |

## 3. Derived Runtime Energy Parameters
At engine construction, `EnergyParams` are derived from ratios:

$$
\begin{aligned}
\text{movement\_cost} &= \text{int}(\alpha \cdot \text{max\_harvest}) \\
\text{reproduction\_threshold} &= \text{int}(\gamma \cdot \text{movement\_cost}) \\
\text{reproduction\_cost} &= \text{int}(\beta \cdot \text{reproduction\_threshold})
\end{aligned}
$$

`int(...)` follows Python truncation behavior.

## 4. Regime Presets
Defined in `regimes/registry.py` as `(alpha, beta, gamma)`:

| Regime | alpha | beta | gamma |
|---|---:|---:|---:|
| `extinction` | `1.2` | `1.0` | `5` |
| `stable` | `0.6` | `0.8` | `10` |
| `saturated` | `0.4` | `0.6` | `6` |

`get_regime_config(regime)` builds a `SimulationConfig` by applying these ratios and keeping other defaults.

## 5. Execution-Level Parameters (Runner/CLI)
These values are not part of `SimulationConfig`, but control experiments and validation.

### 5.1 Seed and batch defaults
From `execution/default.py`:
- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 300, "runs": 2}`

### 5.2 CLI overrides
`main.py` supports:
- `--mode {experiment,validation}`
- `--regime {extinction,stable,saturated,all}`
- `--seed` (master seed override)
- `--runs` and `--ticks` (experiment mode)
- `--plot` (experiment mode)

In validation mode, canonical validation defaults are used.

## 6. Determinism Notes
For reproducible runs:
- keep config immutable during execution
- use explicit seed input
- avoid mid-run parameter mutation
- keep code version fixed

The engine’s canonical state hash and RNG architecture assume this contract.

## 7. Minimal Example
```python
from engine_build.core.config import SimulationConfig, EnergyConfig, EnergyRatios

cfg = SimulationConfig(
    energy_config=EnergyConfig(
        ratios=EnergyRatios(alpha=0.6, beta=0.8, gamma=10.0)
    )
)
```

For predefined regimes, prefer `get_regime_config("stable")`.
