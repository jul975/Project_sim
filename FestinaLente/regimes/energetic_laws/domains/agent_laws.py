
import numpy as np
from dataclasses import dataclass


## DEB scaffold for energy laws. 




## Agent_energy_reserve 


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
'''MOVEMENT : int = 1
REPRODUCTION : int = 2
ENERGY : int = 3

class Agent:
    
    def __init__(self, engine : "Engine" , id : np.int64, agent_setup : AgentSetup, position : tuple[np.int64, np.int64] | None = None) -> None:
        """ engine: Engine
                        id: np.int64
                agent_setup: AgentSetup
        """
        self._init_identity(engine, id)
        self._init_rngs(agent_setup)
        self._init_state(position=position)
        
    def _init_identity(self, engine : "Engine" , id : np.int64) -> None:
        """ initializes agent identity. """
        self.id : np.int64 = id
        self.engine : "Engine" = engine
        self.offspring_count : np.int64 = 0
        self.age : np.int64 = 0


    def _init_rngs(self, agent_setup : AgentSetup) -> None:
        """ initializes agent lineage. """
    
        self.move_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (MOVEMENT,)))
        self.repro_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (REPRODUCTION,)))
        self.energy_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (ENERGY,)))

        return 

    def _init_state(self, position : tuple[np.int64, np.int64] | None = None) -> None:
        """ initializes agent state. """
        if position is None:
            self.position = tuple(self.move_rng.integers(0, self.engine.world_params.world_width, size=2) )
        else:
            self.position = position
        self.alive : bool = True
        self.energy_reserve = self.energy_rng.integers(self.engine.energy_params.energy_init_range[0], self.engine.energy_params.energy_init_range[1])

'''

@dataclass
class SheepState:
    reserve_J: float          # E: spendable reserve energy
    structure_cm3: float      # V: physical structure/body volume
    maturity_J: float         # E_H: developmental state
    repro_buffer_J: float     # E_R: adult reproductive buffer
    age_days: float
    alive: bool = True