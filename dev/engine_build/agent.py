
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

        
        self.agent_entropy = self.agent_seed.entropy
        self.agent_spawn_key = self.agent_seed.spawn_key
        self.pool_size = self.agent_seed.pool_size


        self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)


        # create rngs for movement and reproduction.


        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)
        self.energy_rng = np.random.default_rng(self.energy_ss)


        # initialize position
        self.position : np.int64 = self.move_rng.integers(1, 30)
        self.alive : bool = True

        
        self.energy_level = self.energy_rng.integers(20, 40)



        # idea is that this would create a 1% chance of reproducing per tick.
        self.p = 0.01 if not engine.change_condition else 0.02

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

        instance.position = snapshot["position"]
        instance.alive = snapshot["alive"]
        instance.energy_level = snapshot["energy_level"]

        # seed reconstruction 
        instance.agent_seed = reconstruct_seed_seq(snapshot["agent_seed"], instance.agent_spawn_count)
        
        # redundant clones 
        #instance.move_ss = reconstruct_seed_seq(snapshot["move_ss"])
        #instance.repro_ss = reconstruct_seed_seq(snapshot["repro_ss"])
        #instance.energy_ss = reconstruct_seed_seq(snapshot["energy_ss"])


        instance.move_rng = reconstruct_rng(snapshot["move_rng"])
        instance.repro_rng = reconstruct_rng(snapshot["repro_rng"])
        instance.energy_rng = reconstruct_rng(snapshot["energy_rng"])

        instance.p = 0.01 if not engine.change_condition else 0.02


        return instance

    
         

    def step(self) -> bool:        
        self.position += self.move_rng.choice([-1, 1])

        reproduce = self.repro_rng.random()
        if reproduce < self.p:
            ## create new agent => how to update sequence? => i would use parent_agents rng as a base so it is deterministic but different from parent and other children.
            return True
        return False

            



if __name__ == "__main__":
    pass