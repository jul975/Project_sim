# Configuration Reference

## Purpose
This document defines the configuration model used by the ecosystem engine and experiment runner.

Deterministic behavior is defined by:
- seed
- configuration
- code version

## Configuration Principles
- Explicit parameters: ecological behavior is driven by declared config values.
- Immutable runtime config: simulation config objects are frozen dataclasses.
- Ratio-based energy control: runtime energy costs are derived from dimensionless ratios.

## 1. Configuration Model
Source: `engine_build/regimes/spec.py` and `engine_build/regimes/compiled.py`

```text
RegimeSpec (human-authored)
├─ EnergySpec(beta, gamma, harvest_fraction)
├─ ReproductionSpec(probability, probability_change_condition)
├─ ResourceSpec(regen_fraction)
├─ LandscapeSpec(correlation, contrast, floor)
└─ PopulationSpec(max_agent_count, initial_agent_count, max_age)

CompiledRegime (runtime, computed)
├─ EnergyParams(movement_cost, reproduction_threshold, reproduction_cost, max_harvest, max_energy)
├─ ReproductionParams(probability, probability_change_condition)
├─ ResourceParams(max_resource_level, regen_rate)
├─ LandscapeParams(correlation, contrast, floor)
├─ PopulationParams(max_agent_count, initial_agent_count, max_age)
└─ WorldParams(world_width, world_height)
```

## 2. Current Defaults
### 2.1 World Parameters (2D Grid)
| Field | Default | Description |
|---|---:|---|
| `world_width` | `20` | Number of cells in X dimension |
| `world_height` | `20` | Number of cells in Y dimension |
| `world_size` | `400` | Total cells (width × height) |

Agents move on a 2D toroidal grid with wrapping boundaries:
```text
(x + dx) mod world_width
(y + dy) mod world_height
```

### 2.2 `PopulationSpec`
| Field | Default | Description |
|---|---:|---|
| `initial_agent_count` | `10` | Initial population size |
| `max_agent_count` | `1000` | Hard population cap |
| `max_age` | `100` | Age threshold for old-age death marking |

### 2.3 `EnergySpec` and Derived `EnergyParams`
| Field | Default | Description |
|---|---:|---|
| `beta` | `0.8` | Reproductive cost multiplier |
| `gamma` | `10` | Energy maturity scale factor |
| `harvest_fraction` | `0.35` | Fraction of fertility harvestable per tick |
| *derived:* `movement_cost` | varies | int(beta × max_harvest) |
| *derived:* `reproduction_threshold` | varies | int(gamma × movement_cost) |
| *derived:* `reproduction_cost` | varies | int(beta × reproduction_threshold) |

### 2.4 Resource and Landscape Parameters
| Field | Default | Description |
|---|---:|---|
| `regen_fraction` | `0.1` | Fraction of fertility regenerated per tick |
| `correlation` | `0.055` | Landscape correlation radius (as fraction of world_width) |
| `contrast` | `1.0` | Fertility contrast multiplier |
| `floor` | `0.0` | Minimum fertility level |

## 3. Derived Runtime Energy Parameters
At engine compilation, landscape is generated and energy parameters computed as:

$$
\begin{aligned}
\text{movement\_cost} &= \text{int}(\text{beta} \cdot \text{max\_harvest}) \\
\text{reproduction\_threshold} &= \text{int}(\text{gamma} \cdot \text{movement\_cost}) \\
\text{reproduction\_cost} &= \text{int}(\text{beta} \cdot \text{reproduction\_threshold})
\end{aligned}
$$

`int(...)` uses Python truncation.

## 4. Regime Presets
Source: `engine_build/regimes/registry.py`

| Regime | Description | Use Case |
|---|---|---|
| `stable` | Bounded population, low extinction pressure | Default baseline for experiments |
| `test_stable` | Tighter energy budget variant of stable | Rapid validation checks |
| `fragile` | Tight energy constraints, high collapse risk | Testing robustness under stress |
| `abundant` | High resources, relaxed energy requirements | Testing growth capacity dynamics |

Each regime is defined via `RegimeSpec` with configurable energy, reproduction, resource, landscape, and population parameters.

Reference: Energy parameters (beta, gamma, harvest_fraction) determine agent energy dynamics. Resource parameters (regen_fraction) control regeneration rates. See [engine_build/regimes/compiler.py](../../engine_build/regimes/compiler.py) for compilation logic.

## 5. Execution-Level Controls
These are runtime controls for batch execution (not fields of `SimulationConfig`).

Source: `engine_build/execution/default.py`
- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 300, "runs": 2}`

CLI-level overrides in `engine_build/main.py`:
- `experiment {regime}` — Run regime experiments
- `validate {--suite}` — Run validation suites
- `fertility {--seed}` — Run fertility exploration
- Regime choices: `stable`, `test_stable`, `fragile`, `abundant`
- `--seed`, `--runs`, `--ticks` — Override defaults

## 6. Determinism Constraints
For reproducible runs:
- do not mutate config during a run
- use explicit seed values
- keep code/runtime environment stable

## 7. Minimal Usage Example
```python
from engine_build.core.config import SimulationConfig, EnergyConfig, EnergyRatios

cfg = SimulationConfig(
    energy_config=EnergyConfig(
        ratios=EnergyRatios(alpha=0.6, beta=0.8, gamma=10.0)
    )
)
```

For canonical presets, use `get_regime_config("stable")`.
