
from dataclasses import dataclass

# CompiledRegime  →  Engine / World / Agent
# obj gets created during intialization of engine.

        # EVERY SUBSYSTEM READS FROM THIS.


"""
    RegimeSpec
    ├─ EnergySpec
    ├─ ResourceSpec
    ├─ LandscapeSpec
    ├─ ReproductionSpec
    └─ PopulationSpec
        
        → CompiledRegime
            ├─ EnergyParams
            ├─ ResourceParams
            ├─ LandscapeParams
            ├─ ReproductionParams
            └─ PopulationParams


            → Engine
                ├─ World
                │   └─ Agents
                └─ Metrics

"""
@dataclass(frozen=True)
class EnergyParams:
    # max_energy
    max_energy: int
    energy_init_range: tuple[int, int]
    
    max_harvest: int # agent level logic
    movement_cost: int
    reproduction_threshold: int
    reproduction_cost: int

@dataclass(frozen=True)
class ReproductionParams:
    probability: float
    probability_change_condition: float

@dataclass(frozen=True)
class ResourceParams:
    regen_rate: int

@dataclass(frozen=True)
class LandscapeParams:
    correlation: float
    contrast: float
    floor: float

@dataclass(frozen=True)
class PopulationParams:
    max_agent_count: int
    initial_agent_count: int
    max_age: int

@dataclass(frozen=True)
class WorldParams:
    world_width: int
    world_height: int



@dataclass(frozen=True)
class CompiledRegime:

    # anchors
    max_energy: int
    max_resource_level: int

    # energy system
    energy_params: EnergyParams

    # resource system
    resource_params: ResourceParams

    # reproduction system
    reproduction_params: ReproductionParams

    # population system
    population_params: PopulationParams

    # world system
    world_params: WorldParams


    # landscape
    landscape_params: LandscapeParams