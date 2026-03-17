
from .spec import RegimeSpec, EnergySpec, ResourceSpec, LandscapeSpec, PopulationSpec, ReproductionSpec




# NOTE: population config needs work, not biologically, need SimulationDomain
REGIMES = {
    
    "stable": RegimeSpec(
        energy_spec=EnergySpec(beta=0.8, gamma=10, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)
    ),
    "fragile": RegimeSpec(
        energy_spec=EnergySpec(beta=5, gamma=10, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)
    ),
    "extinction": RegimeSpec(
        energy_spec=EnergySpec(beta=1.0, gamma=5, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
        resources_spec=ResourceSpec(regen_fraction=0.03),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)  
    ),
    "collapse": RegimeSpec(
        energy_spec=EnergySpec(beta=1.0, gamma=2.5, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
        resources_spec=ResourceSpec(regen_fraction=0.03),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)  
    ),
    "saturated": RegimeSpec(
        energy_spec=EnergySpec(beta=0.8, gamma=1, harvest_fraction=0.05),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(max_agent_count=1000, initial_agent_count=10, max_age=100)
    ),
    "abundant": RegimeSpec(
        energy_spec=EnergySpec(beta=0.1, gamma=1, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(probability=0.25, probability_change_condition=0.5),
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