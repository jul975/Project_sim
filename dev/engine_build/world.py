import numpy as np

class World:
    def __init__(self, change_condition=False) -> None:   
        self.tick : np.int64 = 0
        self.change_condition = change_condition


    @classmethod
    def from_snapshot(cls, world_snapshot: dict) -> "World":
        clone_world = object.__new__(cls)
        clone_world.tick = world_snapshot["tick"]
        clone_world.change_condition = world_snapshot["change_condition"]
        return clone_world
    
    