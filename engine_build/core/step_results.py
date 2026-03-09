
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