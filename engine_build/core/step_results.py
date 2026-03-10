
"""
NOTE: 
    - STEP METRICS REPRESENTS OBSERVABILITY FROM OUTSIDE THE ENGINE. 
    - NO STATE MUTATION LOGIC SHOULD BE PERFORMED IN THIS LAYER.

"""


from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class DeathBucket:
    count: int = 0
    agents: List[np.int64] = field(default_factory=list)

@dataclass(frozen=True)
class StepMetrics:
    births : int
    deaths : int
    pending_death : dict[str, DeathBucket] = field(default_factory=dict)
    occupancy_metrics : dict[str, np.float64] = field(default_factory=dict)

# NOTE: not holding agent references, only ids.
@dataclass(frozen=True)
class MovementReport:
    metabolic_deaths : DeathBucket
    age_deaths : DeathBucket












##################################
"""
occupied_cells = len(context.occupied_positions)
moved_surviving_agents  = sum(len(v) for v in context.occupied_positions.values())
mean_occupancy = (moved_surviving_agents  / len(context.occupied_positions)) if context.occupied_positions else 0
max_occupancy = max(len(v) for v in context.occupied_positions.values()) if context.occupied_positions else 0
ratio_t = max_occupancy / mean_occupancy if mean_occupancy > 0 else 0

occupancy_metrics : dict[str, np.float64] = {
    "occupied_cells" : occupied_cells,
    "mean_occupancy" : mean_occupancy,
    "max_occupancy" : max_occupancy,
    "ratio_t" : ratio_t
}"""