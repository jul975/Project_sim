# Experiments, Analytics, and Validation

## Status

This document describes the live experiment and validation surface on March 23, 2026.

Current project posture:

- pre-Stage III / pre-`v0.3` freeze candidate
- experiment lane is usable and is the main runtime path
- verification and validation are both wired through the CLI and pytest
- full local test run in the project virtual environment passed on March 23, 2026: `31 passed`

## 1. Experiment Lane

The canonical experiment entrypoint is:

```bash
python -m engine_build.main experiment --regime <name>
```

Runtime path:

```text
CLI / menu
-> ExperimentRequest
-> dispatch()
-> run_experiment_mode()
-> get_regime_spec()
-> compile_regime()
-> Runner.run_regime_batch()
-> analyze_batch()
-> summarise_regime()
-> classify_regime()
-> report / optional plots
```

## 2. Current CLI Surface

`experiment` currently supports:

- `--regime`
- `--runs`
- `--ticks`
- `--seed`
- `--plot`
- `--plot-dev`
- `--perf-flag`
- `--world-frame-flag`
- `--tail-fraction` (fraction of run used for final metrics; default: 0.25)

All flags are properly wired end-to-end through [ExecutionContext](execution_model/execution_context.py) → [execute.py](app/execution/execute_service/execute.py) → [AnalysisContext](analytics/contracts/analysis_context.py).

## 3. Defaults

From [engine_build/app/execution_model/default.py](engine_build/app/execution_model/default.py):

- `DEFAULT_MASTER_SEED = 20250302`
- `EXPERIMENT_DEFAULTS = {"ticks": 1000, "runs": 10}`
- `VALIDATION_DEFAULTS = {"ticks": 1000, "runs": 10}`

Validation and experiment defaults are now aligned. Older docs referring to `300` ticks or `2` runs are stale.

## 4. Named Regimes

The live regime registry is:

| Regime | Current role |
|---|---|
| `stable` | bounded baseline |
| `fragile` | stressed but surviving case |
| `extinction` | high-failure regime |
| `collapse` | low-regeneration collapse regime |
| `saturated` | cap-pressure / dense occupancy regime |
| `abundant` | permissive growth regime |

## 5. Per-Run Metrics

`SimulationMetrics` records:

- `population`
- `births`
- `deaths`
- death causes:
  - `age_deaths`
  - `metabolic_deaths`
  - `post_harvest_starvation`
  - `post_reproduction_death`
- optional `mean_energy`
- optional `world_view`

`mean_energy` and `world_view` are only populated when world-frame capture is enabled.

## 6. Fingerprints

### Run-level fingerprint

`engine_build/analytics/fingerprint.py::compute_fingerprint()` produces:

- `min_population`
- `max_population`
- `final_population`
- `mean_population`
- `std_population`
- `range_population`
- `cap_hit_rate`
- `extinction_tick`
- `mean_births_per_tick`
- `mean_deaths_per_tick`
- `mean_deaths_cause_tail`
- `proportion_deaths_cause_tail`
- `near_cap_rate`
- `low_population_rate`

### Batch aggregate fingerprint

`get_aggregate_fingerprints()` produces:

- `final_populations`
- `mean_population_over_runs`
- `std_mean_population_over_runs`
- `extinction_rate`
- `cap_hit_rate`
- `birth_death_ratio`
- `mean_time_cv_over_runs`
- `batch_near_cap_rate`
- `batch_near_low_population_rate`

The tail window is currently the last `25%` of the run unless `AnalysisConfig` is built manually elsewhere.

## 7. Regime Summary and Classification

The experiment lane converts aggregate fingerprints into a `RegimeSummary`, then classifies them with `classify_regime()`.

Current classification logic:

```text
stable_like = (time_cv <= 0.10) and (0.95 <= birth_death_ratio <= 1.05)

if extinction_rate >= 0.95: EXTINCTION
elif extinction_rate >= 0.50: COLLAPSE
elif low_population_rate >= 0.80 and birth_death_ratio < 0.95: COLLAPSE
elif cap_hit_rate >= 0.20 or near_cap_rate >= 0.30: SATURATED
elif low_population_rate >= 0.20: FRAGILE
elif stable_like and pop_ratio >= 0.20: ABUNDANT
elif stable_like: STABLE
else: UNCLASSIFIED
```

Important implication:

- classification is behavioral and post hoc
- the configured regime name and the classified regime can diverge

## 8. Optional Analysis Paths

### Performance profiling

When `--perf-flag` is enabled:

- step-level phase timings are collected
- commit timings are split into setup, deaths, births, and resource regrowth
- batch profiling aggregates those timings across runs

### World-frame analytics

When `--world-frame-flag` is enabled:

- `Engine.step()` samples a `WorldView` every 10 ticks
- batch analysis can then compute:
  - occupancy rate
  - crowding
  - peak density
  - resource level and heterogeneity
  - sampled energy moments
  - density/resource correlation

This path is useful but still secondary to the main experiment and verification flow.

## 9. Validation Surface

The validation CLI is:

```bash
python -m engine_build.main validate --suite <all|contracts|separation>
```

`run_validation_mode()` resolves the requested suite through `engine_build/cli/spec.py`.

There is also a small alias layer for older suite names:

- `test_regime_contracts -> contracts`
- `test_regime_separation -> separation`
- `regime_contracts -> contracts`

### Contract validation

`tests/validation/test_regime_contracts.py` currently checks:

- `stable`
- `extinction`
- `saturated`

using the regime contracts in `engine_build/validation/contracts.py`.

### Separation validation

`tests/validation/test_regime_separation.py` currently checks:

- `stable` vs `extinction`
- `saturated` vs `stable`
- `fragile` vs `stable`

### Validation helper path

Programmatic validation currently runs through:

```text
run_validation_case()
-> Runner.run_regime_batch()
-> analyze_batch()
-> summarise_regime()
-> classify_regime()
```

using `VALIDATION_DEFAULTS`.

## 10. Verification Surface

The verification CLI is:

```bash
python -m engine_build.main verify --suite <all|determinism|invariants|rng|snapshots>
```

Verification currently covers:

- determinism
- snapshots
- RNG isolation
- invariants

## 11. Freeze-Relevant Limits

- validation is selective, not exhaustive across all six named regimes
- `collapse` and `abundant` are classified and runnable, but they are not yet covered by hard contract tests
- world-frame analytics and `plot_dev` are useful support tools, not yet the most polished public interface
- custom `tail_fraction` is not fully wired into `run_experiment_mode()`

## 12. Recommended Commands

Baseline experiment:

```bash
python -m engine_build.main experiment --regime stable
```

Experiment with profiling:

```bash
python -m engine_build.main experiment --regime abundant --perf-flag
```

Experiment with world-frame sampling:

```bash
python -m engine_build.main experiment --regime stable --world-frame-flag --plot-dev
```

Verification and validation:

```bash
python -m engine_build.main verify --suite all
python -m engine_build.main validate --suite all
```
