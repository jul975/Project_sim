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

"""
Fertility Smoothing: Landscape Correlation Ratio

The core idea is defined by the following relationship:

$$\rho_L = \frac{k}{W}$$

Where:
* k  = Kernel size
* W  = World size
* \rho_L = Landscape correlation ratio

This ratio determines the spatial influence of fertility across the environment.
"""



class World:
    def __init__(self, world_seed : np.int64 ,config : SimulationConfig, change_condition=False) -> None:   
        self.tick : np.int64 = 0
        self.world_size = config.world_size

        self.world_width = config.world_width
        self.world_height = config.world_height

        # self.world_area = 
        
        self.change_condition = change_condition
        self.config = config

        self.rng_world = np.random.default_rng(world_seed)

        # need to cleanup type hints, 
        self.fertility = self._generate_fertility_fields()
        self.resources = self.fertility.copy()
        self.resource_regen_rate = config.resource_regen_rate



        self.max_harvest = config.energy_config.max_harvest
    
 




    def _generate_fertility_fields(self) -> np.ndarray:
        """ generates fertility fields for the world. random noise → smooth fertility landscape. """

        # ρ_L = k / W
        # k = ρ_L * W
        # k = ρ_L * sqrt(W)
        # random 20×20 noise
        #        ↓
        # local 3×3 averaging
        #        ↓
        # smoothed 20×20 field
        #        ↓
        # scaled fertility 20×20 field

            # 
        raw_kernel = (
            self.config.fertility_config.fertility_correlation_ratio
            * self.world_width
        )

        kernel_size = max(3, int(round(raw_kernel)))

        if kernel_size % 2 == 0:
            kernel_size += 1

        radius = kernel_size // 2

        # random 2D noise
        noise = self.rng_world.random((self.world_height, self.world_width))

        smooth = np.zeros_like(noise)

        for y in range(self.world_height):
            for x in range(self.world_width):

                total = 0.0
                count = 0

                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):

                        ny = (y + dy) % self.world_height
                        nx = (x + dx) % self.world_width

                        total += noise[ny, nx]
                        count += 1

                smooth[y, x] = total / count

        fertility = (smooth * self.config.max_resource_level).astype(np.int64)

        return fertility






    def harvest(self, agents : list[Agent], position : tuple[np.int64, np.int64]) -> np.int64:
        """ harvests resources from a given cell, deterministically. """
        
        x, y = position
       
        available_resources = self.resources[y, x]
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

        self.resources[y, x] -= harvest
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
    def wrap_around(self, position : tuple[np.int64, np.int64]) -> tuple[np.int64, np.int64]:
        """ wraps position around world size. """
        return (position[0] % self.world_width, position[1] % self.world_height)


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
        # derive
        clone_world.world_width = world_snapshot["world_width"]
        clone_world.world_height = world_snapshot["world_height"]
        clone_world.world_size = clone_world.world_width * clone_world.world_height
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

    
    def resolve_harvest_world(self, occupied_positions : dict[tuple[np.int64, np.int64], list[Agent]]) -> None:

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

        return reproducing_agents, pending_death
    
    
    

