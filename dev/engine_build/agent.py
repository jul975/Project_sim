
import numpy as np
# check logic and eff of type checking statements.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engineP4 import Engine



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

        self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)


        # create rngs for movement and reproduction.


        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)
        self.energy_rng = np.random.default_rng(self.energy_ss)


        # initialize position
        self.position : np.int64 = self.move_rng.integers(1, 30)
        self.alive : bool = True

        # setup energy level as static variable for now. 
        # current idea is that on initialization each agent has a certain energy range
        # gives it a inborn "fitness" will be used later
        self.energy_level = self.energy_rng.integers(20, 40)



        # idea is that this would create a 10% chance of reproducing per tick.
        self.p = 0.01 if not engine.change_condition else 0.02


    
         

    def step(self):        
        self.position += self.move_rng.choice([-1, 1])

        reproduce = self.repro_rng.random()
        if reproduce < self.p:
            ## create new agent => how to update sequence? => i would use parent_agents rng as a base so it is deterministic but different from parent and other children.
            return True
        return False

            



if __name__ == "__main__":
    pass