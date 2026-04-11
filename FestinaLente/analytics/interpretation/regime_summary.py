from dataclasses import dataclass

import numpy as np

from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.analytics.derive.batch.aggregate_fingerprint import AggregatedFingerprint

@dataclass(frozen=True)
class RegimeSummary:
    """ Summary of a regime. 
    
    Attributes:
        - final_populations_mean:           Mean of the final populations over runs.
        - mean_population_over_runs:        Mean of the mean populations over runs.

        - std_mean_population_over_runs:    Standard deviation of the mean populations over runs.
        - extinction_rate:                  Fraction of runs that went extinct.

        - cap_hit_rate:                     Fraction of time steps at which the carrying capacity was hit.
        - near_cap_rate:                    Fraction of time steps at which the population was near the carrying capacity.

        - low_population_rate:              Fraction of time steps at which the population was low.
        - birth_death_ratio:                Mean birth to death ratio over runs.

        - mean_time_cv_over_runs:           Mean of the time coefficient of variation over runs.
        - final_population_cv:              Coefficient of variation of the final populations over runs.
        - max_agent_count:                  Maximum agent count of the regime.
    """
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
    """ summarise a regime from a batch analysis. 
    
    Returns:
        RegimeSummary

    NOTE: 
        -   This is a post hoc summary, and should be used for reporting only.
        -   Classification should be used for regime classification.
        -   This summary is derived from the aggregate fingerprint, and does not contain all information
            from the batch analysis.
    """
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
        
        final_population_cv = 0.0 if mean_final == 0 else float(std_final / mean_final),
        
        max_agent_count= batch_analysis.batch_metadata.max_agent_count,
    )

