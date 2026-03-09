

from .spec import RegimeSpec, EnergySpec, ReproductionSpec, ResourceSpec, LandscapeSpec, PopulationSpec
from .compiled import CompiledRegime, EnergyParams, ReproductionParams, ResourceParams, LandscapeParams, PopulationParams, WorldParams

from math import sqrt
# RegimeSpec  →  CompiledRegime  →  Engine / World / Agent

# RegimeSpec → Compiler → CompiledRegime

# CompiledRegime → Engine → World → Agent

# NOTE: Single place in the codebase where the ecological math exists.!!

# becomes ecological compiler

"""
    NOTE: goal CompiledRegime:

                    RegimeSpec
                        ↓
                    compile()
                        ↓
                    CompiledRegime
                        ↓
                    Engine / World / Agent


    RegimeSpec
    ├─ EnergySystem
    ├─ ResourceSystem
    ├─ LandscapeSystem
    └─ PopulationSystem
        
        → CompiledRegime
            ├─ EnergySystem => EnergyParams
            │   ├─ E_max => anchor
            │   ├─ metabolic pressure (α)          => ratio 
            │   ├─ reproductive depletion (β)      => ratio
            │   ├─ reproductive maturity (γ)       => ratio
            │   ├─ harvest fraction (h)            => ratio
            │   ├─ max_harvest (H_max)               => derived
            │   ├─ movement_cost (c_m)               => derived
            │   ├─ reproduction_threshold (θ)        => derived
            │   └─ reproduction_cost (c_r)           => derived
            │
            ├─ ResourceSystem => ResourceParams
            │   ├─ R_max => anchor
            │   ├─ regen fraction (r)                => ratio
            │   └─ regen_rate (r_max)                => derived
            │
            ├─ LandscapeSystem => LandscapeParams
            │   ├─ fertility correlation ratio (ρ_L)                 => ratio
            │   ├─ fertility contrast (σ_F)                    => ratio
            │   └─ fertility floor (f_min)                       => ratio
            │       -> kernel size (k)                           => derived k = ρ_L * sqrt(W)
            │       -> fertility (f)                             => derived fertility = f_min + σ_F * smooth * (R_max - f_min)
            │
            └─ PopulationSystem => PopulationParams
                ├─ max_agent_count (P_max) => anchor
                ├─ max_age (A_max) => anchor
                └─ initial_agent_count (P_0) => anchor

            → Engine
                ├─ World
                │   └─ Agents
                └─ Metrics
                    


"""
def _compile_energy_system(regime_spec: RegimeSpec) -> EnergyParams:
    """ Compiles the energy system from the energy spec and the anchors. """
    # NOTE: round to avoid downward bias, max to avoid 0
    #       -   note, need to structure hierarchy enforcement of clearly

    E_max = regime_spec.max_energy
    R_max = regime_spec.max_resource_level
    energy_spec = regime_spec.energy_spec

    
    h_max = max(1, int(round(energy_spec.harvest_fraction * R_max)))
    h_max = min(h_max, E_max)

    c_m = max(1, int(round(energy_spec.alpha * h_max)))

    c_m = min(c_m, h_max)
    c_m = min(c_m, E_max)

    
    theta = max(1, (int(round(energy_spec.gamma * c_m))))
    # NOTE: theta = max(theta, 2 * c_m) => agents need to accumulate at least 2 movement costs before reproducing.
    # not now will look at effect when rewiring is done

    theta = max(theta, c_m)
    theta = min(theta, E_max)

    c_r = max(1, (int(round(energy_spec.beta * theta))))

    c_r = min(c_r, theta)

    low = max(1, int(round(energy_spec.initial_energy_low_ratio * E_max)))
    high = max(low, int(round(energy_spec.initial_energy_high_ratio * E_max)))

    energy_init_range = (low, high)

    
    return EnergyParams(
        max_energy=E_max,
        energy_init_range=energy_init_range,
        max_harvest=h_max,
        movement_cost=c_m,
        reproduction_threshold=theta,
        reproduction_cost=c_r
    )



def _compile_reproduction_system(regime_spec: RegimeSpec) -> ReproductionParams:
    """ Compiles the reproduction system from the reproduction spec and the anchors. """
    return ReproductionParams(
        probability=regime_spec.reproduction_spec.probability,
        probability_change_condition=regime_spec.reproduction_spec.probability_change_condition
    )

def _compile_resource_system(regime_spec: RegimeSpec) -> ResourceParams:
    """ Compiles the resource system from the resource spec and the anchors. """
    regen_rate = max(1, int(round(regime_spec.resources_spec.regen_fraction * regime_spec.max_resource_level)))
    
    
    return ResourceParams(
        max_resource_level=regime_spec.max_resource_level,
        regen_rate=regen_rate
    )



def _compile_landscape_system(regime_spec: RegimeSpec) -> LandscapeParams:
    """ Compiles the landscape system from the landscape spec and the anchors. """
    return LandscapeParams(
        correlation=regime_spec.landscape_spec.correlation,
        contrast=regime_spec.landscape_spec.contrast,
        floor=regime_spec.landscape_spec.floor
    )

def _compile_population_system(regime_spec: RegimeSpec) -> PopulationParams:
    """ Compiles the population system from the population spec and the anchors. """
    return PopulationParams(
        max_agent_count=regime_spec.population_spec.max_agent_count,
        initial_agent_count=regime_spec.population_spec.initial_agent_count,
        max_age=regime_spec.population_spec.max_age
    )

def _compile_world_system(W: int) -> WorldParams:
    """ Compiles the world system from the anchors. """
    return WorldParams(
        world_width=int(round(sqrt(W))),
        world_height=int(round(sqrt(W)))
    )


def compile_regime(regime_spec: RegimeSpec) -> CompiledRegime:
    """ Compiles the regime from the regime spec. """

    # NOTE: still need to select regime_specs, 
        #   -   define stable regime as class entry to have stable, single point of entry for now 

    
    energy_params = _compile_energy_system(regime_spec)
    resource_params = _compile_resource_system(regime_spec)
    reproduction_params = _compile_reproduction_system(regime_spec)
    landscape_params = _compile_landscape_system(regime_spec)
    population_params = _compile_population_system(regime_spec)
    world_params = _compile_world_system(regime_spec.world_size)


    return CompiledRegime(
        energy_params=energy_params,
        resource_params=resource_params,
        reproduction_params=reproduction_params,
        population_params=population_params,
        world_params=world_params,
        landscape_params=landscape_params
    )





def validate_regime(regime: CompiledRegime):

    energy = regime.energy_params
    resources = regime.resource_params

    if resources.regen_rate <= energy.movement_cost:
        print("Warning: regeneration ≤ movement cost → extinction likely")

    if energy.reproduction_threshold >= energy.max_energy:
        print("Warning: reproduction unreachable")

    if energy.max_harvest <= energy.movement_cost:
        print("Warning: agents barely sustain movement")