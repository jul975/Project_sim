# Validation Analytics Reference

## Purpose
This document defines the metrics and thresholds used by the regime validation system in `test/validation.py`.

It is the source-of-truth summary for:
- which analytics are checked
- the exact pass/fail thresholds per regime
- how aggregate validation is computed

## Validation Run Context
`run_validation_mode(args)` uses:
- regime config from `regimes/registry.py`
- `VALIDATION_DEFAULTS` from `execution/default.py`

Current defaults:
- `ticks = 300`
- `runs = 2`
- `batch_id = DEFAULT_MASTER_SEED`

## Metric Source
Validation is performed on `AggregatedFingerprint` (from `analytics/fingerprint.py`):

- `mean_population_over_runs`
- `std_mean_population_over_runs`
- `extinction_rate`
- `cap_hit_rate`
- `birth_death_ratio`
- `mean_time_cv_over_runs`

## Metric Definitions
### 1. `mean_population_over_runs`
Mean of per-run tail mean populations.

### 2. `std_mean_population_over_runs`
Standard deviation of per-run tail mean populations.

### 3. `extinction_rate`
Fraction of runs with at least one tail-window population value equal to zero.

### 4. `cap_hit_rate`
Mean across runs of per-run cap occupancy frequency in the tail window.

### 5. `birth_death_ratio`
$$
\text{birth\_death\_ratio} =
\begin{cases}
\frac{\overline{b}}{\overline{d}} & \text{if } \overline{d} > 0 \\
\infty & \text{if } \overline{d} = 0
\end{cases}
$$
where $\overline{b}$ and $\overline{d}$ are mean births/deaths per tick aggregated over runs.

### 6. `mean_time_cv_over_runs`
Mean coefficient of variation over runs:
$$
\text{CV} = \frac{\sigma_{\text{pop}}}{\mu_{\text{pop}}}
$$
(using tail-window population series per run).

## Shared Validation Gate (All Regimes)
Before regime-specific checks, validation enforces:
- every `AggregatedFingerprint` field must be finite (`np.isfinite`)

If any field is non-finite, validation fails immediately.

## Regime-Specific Thresholds

### Stable Regime (`validate_stable_regime`)
Pass conditions:
- `mean_population_over_runs > 0`
- `extinction_rate < 0.1`
- `cap_hit_rate < 0.2`
- `mean_time_cv_over_runs <= 0.2`
- `abs(birth_death_ratio - 1.0) <= 0.1`

Interpretation: sustained non-zero population, low extinction pressure, low cap saturation, moderate temporal stability, and near birth/death equilibrium.

### Extinction Regime (`validate_extinction_regime`)
Let `cap = next(iter(result.batch_metrics.values())).max_agent_count`.

Pass conditions:
- `extinction_rate >= 0.8`
- `mean_population_over_runs <= 0.1 * cap`
- every run fingerprint has `extinction_tick is not None`
- `cap_hit_rate <= 0.1`
- `birth_death_ratio < 1`

Interpretation: collapse-dominant dynamics with low cap pressure and death-dominated flow.

### Saturated Regime (`validate_saturated_regime`)
Let `cap = next(iter(result.batch_metrics.values())).max_agent_count`.

Pass conditions:
- `cap_hit_rate >= 0.8`
- `mean_population_over_runs >= 0.8 * cap`
- `mean_time_cv_over_runs <= 0.2`
- `extinction_rate <= 0.05`
- `abs(birth_death_ratio - 1.0) <= 0.1`

Interpretation: high occupancy near carrying capacity with low extinction and near-equilibrium turnover.

## Validator Mapping
`VALIDATORS` in `test/validation.py`:
- `"extinction" -> validate_extinction_regime`
- `"stable" -> validate_stable_regime`
- `"saturated" -> validate_saturated_regime`

## Notes
- Validation thresholds are hard-coded in `test/validation.py` and should be updated there first.
- This document should be updated whenever those constants or metric definitions change.
