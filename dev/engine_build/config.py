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


@dataclass
class DeathBucket:
    count: int = 0
    agents: List[np.int64] = field(default_factory=list)

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