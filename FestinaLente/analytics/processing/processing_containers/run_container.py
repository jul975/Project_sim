
from dataclasses import dataclass, field

import numpy as np





## fingerprint
@dataclass(frozen=True)
class Fingerprint:
    """ Fingerprint of a single run. """
    min_population: int
    max_population: int
    final_population: int
    mean_population: float
    std_population: float
    range_population: float
    cap_hit_rate: float

    extinction_tick: int | None

    mean_births_per_tick: float
    mean_deaths_per_tick: float

    mean_deaths_cause_tail: dict[str, float]
    proportion_deaths_cause_tail: dict[str, float]

    near_cap_rate: float
    low_population_rate: float


## performance

@dataclass
class RunPerformanceMetrics:
    """ Performance metrics of a single run. """
    movement_time: float = 0.0
    interaction_time: float = 0.0
    biology_time: float = 0.0
    commit_time: float = 0.0

    commit_setup_time: float = 0.0
    commit_deaths_time: float = 0.0
    commit_births_time: float = 0.0
    commit_resource_regrowth_time: float = 0.0


## world frame 

@dataclass(frozen=True)
class SingleRunWorldFrameSummary:
    """ Summary of single run world frame analytics. 
    
    Attributes:
     - mean_occupancy_rate: mean proportion of occupied cells across captured world frames.
        - mean_crowding_nonzero: mean number of agents in occupied cells across captured world frames.
        - mean_peak_density_sampled: mean of the maximum agent count in any cell across captured world frames.

        - mean_resource_level: mean resource level across cells and captured world frames.
        - mean_resource_heterogeneity: mean of the standard deviation of resource levels across cells for each captured world frame.
        - mean_resource_depletion_rate: mean rate of change of resource levels across cells and captured

        - mean_energy_reserve_sampled: mean energy level of agents across captured world frames.
        - mean_energy_std_sampled: mean of the standard deviation of energy levels of agents across
        - mean_energy_cv_sampled: mean of the coefficient of variation of energy levels of agents across captured world frames.

        - mean_density_resource_correlation: mean of the correlation coefficient between agent density and resource level across captured world frames.
    
    """
    mean_occupancy_rate: float
    mean_crowding_nonzero: float
    mean_peak_density_sampled: float

    mean_resource_level: float
    mean_resource_heterogeneity: float
    mean_resource_depletion_rate: float

    mean_energy_reserve_sampled: float
    mean_energy_std_sampled: float
    mean_energy_cv_sampled: float

    mean_density_resource_correlation: float

@dataclass
class RunFrames:
    """ Metrics of world frames.
    Attributes: 
     - densities: list of 2D arrays of agent counts in each cell for each captured world frame.
     - resources: list of 2D arrays of resource levels in each cell for each captured world frame.
     - energies: list of 2D arrays of agent energy levels in each cell for each captured world frame.
     """
    densities: list[np.ndarray] = field(default_factory=list)
    resources: list[np.ndarray] = field(default_factory=list)
    energies: list[np.ndarray] = field(default_factory=list)