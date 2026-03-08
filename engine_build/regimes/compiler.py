

from .spec import RegimeSpec
from .compiled import CompiledRegime

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


def compile_regime(spec: RegimeSpec) -> CompiledRegime:

    E_max = spec.max_energy
    R_max = spec.max_resource_level

    r = spec.energy
    res = spec.resources
    land = spec.landscape

    # harvest
    max_harvest = int(r.harvest_fraction * R_max)

    # metabolism
    movement_cost = int(r.alpha * max_harvest)

    # reproduction
    reproduction_threshold = int(r.gamma * movement_cost)
    reproduction_cost = int(r.beta * reproduction_threshold)

    # environment
    regen_rate = int(res.regen_fraction * R_max)

    return CompiledRegime(
        max_energy=E_max,
        max_resource_level=R_max,

        max_harvest=max_harvest,
        movement_cost=movement_cost,
        reproduction_threshold=reproduction_threshold,
        reproduction_cost=reproduction_cost,

        regen_rate=regen_rate,

        correlation=land.correlation,
        contrast=land.contrast,
        floor=land.floor
    )