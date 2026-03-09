
from .spec import RegimeSpec, EnergySpec, ResourceSpec, LandscapeSpec, PopulationSpec



# NOTE: population config needs work, not biologically, need SimulationDomain
REGIMES = {
    
    "stable": RegimeSpec(
        energy_spec=EnergySpec(beta=0.8, gamma=10),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)
    ),
    "extinction": RegimeSpec(
        energy_spec=EnergySpec(beta=1.0, gamma=5),
        resources_spec=ResourceSpec(regen_fraction=0.03),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)  
    ),
    "saturated": RegimeSpec(
        energy_spec=EnergySpec(beta=0.6, gamma=6),
        resources_spec=ResourceSpec(regen_fraction=0.12),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)  
    )
}





def get_regime_spec(regime : str) -> RegimeSpec:
    try:
        return REGIMES[regime]
    except KeyError:
        raise ValueError(f"Unknown regime: {regime}")