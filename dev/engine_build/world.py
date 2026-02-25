import numpy as np
from .config import SimulationConfig
from .rng_utils import reconstruct_rng
"""
NOTE: 
=> topological helpers, 
    - wrap around logic
    - distance metrics 
    - random position 

    
self.fertility => 
K(x)=fertility[x]

"""



class World:
    def __init__(self, world_seed : np.int64 ,config : SimulationConfig, change_condition=False) -> None:   
        self.tick : np.int64 = 0
        self.world_size = config.world_size
        self.change_condition = change_condition
        self.config = config

        self.rng_world = np.random.default_rng(world_seed)

        # need to cleanup type hints, 
        self.fertility = self.rng_world.integers(0, config.max_resource_level, self.world_size) # NOTE: => scalar field 
        self.resources = self.fertility.copy()
        self.resource_regen_rate = config.resource_regen_rate

        self.max_harvest = config.energy_config.max_harvest




    def harvest(self, position : np.int64) -> np.int64 | bool:
        """ harvests resources from a given position. """
        """ NOTE: as harvest is agent based, the return value should either be an int representing the harvested quantity or False:
                            
                                   => if available resource at postion is falsy, return False
                                      -> will not modify streams and easy to handle in agent logic.
        """
       
        available_resources = self.resources[position]
        
        # NOTE: 
        # => future implementation with dynamic harvest values, right now keeping it simple
        harvest = min(available_resources, self.max_harvest)
        # self.resources[position] -= harvest
        self.resources[position] -= harvest
        return harvest
        

    def regrow_resources(self) -> None:
        """ regrows resources according to fertility. """
        self.resources = np.minimum(
            self.resources + self.resource_regen_rate,
            self.fertility
            )
        # evaluate and return as array of bools
        assert (self.resources >= 0).all()
        assert (self.resources <= self.fertility).all()
        
        


    # wrap around logic needs to be cleared up 
    def wrap_around(self, position : np.int64) -> np.int64:
        """ wraps position around world size. """
        return position % self.world_size


    @classmethod
    def from_snapshot(cls, world_snapshot: dict) -> "World":
        # config file is not needed for world reconstruction.
        clone_world = object.__new__(cls)
        clone_world.tick = world_snapshot["tick"]
        clone_world.rng_world = reconstruct_rng(world_snapshot["rng_world"])
        clone_world.change_condition = world_snapshot["change_condition"]

        # these are array!! so need to avoid copy by reference.
        clone_world.resources = world_snapshot["resources"].copy()
        clone_world.fertility = world_snapshot["fertility"].copy()

        clone_world.resource_regen_rate = world_snapshot["resource_regen_rate"]
        clone_world.max_harvest = world_snapshot["max_harvest"]
        clone_world.world_size = world_snapshot["world_size"]
        return clone_world
    
    