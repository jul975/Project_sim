from dataclasses import dataclass
from .regime_classification import RegimeClass
from .batch_analytics import BatchAnalysis
import numpy as np


@dataclass(frozen=True)
class RegimeSummary:
    mean_population_over_runs: float
    std_mean_population_over_runs: float
    extinction_rate: float
    cap_hit_rate: float
    near_cap_rate: float
    birth_death_ratio: float
    mean_time_cv_over_runs: float
    final_population_cv: float
    max_agent_count: int


def summarise_regime(batch_analysis : BatchAnalysis) -> RegimeSummary:
    """ summarise a regime from a batch analysis. """
    agg = batch_analysis.aggregate_fingerprint
    final_populations = [run_results.metrics.population[-1] for run_results in batch_analysis.batch_metrics.values()]
    mean_final = np.mean(final_populations)
    std_final = np.std(final_populations)

    return RegimeSummary(
        mean_population_over_runs=agg.mean_population_over_runs,
        std_mean_population_over_runs=agg.std_mean_population_over_runs,
        extinction_rate=agg.extinction_rate,
        cap_hit_rate=agg.cap_hit_rate,
        near_cap_rate=agg.batch_near_cap_rate,
        birth_death_ratio=agg.birth_death_ratio,
        mean_time_cv_over_runs=agg.mean_time_cv_over_runs,
        final_population_cv=std_final / mean_final,
        max_agent_count=next(iter(batch_analysis.batch_metrics.values())).metrics.max_agent_count
    )


def classify_regime(summary: RegimeSummary) -> RegimeClass:
    pop_ratio = summary.mean_population_over_runs / summary.max_agent_count

    if summary.extinction_rate >= 0.8:
        return RegimeClass.COLLAPSE

    if summary.extinction_rate > 0.0:
        return RegimeClass.FRAGILE

    if summary.cap_hit_rate >= 0.05 or summary.near_cap_rate >= 0.35:
        return RegimeClass.SATURATED

    if pop_ratio >= 0.14 and summary.mean_time_cv_over_runs <= 0.08:
        return RegimeClass.ABUNDANT

    if summary.mean_time_cv_over_runs <= 0.10 and 0.95 <= summary.birth_death_ratio <= 1.05:
        return RegimeClass.STABLE

    return RegimeClass.UNCLASSIFIED