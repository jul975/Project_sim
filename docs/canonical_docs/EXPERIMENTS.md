# Experiments and Regime Validation

## Purpose

This document defines the experiment-level validation system used to verify regime behavior.

It covers:

1. regime validation approach
2. metric definitions
3. regime classification logic

Source of truth:

- `tests/test_regime_validation.py`
- `engine_build/analytics/fingerprint.py`
- `engine_build/analytics/regime_summery.py`

## Current Status (Stage II)

**Actively Validated Regimes:**

- `stable` — Standard baseline for bounded population dynamics

**Regimes Under Evaluation:**

- `fragile` — Testing collapse dynamics and population stress responses
- `abundant` — Testing growth capacity and saturation effects

**Legacy Validation Tests:** Pending refactor to align with current regime set.

## 1. Regime Validation Framework

Validation evaluates batch-run aggregate fingerprints against regime-specific thresholds.

Execution path:

- `python -m engine_build.main validate --suite regime`
- config loaded from `engine_build/regimes/registry.get_regime_spec(regime)`
- run defaults from `engine_build/execution/default.VALIDATION_DEFAULTS`

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

The system uses post-hoc classification via `engine_build/analytics/regime_summery.py`:

```python
def classify_regime(summary: RegimeSummary) -> RegimeClass:
    # Returns one of: COLLAPSE, FRAGILE, STABLE, ABUNDANT, SATURATED, UNCLASSIFIED
```

This provides automatic behavioral classification independent of preset names.

### Stable Regime (Active Validation)

Test: `tests/test_regime_validation.py::test_stable_regime_validation`

Rules:

- `mean_population_over_runs > 0`
- `extinction_rate < 0.1`
- `cap_hit_rate < 0.2`
- `mean_time_cv_over_runs <= 0.2`
- `abs(birth_death_ratio - 1.0) <= 0.1`

Interpretation: bounded non-zero population with moderate stability and near birth/death balance.

### Fragile Regime (Emerging)

Target behavior:

- Higher extinction rate (triggered by tighter energy/resource constraints)
- Lower mean population
- Higher variability

### Abundant Regime (Emerging)

Target behavior:

- Near-capacity occupancy
- Low extinction rate
- Growth-toward-limit dynamics

## Notes

- Regime validation thresholds are hard-coded in `tests/test_regime_validation.py`
- Any threshold or metric logic change should update this document in the same changeset
- Legacy validation tests for "extinction" and "saturated" regimes are pending refactor to align with current regime preset names
- Post-hoc classification via `classify_regime()` provides continuous behavioral taxonomy independent of preset brittleness
