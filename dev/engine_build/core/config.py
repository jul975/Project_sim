from dataclasses import dataclass, field
"""
alpha = **Metabolic pressure**

alpha ≈ 0.6 - 0.9
alpha < 1 => movement is sustainable
alpha > 1 => movement is not sustainable, to draining for agent to move
alpha = 1 => movement is barely sustainable

beta = **Reproductive depletion**

beta ≈ 0.8 - 1.0
beta +- 1.0 => reproduction exhausts the agent
beta < 1 => agent survives reproduction
beta > 1 => no reproduction possible, 

gamma = **Energy maturity scale**


gamma ≈ 5 - 15

"""

import numpy as np

from typing import List, TYPE_CHECKING

## TESTING REGIMES
REGIMES = {
    "extinction": (1.2, 1.0, 5),
    "stable": (0.6, 0.8, 10),
    "saturated": (0.4, 0.6, 6),
}


@dataclass(frozen=True)
class EnergyParams:
    movement_cost: np.int64
    reproduction_threshold: np.int64
    reproduction_cost: np.int64

@dataclass(frozen=True)
class EnergyRatios:
    alpha: float = 0.6   # METABOLIC PRESSURE => movement_cost / max_harvest
    beta: float = 0.8   # REPRODUCTIVE DEPLETION => reproduction_cost / reproduction_threshold
    gamma: float = 10.0  # ENERGY MATURITY SCALE => reproduction_threshold / movement_cost

@dataclass(frozen=True)
class EnergyConfig:
    max_harvest: int = 5
    ratios: EnergyRatios = field(default_factory=EnergyRatios)


@dataclass(frozen=True)
class PopulationConfig:
    max_agent_count: int = 1000
    initial_agent_count: int = 10
    max_age: int = 200




@dataclass(frozen=True)
class SimulationConfig:
    population_config: PopulationConfig = field(default_factory=PopulationConfig)
    world_size: int = 200

    energy_init_range: tuple[int, int] = (30, 60)

    reproduction_probability: float = 0.25
    reproduction_probability_change_condition: float = 0.50

    resource_regen_rate: int = 2

    energy_config: EnergyConfig = field(default_factory=EnergyConfig)
    max_resource_level: int = 80


    

    @classmethod
    def from_dict(cls, d: dict) -> "SimulationConfig":
        # rebuild nested dataclasses explicitly
        
        ec_dict = d["energy_config"]
        # GUARD if energy_config is not in passed dictionary, use default_factory
        if ec_dict is None:
            return cls(**d)
      


        r_dict = ec_dict["ratios"]

        ratios = EnergyRatios(**r_dict)
        energy_config = EnergyConfig(
            max_harvest=ec_dict["max_harvest"],
            ratios=ratios
        )

        outer = dict(d)
        outer["energy_config"] = energy_config
        return cls(**outer)
    



#### ========================================================
#### METRICS CONFIG
#### ========================================================

# NOTE: 
        #   -   DeathBucket is used in engine.step() and is part of the fundamental engine logic.
        #   -   Is however implemented as classification tool to order causes of death, needed for internal logic AND metric collection. 

@dataclass
class DeathBucket:
    count: int = 0
    agents: List[np.int64] = field(default_factory=list)


## NOTE: new metrics dataclass to store and process fingerprints

@dataclass(frozen=True)
class RunMetricsConfig:

    run_REGIME : str
    run_seed : np.int64
    tail_window_start : np.int64
    metrics_collection_interval : np.int64

@dataclass(frozen=True)
class RunMetricsAgents:
    min_population : np.int64
    max_population : np.int64
    mean_population : np.float64
    std_population : np.float64
    range_population : np.int64

    cap_hit_rate : np.float64

    extinction_tick : np.int64 | None
    mean_deaths_per_tick : np.float64
    mean_births_per_tick : np.float64
    
    mean_deaths_cause_tail : dict[str, np.float64]
    proportion_deaths_cause_tail : dict[str, np.float64]
    
@dataclass(frozen=True)
class RunMetricsWorld:
    total_resources : np.int64
    mean_resources : np.float64
    depletion_fraction : np.float64
    fertility : np.float64


@dataclass(frozen=True)
class RunMetricsFingerprint:
    # NOTE: 
        #   -   Is frozen bc internals should not be mutated after processing. 
    run_metrics_config : RunMetricsConfig
    agents_metrics : RunMetricsAgents
    world_metrics : RunMetricsWorld



    """ 
        -   min, max, mean population
        -   std/range population
        -   cap_hit_rate

        -   extinction_tick : None | tick_n
        -   mean deaths/tick
        -   mean births/tick

        -   mean(deaths_cause_tail)
        -   proportion: deaths_cause_tail_sum / total_deaths_tail_sum

        
        World metrics:
        1. total resources
        2. mean resources
        3. depletion fraction vs fertility

    """
    pass
