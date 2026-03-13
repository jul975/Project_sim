
import numpy as np
# check logic and eff of type checking statements.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engineP4 import Engine
    from .snapshots import AgentSnapshot



from .snapshots import _agent_from_snapshot



"""
GENERAL NOTES:
    - Deterministic flow is inbetween verisions right now, need to separate seed_sequences from 
      from further logic after initialization.

    - Agent replication should be achieved by using the parents repro_rng in order to create 
      a new child_seed

      => rn, confusion arises in flow of datastream as I'm refactoring the main architecture.

      => clear up dataflow and logic. need to build diagram to visualize it. 


    - Agent death is not implemented yet. if done, need to change ordering system into a dict like
    structure 






"""



"""
NOTE:
NumPy does not expose n_children_spawned in SeedSequence.

We emulate spawn counter restoration by extending spawn_key
with the stored spawn_count.

This preserves deterministic lineage for this engine
but does not reproduce NumPy internal state exactly.

SeedSequence is used here only as entropy mixer,
not as authoritative lineage tracker.
"""



class Agent:
    ''' agents should be a subclass in order to acces span new agent functionality cleanly. '''
    def __init__(self, engine : "Engine" , id : np.int64, agent_seed : np.random.SeedSequence) -> None:
        
        """ engine: Engine
        
                        id: np.int64
                agent_seed: np.random.SeedSequence
        """
        self.engine= engine
        self.id = id
        self.agent_seed = agent_seed

        # external spawn_count logic 
        self.agent_spawn_count = 0

        self.age = 0


        
        self.agent_entropy = self.agent_seed.entropy
        self.agent_spawn_key = self.agent_seed.spawn_key
        self.pool_size = self.agent_seed.pool_size


        self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)


        # create rngs for movement and reproduction.


        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)
        self.energy_rng = np.random.default_rng(self.energy_ss)

# NOTE: 
    
        # CAVE: upper bound exclusive but range is [0, world_width - 1] and [0, world_height - 1]) => ok
        # not rng consumption
        self.position : tuple[np.int64, np.int64] = tuple(self.move_rng.integers(0, engine.world_params.world_width, size=2) )
        self.alive : bool = True

        
        self.energy_level = self.energy_rng.integers(engine.energy_params.energy_init_range[0], engine.energy_params.energy_init_range[1])



        # idea is that this would create a 1% chance of reproducing per tick.
        self._assert_invariants()

    def _assert_invariants(self) -> None:
        """ asserts agent invariants. """

        # identity
        assert isinstance(self.id, int)
        assert self.id >= 0

        # engine reference
        assert self.engine is not None

        # position
        x, y = self.position
        assert 0 <= x < self.engine.world.world_width
        assert 0 <= y < self.engine.world.world_height

        # biological state
        assert self.age >= 0
        assert self.energy_level >= 0 or not self.alive

        # RNG integrity
        assert isinstance(self.move_rng, np.random.Generator)
        assert isinstance(self.repro_rng, np.random.Generator)
        assert isinstance(self.energy_rng, np.random.Generator)

        # lineage
        # RNG lineage invariant
        assert self.agent_spawn_count >= 0

        assert self.agent_seed.entropy == self.agent_entropy
        assert tuple(self.agent_seed.spawn_key) == tuple(self.agent_spawn_key)
        assert self.agent_seed.pool_size == self.pool_size





    def reproduce(self) -> np.random.SeedSequence:
        """ reproduces agent. """
        # I'm returning the child seed in order to maintain sep of consernce. reproduction should be a method of the engine. (for now)

        index = self.agent_spawn_count
        child_spawn_key = self.agent_spawn_key + (index,)
        child_seed = np.random.SeedSequence(
            entropy=self.agent_entropy,
            spawn_key=child_spawn_key,
            pool_size=self.pool_size
        )
        self.agent_spawn_count += 1
        return child_seed

    def harvest_resources(self, harvest : np.int64) -> None:
        """ harvests resources from current position. """
        self.energy_level += harvest




    @classmethod
    def from_snapshot(agent_cls, snapshot : "AgentSnapshot", engine : "Engine") -> "Agent":
        """ create agent from snapshot. """
        return _agent_from_snapshot(agent_cls, snapshot, engine)



    def move_agent(self) -> bool:
        # M, if energy <= 0, agent dies of metabolic starvation.
        self.energy_level -= self.engine.energy_params.movement_cost     
        moves = np.array([(-1, 0), (1, 0), (0, -1), (0, 1)])
        dx, dy = moves[self.move_rng.integers(0, 4)]
        
        x, y = self.position

        self.position = (x + dx, y + dy)


        self.position = self.engine.world.wrap_around(self.position)

        if self.energy_level <= 0:
            self.alive = False
            return False
        return True
    
    def can_reproduce(self) -> bool:
            """ check energy level"""
            if self.energy_level >= self.engine.energy_params.reproduction_threshold:
                return True
            return False
            
    def does_reproduce(self) -> bool:
            reproduce = self.repro_rng.random()
            if reproduce < self.engine.reproduction_probability:
                self.energy_level -= self.engine.energy_params.reproduction_cost
                return True
            return False
         

    def age_agent(self) -> None:
        
        

        

        # reproduction logic
        # NOTE: 
        #       -   gonna change >= to > but need to change in documentation first.
        self.age += 1
        if self.age >= self.engine.population_params.max_age:
            self.alive = False
        


        

            



if __name__ == "__main__":
    pass