

# engine_build/validation/assertions.py
import math

def assert_finite_summary(summary) -> None:
    for name, value in vars(summary).items():
        if isinstance(value, (int, float)):
            assert math.isfinite(value), f"{name} is not finite: {value}"


def assert_contract(summary, contract) -> None:
    pop_ratio = summary.mean_population_over_runs / summary.max_agent_count

    def check_min(value, bound, name):
        if bound is not None:
            assert value >= bound, f"{name}={value} < {bound}"

    def check_max(value, bound, name):
        if bound is not None:
            assert value <= bound, f"{name}={value} > {bound}"

    check_min(summary.extinction_rate, contract.min_extinction_rate, "extinction_rate")
    check_max(summary.extinction_rate, contract.max_extinction_rate, "extinction_rate")

    check_min(summary.cap_hit_rate, contract.min_cap_hit_rate, "cap_hit_rate")
    check_max(summary.cap_hit_rate, contract.max_cap_hit_rate, "cap_hit_rate")

    check_min(summary.low_population_rate, contract.min_low_population_rate, "low_population_rate")
    check_max(summary.low_population_rate, contract.max_low_population_rate, "low_population_rate")

    check_min(summary.birth_death_ratio, contract.min_birth_death_ratio, "birth_death_ratio")
    check_max(summary.birth_death_ratio, contract.max_birth_death_ratio, "birth_death_ratio")

    check_min(pop_ratio, contract.min_mean_population_ratio, "pop_ratio")
    check_max(pop_ratio, contract.max_mean_population_ratio, "pop_ratio")

    check_min(summary.mean_time_cv_over_runs, contract.min_time_cv, "mean_time_cv_over_runs")
    check_max(summary.mean_time_cv_over_runs, contract.max_time_cv, "mean_time_cv_over_runs")