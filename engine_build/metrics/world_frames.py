
from dataclasses import dataclass

import numpy as np

@dataclass
class WorldFrames:
        

        resources : list[np.ndarray] = []
        density : list[np.ndarray] = []
        population : list[int] = []
        
    