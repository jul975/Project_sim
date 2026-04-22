from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CompiledEnergetics:
    reserve_init: float
    repr_buffer_init: float
    eta_base: float
    kappa: float
    maintenance_coeff: float
    mass_scaling_exponent: float
    temperature_ref_K: float | None
    activation_energy_maint: float | None
    activation_energy_assim: float | None
    movement_mode: str
    reproduction_mode: str
    death_mode: str

@dataclass(frozen=True)
class CompiledWorldEnergetics:
    world_width: int
    world_height: int
    capacity_field: np.ndarray
    initial_stock_field: np.ndarray
    inflow_field: np.ndarray
