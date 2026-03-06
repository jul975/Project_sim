
import numpy as np
# check logic and eff of type checking statements.
from typing import TYPE_CHECKING
from .seed_seq_utils import reconstruct_seed_seq

if TYPE_CHECKING:
    from .engineP4 import Engine


from .rng_utils import reconstruct_rng


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
    # need to change created agent spam logic NOW, wil be spread to much.  
        # initialize position
        self.position : np.int64 = self.move_rng.integers(0, engine.world_size)
        self.alive : bool = True

        
        self.energy_level = self.energy_rng.integers(engine.config.energy_init_range[0], engine.config.energy_init_range[1])



        # idea is that this would create a 1% chance of reproducing per tick.
        self.p = engine.config.reproduction_probability if not engine.world.change_condition else engine.config.reproduction_probability_change_condition

    def reproduce(self) -> np.random.SeedSequence:
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
    def from_snapshot(cls, snapshot, engine : "Engine") -> "Agent":
        """ create agent from snapshot. """
        # use reconstruct_rng() from rng_utils.py to reconstruct rngs.

        instance = object.__new__(cls)

        # set agent properties 
        # named it instance to make clear distinction

        instance.agent_spawn_count = snapshot["agent_spawn_count"]


        
        # seed sequence properties
        agent_seed_dict = snapshot["agent_seed"]
        instance.agent_entropy = agent_seed_dict["entropy"]
        instance.agent_spawn_key = agent_seed_dict["spawn_key"]
        instance.pool_size = agent_seed_dict["pool_size"]

        
        instance.engine = engine
        instance.id = snapshot["id"]
        instance.age = snapshot["age"]

        instance.position = snapshot["position"]
        instance.alive = snapshot["alive"]
        instance.energy_level = snapshot["energy_level"]

        # seed reconstruction 
        instance.agent_seed = reconstruct_seed_seq(snapshot["agent_seed"], instance.agent_spawn_count)
        



        instance.move_rng = reconstruct_rng(snapshot["move_rng"])
        instance.repro_rng = reconstruct_rng(snapshot["repro_rng"])
        instance.energy_rng = reconstruct_rng(snapshot["energy_rng"])

        instance.p = engine.config.reproduction_probability if not engine.world.change_condition else engine.config.reproduction_probability_change_condition


        return instance

    def move_agent(self) -> bool:
        # M, if energy <= 0, agent dies of metabolic starvation.
        self.energy_level -= self.engine.energy_params.movement_cost     
        self.position += self.move_rng.choice([-1, 1])
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
            if reproduce < self.p:
                self.energy_level -= self.engine.energy_params.reproduction_cost
                return True
            return False
         

    def age_agent(self) -> None:
        
        

        

        # reproduction logic
        # NOTE: 
        #       -   gonna change >= to > but need to change in documentation first.
        self.age += 1
        if self.age >= self.engine.max_age:
            self.alive = False
        


        

            



if __name__ == "__main__":
    pass