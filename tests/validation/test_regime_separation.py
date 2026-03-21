
import pytest
from engine_build.validation.helpers import run_validation_case

# NOTE: make the right comparisons!!! 


@pytest.mark.regime

def test_stable_vs_extinction():
    stable = run_validation_case("stable")
    extinction = run_validation_case("extinction")

    assert stable.summary.extinction_rate < extinction.summary.extinction_rate
    assert stable.summary.mean_population_over_runs > extinction.summary.mean_population_over_runs
    assert stable.summary.low_population_rate < extinction.summary.low_population_rate


def test_saturated_vs_stable():
    saturated = run_validation_case("saturated")
    stable = run_validation_case("stable")

    assert saturated.summary.cap_hit_rate > stable.summary.cap_hit_rate
    assert saturated.summary.near_cap_rate > stable.summary.near_cap_rate
    assert saturated.summary.mean_population_over_runs > stable.summary.mean_population_over_runs


def test_fragile_vs_stable():
    fragile = run_validation_case("fragile")
    stable = run_validation_case("stable")

    assert fragile.summary.low_population_rate > stable.summary.low_population_rate
    assert fragile.summary.mean_time_cv_over_runs >= stable.summary.mean_time_cv_over_runs