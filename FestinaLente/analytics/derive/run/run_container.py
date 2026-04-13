
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



## world frame 

@dataclass(frozen=True)
class SingleRunWorldFrameSummary:
    """ Summary of single run world frame analytics. """
    mean_occupancy_rate: float
    mean_crowding_nonzero: float
    mean_peak_density_sampled: float

    mean_resource_level: float
    mean_resource_heterogeneity: float
    mean_resource_depletion_rate: float

    mean_energy_level_sampled: float
    mean_energy_std_sampled: float
    mean_energy_cv_sampled: float

    mean_density_resource_correlation: float

@dataclass
class RunFrames:
    """ Metrics of world frames. """
    densities: list[np.ndarray] = field(default_factory=list)
    resources: list[np.ndarray] = field(default_factory=list)
    energies: list[np.ndarray] = field(default_factory=list)