
from dataclasses import dataclass

import numpy as np

from FestinaLente.core.contracts.step_results import AgentSetup
from FestinaLente.regimes.deb.universal_laws.agent_phases import EnergyState, EnergyParams
from FestinaLente.regimes.deb.universal_laws.agent_phases import mobilization_phase, branch_split_phase, maintenance_phase, movement_phase, growth_phase, maturity_reproduction_phase
'''
NOTE: 
    on engine, only use hash, to interact with agent collection
    agent id, ech cluster in birth and death id's

    tick budget containing branched energy deviations reset each tick, 

'''
@dataclass(frozen=True)
class AgentCreationID:
    owned_id : int
    parent_id: int
    
@dataclass(frozen=True)
class AgentDeathID:
    owned_id : int
    perent_id: int
    offspring_count: int
    age : int

    # offspring_index: []
    # cause and other metadata as well? 
    cause: str

@dataclass(frozen=True)
class PhysiologySpec:
    """Model concept	AmP anchor
    -> species specific physiological parameters, which are used to compute energy flow and life history events.
    -> v, kap, kap_R, p_M, k_J, E_G, E_Hb, E_Hx, E_Hp"""
    v: float                # cm/day
    kappa: float
    kappa_R: float

    p_M: float              # J/day/cm^3
    E_G: float              # J/cm^3
    k_J: float              # 1/day

    E_Hb: float             # birth threshold
    E_Hx: float             # weaning / movement threshold
    E_Hp: float             # puberty threshold

    reserve_init_fraction: float
    structure_init_volume: float

class DerivedPhysiologySpec:
    """ derived parameters for convenience, to avoid repeated calculations. """
    cPar = parscomp_st(par)
    E_Rb: float             # reproduction buffer at birth, J
    E_Rp: float             # reproduction buffer at puberty, J


@dataclass
class AgentState:
    agent_id: int 
    offspring_count: int
    age: float 

    reserve_energy: float        # J
    position: tuple[int, int]  # (x, y) coordinates => as of now, spatial only on engine level, 
    structural_volume: float     # cm^3
    maturity: float              # J
    reproduction_buffer: float   # J
    age_days: int
    alive: bool = True

    # movement cost J in state

@dataclass
class PreMovementResult:
    alive : bool
    movement_cost_j: float




class DEBAgent:
    def __init__(self, agent_setup : AgentSetup ,initial_state: EnergyState, params: EnergyParams):
        
        self._init_rngs(agent_setup)
        self.state = initial_state
        self.params = params

    def _init_rngs(self, agent_setup : AgentSetup) -> None:
        """ initializes agent lineage. """
        

        self.move_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (MOVEMENT,)))
        self.repro_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (REPRODUCTION,)))
        self.energy_rng = np.random.Generator(np.random.PCG64(agent_setup.identity_words + (ENERGY,)))


        return 
    
    def early_tick_energy_update(self, dt: float) :
        """
        update pre-movement energy steps, e.g. mobilization, branch split, maintenance, movement cost deduction, etc."""
        # 0. add assimilation energy to reserve (not implemented yet, so assume constant reserve for now)
        
        # 1. Mobilization phase
        mobilized_energy = mobilization_phase(self.state, self.params, dt)

        # 2. Branch split phase
        branch_budget = branch_split_phase(mobilized_energy, self.params)

        # 3. Maintenance phase
        maintenance_result = maintenance_phase(self.state, self.params, dt, branch_budget)


        return

    def move_agent(self, dt: float):
        """ movement phase, which deducts movement cost from soma budget, and returns movement result for use in growth phase. """
        movement_result = movement_phase(self, branch_budget.soma_budget_J, self.params, dt)
        return movement_result




    def step(self, dt: float):

        self.early_tick_energy_update(dt)
       
        # 4. Movement phase (placeholder)
        movement_result = movement_phase(self, branch_budget.soma_budget_J, self.params, dt)

        # 5. Growth phase
        growth_result = growth_phase(self.state, branch_budget.soma_budget_J - movement_result.movement_cost_J, self.params, dt)

        # 6. Maturity/Reproduction phase
        maturity_result = maturity_reproduction_phase(self.state, branch_budget.maturity_repro_budget_J, self.params)

        # 7. Harvest 

        # 8. Update state variables, e.g. age, offspring count, etc.
        self.state += dt