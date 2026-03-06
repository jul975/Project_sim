import numpy as np
from .config import SimulationConfig
from .rng_utils import reconstruct_rng
from .agent import Agent

from .config import DeathBucket
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




    def harvest(self, agents : list[Agent], position : np.int64) -> np.int64:
        """ harvests resources from a given cell, deterministically. """
        
       
        available_resources = self.resources[position]
        if available_resources <= 0:
            return 0
        agents = sorted(agents, key=lambda a: a.id)

        n_agents = len(agents)
        total_demand = n_agents * self.max_harvest
        harvest = min(available_resources, total_demand)

        base_agent_harvest = harvest // n_agents
        remaining_harvest = harvest % n_agents

        for i, agent in enumerate(agents):
            # distribute remainder deterministically while conserving energy
            agent_harvest = base_agent_harvest + 1 if i < remaining_harvest else base_agent_harvest
            # note, removes explicit agent method, 
            agent.harvest_resources(agent_harvest)

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
    

            # NOTE: 
                # future: will prop need to sep resolve_harvest into diff sub steps.
                # right now, this is the cleanest step, despite seeming bloated.
                # => Need more logic in order to structure it properly. will create problems if i do it now
    
            # M: move agents
            # H: world.resolve_harvest()
            # R: world.resolve_reproduction()
            # G: world.resolve_agent_aging()
            # Π: commit births/deaths
        """
        | Mean occupancy | Meaning               |
        | -------------- | --------------------- |
        | ≈ 1            | agents evenly spread  |
        | 2-3            | moderate clustering   |
        | 4-6            | strong clustering     |
        | >6             | severe local pressure |
        """

    
    def resolve_harvest_world(self, occupied_positions : dict[np.int64, list[Agent]]) -> None:

        pending_death: dict[str: DeathBucket] = {
            "post_harvest_starvation" : DeathBucket(),
            "post_reproduction_death" : DeathBucket()
            }
        
        reproducing_agents: list[Agent] = []

        for position, agents in occupied_positions.items():

            harvest = self.harvest(agents, position)
            if harvest <= 0:
                for agent in agents:
                    if agent.energy_level <= 0:
                        pending_death["post_harvest_starvation"].count += 1
                        pending_death["post_harvest_starvation"].agents.append(agent.id)
                        continue

                # R
            for agent in agents:
                if agent.can_reproduce():
                    if agent.does_reproduce():
                        reproducing_agents.append(agent)
                        if agent.energy_level <= 0:
                            pending_death["post_reproduction_death"].count += 1
                            pending_death["post_reproduction_death"].agents.append(agent.id)
                            continue

                agent.age_agent()
                
        return reproducing_agents, pending_death, 
    
    
    

