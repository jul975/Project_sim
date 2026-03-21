from dataclasses import dataclass
from .regime_classification import RegimeClass
from .batch_analytics import BatchAnalysis
import numpy as np
from .fingerprint import AggregatedFingerprint


@dataclass(frozen=True)
class RegimeSummary:
    final_populations_mean: int
    mean_population_over_runs: float

    std_mean_population_over_runs: float
    extinction_rate: float
    
    cap_hit_rate: float
    near_cap_rate: float
    
    low_population_rate: float
    birth_death_ratio: float
    
    mean_time_cv_over_runs: float
    final_population_cv: float
    max_agent_count: int


def summarise_regime(batch_analysis : BatchAnalysis) -> RegimeSummary:
    """ summarise a regime from a batch analysis. """
    agg : AggregatedFingerprint = batch_analysis.aggregate_fingerprint
    final_populations = agg.final_populations
    mean_final = np.mean(final_populations)
    std_final = np.std(final_populations)

    return RegimeSummary(
        final_populations_mean= int(mean_final),
        mean_population_over_runs=agg.mean_population_over_runs,
        
        std_mean_population_over_runs=agg.std_mean_population_over_runs,
        extinction_rate=agg.extinction_rate,
        
        cap_hit_rate=agg.cap_hit_rate,
        near_cap_rate=agg.batch_near_cap_rate,
        
        low_population_rate=agg.batch_near_low_population_rate,
        birth_death_ratio=agg.birth_death_ratio,
        
        mean_time_cv_over_runs=agg.mean_time_cv_over_runs,
        
        final_population_cv=std_final / mean_final,

        max_agent_count= batch_analysis.batch_metadata.max_agent_count,
    )


def classify_regime(summary: RegimeSummary) -> RegimeClass:
    pop_ratio = summary.mean_population_over_runs / summary.max_agent_count
    bdr = summary.birth_death_ratio
    time_cv = summary.mean_time_cv_over_runs

    stable_like = (
        time_cv <= 0.10
        and 0.95 <= bdr <= 1.05
    )

    # 1) FAILURE STATES
    if summary.extinction_rate >= 0.95:
        return RegimeClass.EXTINCTION

    if summary.extinction_rate >= 0.50:
        return RegimeClass.COLLAPSE

    # severe low-pop persistence without full extinction
    if summary.low_population_rate >= 0.80 and bdr < 0.95:
        return RegimeClass.COLLAPSE

    # 2) BOUNDARY STATE
    if summary.cap_hit_rate >= 0.20 or summary.near_cap_rate >= 0.30:
        return RegimeClass.SATURATED

    # 3) SURVIVING BUT STRESSED
    if summary.low_population_rate >= 0.20:
        return RegimeClass.FRAGILE

    # 4) INTERIOR REGIMES
    if stable_like and pop_ratio >= 0.20:
        return RegimeClass.ABUNDANT

    if stable_like:
        return RegimeClass.STABLE

    return RegimeClass.UNCLASSIFIED