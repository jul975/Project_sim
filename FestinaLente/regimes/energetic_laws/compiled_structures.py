from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CompiledAnimalParams:
    # NOTE: max harvest => adult sheep 3% of mass for average pasture
    # NOTE: will need to change agent class 
    birth_structure_kg: float
    max_structure_kg: float
    maturity_move_threshold_J: float
    maturity_repro_threshold_J: float
    kappa: float
    growth_efficiency: float
    reproduction_efficiency: float
    maturity_maintenance_rate_per_day: float
    somatic_maintenance_J_per_kg_day: float

@dataclass(frozen=True)
class CompiledWorldEnergetics:
    world_width: int
    world_height: int
    capacity_field: np.ndarray
    initial_stock_field: np.ndarray
    inflow_field: np.ndarray


