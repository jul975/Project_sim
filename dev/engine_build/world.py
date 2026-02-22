import numpy as np
from .config import SimulationConfig

class World:
    def __init__(self, config : SimulationConfig, change_condition=False) -> None:   
        self.tick : np.int64 = 0
        self.world_size = config.world_size
        self.change_condition = change_condition
        self.config = config


    # wrap around logic needs to be cleared up 
    def wrap_around(self, position : np.int64) -> np.int64:
        """ wraps position around world size. """
        return position % self.world_size


    @classmethod
    def from_snapshot(cls, world_snapshot: dict) -> "World":
        clone_world = object.__new__(cls)
        clone_world.tick = world_snapshot["tick"]
        clone_world.change_condition = world_snapshot["change_condition"]
    
        
        clone_world.world_size = world_snapshot["world_size"]
        return clone_world
    
    