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


#PL 
# ρ_L = k / W
# k = ρ_L * W
# 0.03
# 0.055
# 0.1
@dataclass(frozen=True)
class FertilityConfig:
    fertility_correlation_ratio: float = 0.055
    fertility_floor_ratio: float = 0.0
    fertility_contrast_ratio: float = 1.0


@dataclass(frozen=True)
class SimulationConfig:
    population_config: PopulationConfig = field(default_factory=PopulationConfig)
    world_size: int = 200

    fertility_config: FertilityConfig = field(default_factory=FertilityConfig)

    energy_init_range: tuple[int, int] = (30, 60)

    reproduction_probability: float = 0.25
    reproduction_probability_change_condition: float = 0.50

    resource_regen_rate: int = 2

    energy_config: EnergyConfig = field(default_factory=EnergyConfig)
    max_resource_level: int = 80


    

    @classmethod
    def from_dict(cls, d: dict) -> "SimulationConfig":
        outer = dict(d)

        # rebuild population_config
        pc_dict = outer.get("population_config")
        if isinstance(pc_dict, dict):
            outer["population_config"] = PopulationConfig(**pc_dict)

        # rebuild energy_config (your existing logic, slightly guarded)
        ec_dict = outer.get("energy_config")
        if isinstance(ec_dict, dict):
            r_dict = ec_dict.get("ratios")
            ratios = EnergyRatios(**r_dict) if isinstance(r_dict, dict) else EnergyRatios()
            outer["energy_config"] = EnergyConfig(
                max_harvest=ec_dict.get("max_harvest", EnergyConfig().max_harvest),
                ratios=ratios
            )
        
        # rebuild fertility_config
        fc_dict = outer.get("fertility_config")
        if isinstance(fc_dict, dict):
            outer["fertility_config"] = FertilityConfig(**fc_dict)
        

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

