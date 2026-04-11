# Configuration

## Status

This document describes the live configuration model on March 23, 2026.

The authoritative path is:

```text
RegimeSpec
-> compile_regime()
-> CompiledRegime
-> Engine / World / Agent / Runner
```

Configuration lives in `FestinaLente/regimes/`. There is no active `core/config.py` runtime layer.

## Authoring Layer: `RegimeSpec`

`FestinaLente/regimes/spec.py` defines the human-authored inputs.

```python
RegimeSpec(
    energy_spec=EnergySpec(...),
    resources_spec=ResourceSpec(...),
    landscape_spec=LandscapeSpec(...),
    reproduction_spec=ReproductionSpec(...),
    population_spec=PopulationSpec(...),
    max_energy=100,
    max_resource_level=80,
    world_size=400,
)
```

Subsystem dataclasses:

- `EnergySpec(beta, gamma, harvest_fraction, alpha=0.6, initial_energy_low_ratio=0.3, initial_energy_high_ratio=0.6)`
- `ReproductionSpec(probability=0.25, probability_change_condition=0.5)`
- `ResourceSpec(regen_fraction)`
- `LandscapeSpec(correlation, contrast, floor)`
- `PopulationSpec(max_agent_count, initial_agent_count, max_age)`

All of these dataclasses are currently frozen.

## Runtime Layer: `CompiledRegime`

`FestinaLente/regimes/compiled.py` defines the compiled runtime shape:

- `EnergyParams`
- `ReproductionParams`
- `ResourceParams`
- `PopulationParams`
- `WorldParams`
- `LandscapeParams`

## Compilation Rules

`FestinaLente/regimes/compiler.py` is the single place where the ratio math is compiled into runtime integers.

For anchors:

- `E_max = max_energy`
- `R_max = max_resource_level`
- `W = world_size`

Current rules:

| Runtime field | Current rule |
|---|---|
| `max_harvest` | `min(max_energy, max(1, round(harvest_fraction * max_resource_level)))` |
| `movement_cost` | `min(max_energy, max_harvest, max(1, round(alpha * max_harvest)))` |
| `reproduction_threshold` | `min(max_energy, max(max(1, round(gamma * movement_cost)), movement_cost))` |
| `reproduction_cost` | `min(reproduction_threshold, max(1, round(beta * reproduction_threshold)))` |
| `energy_init_range` | `(max(1, round(low_ratio * max_energy)), max(low, round(high_ratio * max_energy)))` |
| `regen_rate` | `max(1, round(regen_fraction * max_resource_level))` |
| `world_width` / `world_height` | `round(sqrt(world_size))` |

Important implementation notes:

- `round()` is Python's built-in rounding, so midpoint values use banker's rounding
- `world_size` is treated as a square-world anchor, not a strict area invariant
- non-perfect squares are rounded to a side length; the realized world area is then `side * side`
- `max_energy` is an anchor and initialization bound, not a runtime clamp on `energy_level`

## Shared Baseline Defaults

The checked-in regimes share these defaults unless overridden:

| Field | Value |
|---|---:|
| `max_energy` | `100` |
| `max_resource_level` | `80` |
| `world_size` | `400` |
| `alpha` | `0.6` |
| `initial_energy_low_ratio` | `0.3` |
| `initial_energy_high_ratio` | `0.6` |
| `probability` | `0.25` |
| `probability_change_condition` | `0.5` |
| `correlation` | `0.055` |
| `contrast` | `1.0` |
| `floor` | `0.0` |
| `max_agent_count` | `1000` |
| `initial_agent_count` | `10` |
| `max_age` | `100` |

With the current defaults, `world_size=400` compiles to a `20 x 20` toroidal world.

## Named Regimes

The live registry defines six regimes:

| Regime | Compiled highlights | Intent |
|---|---|---|
| `stable` | `regen_rate=8`, `max_harvest=28`, `movement_cost=17`, `threshold=100`, `repro_cost=80` | bounded baseline |
| `fragile` | `regen_rate=8`, `max_harvest=28`, `movement_cost=17`, `threshold=100`, `repro_cost=100` | expensive reproduction stress case |
| `extinction` | `regen_rate=2`, `max_harvest=32`, `movement_cost=19`, `threshold=100`, `repro_cost=100` | low-regeneration failure pressure |
| `collapse` | `regen_rate=2`, `max_harvest=28`, `movement_cost=17`, `threshold=42`, `repro_cost=42` | lower-threshold collapse case |
| `saturated` | `regen_rate=8`, `max_harvest=4`, `movement_cost=2`, `threshold=2`, `repro_cost=2` | high-occupancy / cap-pressure case |
| `abundant` | `regen_rate=10`, `max_harvest=28`, `movement_cost=17`, `threshold=17`, `repro_cost=2` | permissive growth regime |

## Landscape Behavior

Landscape generation currently uses only the correlation field directly.

`FestinaLente/core/world.py` computes:

```text
raw_kernel = correlation * world_width
kernel_size = max(3, round(raw_kernel))
if kernel_size is even: kernel_size += 1
```

The world then smooths random noise across the torus and scales the result by `max_resource_level`.

Current limitation:

- `contrast` and `floor` are preserved in config objects but are not applied during fertility generation

## Runtime Defaults

Shared defaults in `FestinaLente/execution/default.py` are:

- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 1000, "runs": 10}`

That validation default changed from earlier March drafts. Any documentation still referring to `300` ticks and `2` runs is stale.

## CLI Surface

Current main-path commands:

```bash
python -m FestinaLente.main experiment --regime stable
python -m FestinaLente.main experiment --regime stable --seed 42 --runs 5 --ticks 500
python -m FestinaLente.main verify --suite determinism
python -m FestinaLente.main validate --suite contracts
```

Experiment request flags also include:

- `--plot`
- `--plot-dev`
- `--perf-flag`
- `--world-frame-flag`
- `--tail-fraction` (default: 0.25, specifies fraction of run used for final metrics analysis)

## Recommended Usage

Canonical path from name to runtime config:

```python
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.compiler import compile_regime

regime = compile_regime(get_regime_spec("stable"))
```

That is the current baseline configuration flow for experiments, verification, and validation.
