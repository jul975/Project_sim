
import numpy as np
# check logic and eff of type checking statements.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engineP4 import Engine
    from .snapshots import AgentSnapshot



from .snapshots import _agent_from_snapshot

from engine_build.dev.perf import PerfSink, NullPerfSink, measure_block


import time



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

# relocated temp for now bc of performance reasons.
moves = ((-1, 0), (1, 0), (0, -1), (0, 1))



class Agent:
    ''' agents should be a subclass in order to acces span new agent functionality cleanly. '''
    def __init__(self, engine : "Engine" , id : np.int64, agent_seed : np.random.SeedSequence, position : tuple[np.int64, np.int64] | None = None, perf : PerfSink | None = None) -> None:
        
        """ engine: Engine
        
                        id: np.int64
                agent_seed: np.random.SeedSequence
        """
        if perf is None:        
            self._init_identity(engine, id, agent_seed)
            self._init_lineage()
            self._init_rngs()
            self._init_state(position=position)
        else:
            t0 = time.perf_counter()

            measure_block(
                perf,
                "agent.__init__.total",
                lambda: self._init_identity(engine, id, agent_seed),
            )
            measure_block(
                perf,
                "agent.__init__.lineage",
                lambda: self._init_lineage(),
            )
            measure_block(
                perf,
                "agent.__init__.rngs",
                lambda: self._init_rngs(),
            )
            measure_block(
                perf,
                "agent.__init__.state",
                lambda: self._init_state(position=position),
            )
            perf.add_time("agent.__init__.total", time.perf_counter() - t0)

            
    def _init_identity(self, engine : "Engine" , id : np.int64, agent_seed : np.random.SeedSequence) -> None:
        """ initializes agent identity. """
        self.id : np.int64 = id
        self.engine : "Engine" = engine
        self.agent_seed : np.random.SeedSequence = agent_seed
        self.agent_spawn_count : np.int64 = 0
        self.age : np.int64 = 0
        self.agent_entropy : np.int64 = self.agent_seed.entropy
        self.agent_spawn_key : tuple[np.int64, ...] = self.agent_seed.spawn_key
        self.pool_size : np.int64 = self.agent_seed.pool_size


    def _init_lineage(self) -> None:
        """ initializes agent lineage. """
        self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)

    def _init_rngs(self) -> None:
        """ initializes agent rngs. """
        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)
        self.energy_rng = np.random.default_rng(self.energy_ss)
        

    def _init_state(self, position : tuple[np.int64, np.int64] | None = None) -> None:
        """ initializes agent state. """
        if position is None:
            self.position = tuple(self.move_rng.integers(0, self.engine.world_params.world_width, size=2) )
        else:
            self.position = position
        self.alive : bool = True
        self.energy_level = self.energy_rng.integers(self.engine.energy_params.energy_init_range[0], self.engine.energy_params.energy_init_range[1])




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