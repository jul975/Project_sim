

from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class EnergeticLawSpec:
    body_size_ref: float
    reserve_init_fraction: float
    repr_buffer_init_fraction: float
    assimilation_efficiency_base: float
    soma_allocation_kappa: float
    maintenance_coeff: float
    mass_scaling_exponent: float
    temperature_ref_K: float | None = None
    activation_energy_maint: float | None = None
    activation_energy_assim: float | None = None
    movement_mode: str = "fixed_cost"
    reproduction_mode: str = "buffer_threshold"
    death_mode: str = "reserve_failure"

@dataclass(frozen=True)
class WorldLawSpec:
    world_width: int
    world_height: int
    capacity_anchor: float
    patch_correlation: float
    patch_contrast: float
    patch_floor: float
    initial_fill_ratio: float
    world_balance_phi: float
    inflow_mode: str = "fertility_weighted"
"""

Data	Generalised animal	Ovis aries	Unit	Description
v	0.02	0.02737	cm/d	energy conductance
p_M	18	2511	J/d.cm^3	vol-spec som maint
k_J	0.002	0.002	1/d	maturity maint rate coefficient
k	0.3	0.006254	-	maintenance ratio
kap	0.8	0.7978	-	allocation fraction to soma
kap_G	0.8	0.7994	-	growth efficiency
kap_R	0.95	0.95	-	reproduction efficiency

"""


sheep = EnergeticLawSpec()