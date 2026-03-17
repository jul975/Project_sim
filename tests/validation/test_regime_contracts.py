import pytest
import numpy as np
from dataclasses import fields

from engine_build.execution.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.runner.regime_runner import Runner
from engine_build.analytics.batch_analytics import analyze_batch


def run_regime_analysis(regime_name: str):
    regime_spec = get_regime_spec(regime_name)
    regime_config = compile_regime(regime_spec)

    runner = Runner(
        regime_config=regime_config,
        n_runs=VALIDATION_DEFAULTS["runs"],
        batch_id=DEFAULT_MASTER_SEED,
    )

    batch_results = runner.run_regime_batch(ticks=VALIDATION_DEFAULTS["ticks"])
    batch_analysis = analyze_batch(batch_results, regime_label=regime_name)
    return batch_analysis, batch_results


def assert_aggregate_fingerprint_finite(agg) -> None:
    for f in fields(agg):
        value = getattr(agg, f.name)
        assert np.isfinite(value), f"Invalid aggregate field: {f.name}={value}"


@pytest.mark.regime
@pytest.mark.validate
def test_stable_regime_validation():
    batch_analysis, batch_results = run_regime_analysis("stable")
    agg = batch_analysis.aggregate_fingerprint

    assert_aggregate_fingerprint_finite(agg)

    assert agg.mean_population_over_runs > 0
    assert agg.extinction_rate < 0.1
    assert agg.cap_hit_rate < 0.2
    assert agg.mean_time_cv_over_runs <= 0.2
    assert abs(agg.birth_death_ratio - 1.0) <= 0.1


@pytest.mark.regime
@pytest.mark.validate
def test_extinction_regime_validation():
    batch_analysis, batch_results = run_regime_analysis("extinction")
    agg = batch_analysis.aggregate_fingerprint

    assert_aggregate_fingerprint_finite(agg)

    cap = next(iter(batch_results.runs.values())).engine_final.max_agent_count

    assert agg.extinction_rate >= 0.8
    assert agg.mean_population_over_runs <= 0.1 * cap
    assert agg.cap_hit_rate <= 0.1
    assert agg.birth_death_ratio < 1.0

    for fp in batch_analysis.fingerprints_dict.values():
        assert fp.extinction_tick is not None, "Not all extinction runs extinguished"


@pytest.mark.regime
@pytest.mark.validate
def test_saturated_regime_validation():
    batch_analysis, batch_results = run_regime_analysis("saturated")
    agg = batch_analysis.aggregate_fingerprint

    assert_aggregate_fingerprint_finite(agg)

    cap = next(iter(batch_results.runs.values())).engine_final.max_agent_count

    assert agg.cap_hit_rate >= 0.8
    assert agg.mean_population_over_runs >= 0.8 * cap
    assert agg.mean_time_cv_over_runs <= 0.2
    assert agg.extinction_rate <= 0.05
    assert abs(agg.birth_death_ratio - 1.0) <= 0.1