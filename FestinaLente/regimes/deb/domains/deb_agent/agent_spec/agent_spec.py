'''
Human authored model assumptions
source: amp, literature, expert knowledge

'''

from dataclasses import dataclass



@dataclass(frozen=True)
class SheepModelSpec:
    dt_days: float = 1.0

    grass_energy_density_J_per_kg_DM: float = 18_000_000.0
    assimilation_efficiency: float = 0.45

    newborn_dmi_ratio_per_day: float = 0.00
    juvenile_dmi_ratio_per_day: float = 0.04
    adult_dmi_ratio_per_day: float = 0.025

    structure_energy_density_J_per_cm3: float = 23_000.0

    c_transport_J_per_kg_m: float = 2.35
    baseline_daily_path_length_m: float = 9500.0
    terrain_factor: float = 1.0