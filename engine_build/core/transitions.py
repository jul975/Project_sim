

from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class DeathBucket:
    count: int = 0
    agents: List[np.int64] = field(default_factory=list)

