



from dataclasses import dataclass

from pyparsing import Dict

from FestinaLente.runner.utils.results import RunArtifacts
from FestinaLente.analytics.processing.run.world_frame_summary import SingleRunWorldFrameSummary











## Fingerprints

@dataclass(frozen=True)
class AggregatedFingerprint:
    """ Aggregated fingerprint over a batch of runs. """
    final_populations: list[int] 
    mean_population_over_runs: float
    std_mean_population_over_runs: float
    extinction_rate: float
    cap_hit_rate: float
    birth_death_ratio: float
    mean_time_cv_over_runs: float

    batch_near_cap_rate: float
    batch_near_low_population_rate: float


## Performance



@dataclass
class BatchPhaseProfile:
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0

    commit_setup: float = 0.0
    commit_deaths: float = 0.0
    commit_births: float = 0.0
    commit_resource_regrowth: float = 0.0

    movement_ratio: float = 0.0
    interaction_ratio: float = 0.0
    biology_ratio: float = 0.0
    commit_ratio: float = 0.0




## World frames

@dataclass(frozen=True)
class BatchWorldFrameSummary:


    mean_occupancy_rate_over_runs: float
    mean_crowding_nonzero_over_runs: float
    peak_density_mean_over_runs: float

    mean_resource_level_over_runs: float
    mean_resource_heterogeneity_over_runs: float
    mean_resource_depletion_rate_over_runs: float

    mean_energy_level_sampled_over_runs: float
    mean_energy_std_sampled_over_runs: float
    mean_energy_cv_sampled_over_runs: float

    mean_density_resource_correlation_over_runs: float

@dataclass(frozen=True)
class BatchWorldFrameAnalysis:
    """ Analysis of batch world frames. """
    # NOTE: 
    run_summaries: dict[int, SingleRunWorldFrameSummary]
    aggregate_summary: BatchWorldFrameSummary
