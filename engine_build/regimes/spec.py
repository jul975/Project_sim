


# RegimeSpec  →  CompiledRegime  →  Engine / World / Agent

"""
RegimeSpec:
    - human-authored
    - ratios + anchors only
    - no derived numbers

    
    RegimeSpec
    ├─ EnergySystem
    ├─ ResourceSystem
    ├─ LandscapeSystem
    └─ PopulationSystem


    Scale anchors:

    - max_energy
    - max_resource_level

    Active ecological controls:

    - harvest_fraction
    - beta
    - gamma
    - regen_fraction

    Temporarily frozen control:

    - alpha = 0.6 => temp hardcoded, clearly sustainable movement and meaningful metabolic pressure
        
"""


from dataclasses import dataclass

@dataclass(frozen=True)
class EnergySpec:
    beta: float
    gamma: float
    harvest_fraction: float

    alpha: float = 0.6 # METABOLIC PRESSURE => movement_cost / max_harvest => temp hardcoded, clearly sustainable movement and meaningful metabolic pressure

    initial_energy_low_ratio : float = 0.3
    initial_energy_high_ratio : float = 0.6

@dataclass(frozen=True)
class ReproductionSpec:
    probability: float = 0.25
    probability_change_condition: float = 0.5


@dataclass(frozen=True)
class ResourceSpec:
    regen_fraction: float


@dataclass(frozen=True)
class LandscapeSpec:
    # ρ_L = k / W
    # σ_F = (F_max - f_min) / R_max
    
    correlation: float 
    contrast: float 
    floor: float 

@dataclass(frozen=True)
class PopulationSpec:
    # NOTE: move to simulationDomain later (simulationDomain = world size + population config + ... )

    max_agent_count: int
    initial_agent_count: int
    max_age: int


"""
        NOTE: 

Anchor Rules:

        1. max_energy comfrable larger then derived reproduction threshold.
            => movement_cost < reproduction_threshold < max_energy
            practically default  = max_energy = 100 or 120

        2. max_resource_level large enough to support smooth harverst scaling.
            => max_harvest < max_resource_level
            practically default  = max_resource_level = 80-100

        3. anchors should make integer rounding stable.
            => avoid fractional values, round to integers. or collapse to 0.
            E_max = 100-150 => 
            R_max = 80-100
            W = 100-400


"""


@dataclass(frozen=True)
class RegimeSpec:
    # energy = EnergyRatios
    # resources = ResourceRatios
    # landscape = LandscapeRatios
    # population = PopulationConfig

    max_energy: int = 100                 # E_max => anchor
    max_resource_level: int  = 80        # R_max => anchor
    world_size: int = 400                 # W => anchor  NOTE: move to simulationDomain later

    energy_spec: EnergySpec
    resources_spec: ResourceSpec
    landscape_spec: LandscapeSpec
    reproduction_spec: ReproductionSpec
    population_spec: PopulationSpec
