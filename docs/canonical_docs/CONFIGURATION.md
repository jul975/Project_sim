# Configuration

## Purpose

This document describes the current configuration model used by the engine, runner, and CLI.

The authoritative pipeline is:

```text
RegimeSpec -> compile_regime() -> CompiledRegime -> Engine / World / Agent
```

Configuration lives in `engine_build/regimes/`. There is no active legacy `core/config.py` runtime layer.

## Configuration Model

### Authoring layer: `RegimeSpec`

`RegimeSpec` is the human-authored input. It contains:

- `energy_spec: EnergySpec`
- `resources_spec: ResourceSpec`
- `landscape_spec: LandscapeSpec`
- `reproduction_spec: ReproductionSpec`
- `population_spec: PopulationSpec`
- `max_energy: int = 100`
- `max_resource_level: int = 80`
- `world_size: int = 400`

Subsystem fields:

- `EnergySpec(beta, gamma, harvest_fraction, alpha=0.6, initial_energy_low_ratio=0.3, initial_energy_high_ratio=0.6)`
- `ReproductionSpec(probability=0.25, probability_change_condition=0.5)`
- `ResourceSpec(regen_fraction)`
- `LandscapeSpec(correlation, contrast, floor)`
- `PopulationSpec(max_agent_count, initial_agent_count, max_age)`

All current spec and compiled config dataclasses are frozen.

### Runtime layer: `CompiledRegime`

`compile_regime()` converts a `RegimeSpec` into runtime parameters:

- `EnergyParams(max_energy, energy_init_range, max_harvest, movement_cost, reproduction_threshold, reproduction_cost)`
- `ResourceParams(max_resource_level, regen_rate)`
- `ReproductionParams(probability, probability_change_condition)`
- `PopulationParams(max_agent_count, initial_agent_count, max_age)`
- `WorldParams(world_width, world_height)`
- `LandscapeParams(correlation, contrast, floor)`

## Compilation Rules

The compiler in `engine_build/regimes/compiler.py` applies the following rules:

| Runtime field | Current rule |
|---|---|
| `max_harvest` | `min(max_energy, max(1, round(harvest_fraction * max_resource_level)))` |
| `movement_cost` | `min(max_energy, max_harvest, max(1, round(alpha * max_harvest)))` |
| `reproduction_threshold` | `min(max_energy, max(movement_cost, round(gamma * movement_cost)))` |
| `reproduction_cost` | `min(reproduction_threshold, max(1, round(beta * reproduction_threshold)))` |
| `energy_init_range` | `(max(1, round(low_ratio * max_energy)), max(low, round(high_ratio * max_energy)))` |
| `regen_rate` | `max(1, round(regen_fraction * max_resource_level))` |
| `world_width` / `world_height` | `round(sqrt(world_size))` |

Important implementation notes:

- `max_energy` is a compilation anchor and initialization bound. The runtime does not currently clamp `agent.energy_level` to it.
- `world_size` is treated as a square-world anchor. Non-perfect squares are rounded, not rejected.

## Current Shared Defaults

These values are shared by the checked-in named regimes unless a regime overrides them:

| Field | Current value | Notes |
|---|---:|---|
| `max_energy` | `100` | Energy-system anchor |
| `max_resource_level` | `80` | Resource-system anchor |
| `world_size` | `400` | Compiles to a `20 x 20` toroidal grid |
| `alpha` | `0.6` | Movement-cost ratio |
| `initial_energy_low_ratio` | `0.3` | Lower bound for initial energy draw |
| `initial_energy_high_ratio` | `0.6` | Upper bound for initial energy draw |
| `probability` | `0.25` | Default reproduction probability |
| `probability_change_condition` | `0.5` | Alternate reproduction probability used by the RNG-isolation check |
| `correlation` | `0.055` | Used to derive fertility smoothing kernel size |
| `contrast` | `1.0` | Present in config, not currently applied in world generation |
| `floor` | `0.0` | Present in config, not currently applied in world generation |
| `max_agent_count` | `1000` | Hard population cap |
| `initial_agent_count` | `10` | Founder count |
| `max_age` | `100` | Age-based death threshold |

## Stable Baseline

The default baseline regime is `stable`. Its compiled runtime values are:

| Field | Value |
|---|---:|
| `world_width` | `20` |
| `world_height` | `20` |
| `energy_init_range` | `(30, 60)` |
| `max_harvest` | `28` |
| `movement_cost` | `17` |
| `reproduction_threshold` | `100` |
| `reproduction_cost` | `80` |
| `regen_rate` | `8` |

## Named Regimes

The current registry defines six named regimes:

| Regime | Key compiled values | Intent |
|---|---|---|
| `stable` | `regen_rate=8`, `threshold=100`, `repro_cost=80` | Baseline bounded regime |
| `fragile` | `regen_rate=8`, `threshold=100`, `repro_cost=100` | Reproduction becomes maximally expensive |
| `extinction` | `regen_rate=2`, `threshold=85`, `repro_cost=85` | Low regeneration with costly reproduction |
| `collapse` | `regen_rate=2`, `threshold=42`, `repro_cost=42` | Low regeneration with earlier but still fully draining reproduction |
| `saturated` | `max_harvest=4`, `movement_cost=2`, `threshold=2`, `repro_cost=2` | Extremely cheap survival and reproduction pressure toward capacity |
| `abundant` | `regen_rate=10`, `threshold=17`, `repro_cost=2` | Easy reproduction and faster regrowth |

## Landscape Behavior

Landscape generation currently uses:

```text
kernel_size = max(3, round(correlation * world_width))
```

If the kernel is even, it is incremented to keep it odd. The world then smooths raw noise on a toroidal grid.

Current limitation: `contrast` and `floor` are carried through the config layer but are not yet used by `World._generate_fertility_fields()`.

## Runtime Controls

Execution defaults in `engine_build/execution/default.py` are:

- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 300, "runs": 2}`

Current CLI examples:

```bash
python -m engine_build.main experiment --regime stable
python -m engine_build.main experiment --regime stable --seed 42 --runs 5 --ticks 500
python -m engine_build.main verify --suite determinism
```

## Recommended Usage

For normal runs and tests:

```python
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime

regime = compile_regime(get_regime_spec("stable"))
```

That is the current canonical path from named regime to runtime configuration.
