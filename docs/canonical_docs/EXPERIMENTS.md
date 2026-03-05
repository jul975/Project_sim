# Experiments and Regime Validation

## Purpose
This document defines the experiment-level validation system used to verify regime behavior.

It covers:
1. regime validation
2. metric definitions
3. regime classification logic

Source of truth:
- `engine_build/test/validation.py`
- `engine_build/analytics/fingerprint.py`

## 1. Regime Validation
Validation evaluates batch-run aggregate fingerprints against regime-specific thresholds.

Execution path:
- `run_validation_mode(args)`
- config loaded from `get_regime_config(args.regime)`
- run defaults from `VALIDATION_DEFAULTS`

Current validation defaults:
- `ticks = 300`
- `runs = 2`
- `batch_id = DEFAULT_MASTER_SEED`

Shared validation gate (all regimes):
- every `AggregatedFingerprint` field must be finite (`np.isfinite`)

If this gate fails, regime validation fails immediately.

## 2. Metric Definitions
Validation uses `AggregatedFingerprint` fields:

- `mean_population_over_runs`
- `std_mean_population_over_runs`
- `extinction_rate`
- `cap_hit_rate`
- `birth_death_ratio`
- `mean_time_cv_over_runs`

Definitions:

### `mean_population_over_runs`
Mean of per-run tail-window population means.

### `std_mean_population_over_runs`
Standard deviation of per-run tail-window population means.

### `extinction_rate`
Fraction of runs where `extinction_tick is not None`.

### `cap_hit_rate`
Mean across runs of per-run frequency where population equals `max_agent_count` in the tail window.

### `birth_death_ratio`
$$
\text{birth\_death\_ratio} =
\begin{cases}
\frac{\overline{b}}{\overline{d}} & \text{if } \overline{d} > 0 \\
\infty & \text{if } \overline{d} = 0
\end{cases}
$$
where $\overline{b}$ and $\overline{d}$ are aggregated mean births/deaths per tick.

### `mean_time_cv_over_runs`
Mean coefficient of variation (CV) over runs:
$$
\text{CV} = \frac{\sigma_{\text{pop}}}{\mu_{\text{pop}}}
$$
using each run's tail-window population series.

## 3. Regime Classification Logic
Validation is rule-based via `VALIDATORS`:

- `"extinction" -> validate_extinction_regime`
- `"stable" -> validate_stable_regime`
- `"saturated" -> validate_saturated_regime`

A run is classified as a valid regime only if **all** regime-specific constraints pass.

### Stable regime rules
- `mean_population_over_runs > 0`
- `extinction_rate < 0.1`
- `cap_hit_rate < 0.2`
- `mean_time_cv_over_runs <= 0.2`
- `abs(birth_death_ratio - 1.0) <= 0.1`

Interpretation: bounded non-zero population with moderate stability and near birth/death balance.

### Extinction regime rules
Let `cap = next(iter(result.batch_metrics.values())).max_agent_count`.

- `extinction_rate >= 0.8`
- `mean_population_over_runs <= 0.1 * cap`
- every run must have `extinction_tick is not None`
- `cap_hit_rate <= 0.1`
- `birth_death_ratio < 1`

Interpretation: collapse-dominant dynamics with sustained death pressure.

### Saturated regime rules
Let `cap = next(iter(result.batch_metrics.values())).max_agent_count`.

- `cap_hit_rate >= 0.8`
- `mean_population_over_runs >= 0.8 * cap`
- `mean_time_cv_over_runs <= 0.2`
- `extinction_rate <= 0.05`
- `abs(birth_death_ratio - 1.0) <= 0.1`

Interpretation: high-cap occupancy with low extinction and near turnover equilibrium.

## Regime Output Examples
These plots illustrate typical outputs for the three validated regimes.

### Stable Regime
![Stable Regime](../images/regime_stable.png)

### Extinction Regime
![Extinction Regime](../images/regime_extinction.png)

### Saturated Regime
![Saturated Regime](../images/regime_saturated.png)

## Notes
- Thresholds are hard-coded in `engine_build/test/validation.py`.
- Any threshold or metric logic change should update this document in the same change set.
