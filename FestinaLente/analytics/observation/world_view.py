
from dataclasses import dataclass, field
import numpy as np

# observational obj

@dataclass(frozen=True)
class WorldView:
    tick : int = 0
    positions : np.ndarray = field(default_factory=np.ndarray)
    energies : np.ndarray = field(default_factory=np.ndarray)
    resources : np.ndarray = field(default_factory=np.ndarray)
    
