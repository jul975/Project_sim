import numpy as np
from .agent import Agent

from engine_build.regimes.compiled import CompiledRegime

from .transitions import DeathBucket

from .snapshots import WorldSnapshot, _world_from_snapshot




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
    def __init__(self, world_seed : np.int64 , config : CompiledRegime , change_condition=False) -> None:   
        self.tick : np.int64 = 0

        self.world_params = config.world_params
        self.resource_params = config.resource_params
        self.landscape_params = config.landscape_params

        self.world_size = self.world_params.world_width * self.world_params.world_height

        self.world_width = self.world_params.world_width
        self.world_height = self.world_params.world_height
        # self.world_area = 
        
        self.change_condition = change_condition
        self.world_params = self.world_params

        self.rng_world = np.random.default_rng(world_seed)

        # need to cleanup type hints, 
        self.fertility = self._generate_fertility_fields()
        self.resources = self.fertility.copy()
        self.resource_regen_rate = self.resource_params.regen_rate



        self.max_harvest = config.energy_params.max_harvest

        self._assert_invariants()
    

    def _assert_invariants(self) -> None:
        """ asserts world invariants. """
        """Validate world state consistency."""

        # world dimensions
        assert self.world_width > 0
        assert self.world_height > 0
        assert self.world_size == self.world_width * self.world_height

        # grid shapes
        assert self.resources.shape == (self.world_height, self.world_width)
        assert self.fertility.shape == (self.world_height, self.world_width)

        # resource bounds
        assert (self.resources >= 0).all()
        assert (self.resources <= self.fertility).all()

        # fertility sanity
        assert (self.fertility >= 0).all()

        # integer resource model
        assert issubclass(self.resources.dtype.type, np.integer)
        assert issubclass(self.fertility.dtype.type, np.integer)

        # tick validity
        assert self.tick >= 0

        # RNG sanity
        assert isinstance(self.rng_world, np.random.Generator)

        assert np.isfinite(self.resources).all()
        assert np.isfinite(self.fertility).all()
    
    




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
            self.landscape_params.correlation
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

        fertility = (smooth * self.resource_params.max_resource_level).astype(np.int64)

        return fertility





# call from transitions
    def harvest(self, agents : list[Agent], position : tuple[np.int64, np.int64]) -> None:
        """ harvests resources from a given cell, deterministically. """
        
        x, y = position
       
        available_resources = self.resources[y, x]
        if available_resources <= 0:
            return 
        # NOTE: potentially remove after next testing round sort agents by id
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
        


        
        
        

    def regrow_resources(self) -> None:
        """ regrows resources according to fertility. """
        np.add(self.resources, self.resource_regen_rate, out=self.resources)
        np.minimum(self.resources, self.fertility, out=self.resources)
        # evaluate and return as array of bools
        assert (self.resources >= 0).all()
        assert (self.resources <= self.fertility).all()
        
        


    # wrap around logic needs to be cleared up 
    def wrap_around(self, position : tuple[np.int64, np.int64]) -> tuple[np.int64, np.int64]:
        """ wraps position around world size. """
        return (position[0] % self.world_width, position[1] % self.world_height)


    @classmethod
    def from_snapshot(world_cls, world_snapshot: "WorldSnapshot") -> "World":
        """ create world from snapshot. """
        return _world_from_snapshot(world_cls, world_snapshot)
    

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

    
        ###################################################


