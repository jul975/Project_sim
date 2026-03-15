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
Source: `engine_build/core/config.py`

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

## 2. Current Defaults
### 2.1 `SimulationConfig`
| Field | Default | Description |
|---|---:|---|
| `world_size` | `200` | Number of cells in the 1D toroidal world |
| `energy_init_range` | `(30, 60)` | Initial energy sampling range (high-exclusive) |
| `reproduction_probability` | `0.25` | Reproduction probability (`change_condition=False`) |
| `reproduction_probability_change_condition` | `0.50` | Reproduction probability (`change_condition=True`) |
| `resource_regen_rate` | `2` | Resources regenerated per tick |
| `max_resource_level` | `80` | Fertility initialization upper bound (`0..79`) |

### 2.2 `PopulationConfig`
| Field | Default | Description |
|---|---:|---|
| `initial_agent_count` | `10` | Initial population size |
| `max_agent_count` | `1000` | Hard population cap |
| `max_age` | `200` | Age threshold for old-age death marking |

### 2.3 `EnergyConfig` / `EnergyRatios`
| Field | Default | Description |
|---|---:|---|
| `max_harvest` | `5` | Max harvestable resources per tick |
| `alpha` | `0.6` | Metabolic pressure |
| `beta` | `0.8` | Reproductive depletion |
| `gamma` | `10.0` | Energy maturity scale |

## 3. Derived Runtime Energy Parameters
At engine initialization, `EnergyParams` are computed as:

$$
\begin{aligned}
\text{movement\_cost} &= \text{int}(\alpha \cdot \text{max\_harvest}) \\
\text{reproduction\_threshold} &= \text{int}(\gamma \cdot \text{movement\_cost}) \\
\text{reproduction\_cost} &= \text{int}(\beta \cdot \text{reproduction\_threshold})
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
