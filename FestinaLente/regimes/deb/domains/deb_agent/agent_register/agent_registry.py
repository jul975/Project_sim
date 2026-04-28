"""
should be blueprint for agent logic and top level specs, => DMI RATIOS ETC spec seperately from agent registry entry, which is more for compiled spec and agent class to use.

"""


# birth size
# adult size
# weaning timing
# puberty timing
# maintenance cost
# maturity maintenance rate
# allocation fraction
# growth efficiency
# reproductive efficiency


# daily max intake as fraction of body mass, from DMI data for sheep
from dataclasses import dataclass


DMI_RATIOS: dict[str, float] = {
    "newborn": 0.00,   # if milk-fed / not grazing yet
    "juvenile": 0.04,  # growing lamb, post-weaning
    "adult": 0.025,    # maintenance adult on pasture
}

grass_energy_density_J_per_kg_DM = 18_000_000.0

'''@dataclass(frozen=True)
class AgentRegistryEntry:
    """ placholder copy of sheep energetic spec, to be used in regime compiler and agent class """
    assimilation_efficiency : float = 0.45
    v_conductance: float  = 0.02737

    birth_wet_mass_kg: float = 5.4
    adult_female_wet_mass_kg: float = 86.0
    weaning_age_days: float = 135.0
    female_puberty_age_days: float = 548.0
    max_lifespan_days: float = 8322.0
    max_reproduction_rate_per_day: float = 0.004329

    kappa: float = 0.7978
    growth_efficiency: float = 0.7994
    reproduction_efficiency: float = 0.95
    maturity_maintenance_rate_per_day: float = 0.002

    somatic_maintenance_J_per_day_per_cm3: float = 2511.0


'''