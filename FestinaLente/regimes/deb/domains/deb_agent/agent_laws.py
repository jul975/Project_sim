
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


### CHILD INITIALIZATION
# child.structure_cm3 = birth_structure_cm3
# child.reserve_J = initial_birth_reserve_J
# child.maturity_J = 0.0 or birth_maturity_J
# child.repro_buffer_J = 0.0






def mobilize_reserve(
    state: SheepState,
    params: SheepParams,
) -> float:
    if params.use_simple_reserve_turnover:
        k_E = params.simple_reserve_turnover_rate_per_day
    else:
        L_cm = state.structure_cm3 ** (1.0 / 3.0)
        k_E = params.energy_conductance_cm_per_day / L_cm

    requested_J = state.reserve_J * k_E * params.dt_days
    mobilized_J = min(state.reserve_J, requested_J)

    state.reserve_J -= mobilized_J

    return mobilized_J



####### REPRODUCTION 

if mother.repro_buffer_J >= reproduction_cost_J:
    mother.repro_buffer_J -= reproduction_cost_J

    child = SheepState(
        reserve_J=initial_birth_reserve_J,
        structure_cm3=birth_structure_cm3,
        maturity_J=0.0,
        repro_buffer_J=0.0,
        age_days=0.0,
        alive=True,
    )


"""
v0:
    stage derived from structure_cm3

v1:
    stage derived from maturity_J
    structure_cm3 used for size, intake, maintenance, movement

v2:
    maturity thresholds calibrated so stage transitions happen near target mass/time

"""

@dataclass(frozen=True)
class SheepParams:
    dt_days: float = 1.0

    # DEB-style allocation
    v_conductance: float  = 0.02737

    kappa: float = 0.7978
    growth_efficiency: float = 0.7994
    reproduction_efficiency: float = 0.95

    # Structure/body scaffold
    birth_structure_cm3: float = 5_400.0
    juvenile_structure_cm3: float = 20_000.0
    adult_structure_cm3: float = 86_000.0
    max_structure_cm3: float = 86_000.0

    # Energy conversion
    structure_energy_density_J_per_cm3: float = 23_000.0

    # Maintenance
    somatic_maintenance_J_per_day_cm3: float = 2511.0
    maturity_maintenance_rate_per_day: float = 0.002

    # Feeding
    grass_energy_density_J_per_kg_DM: float = 18_000_000.0
    assimilation_efficiency: float = 0.45
    newborn_dmi_ratio_per_day: float = 0.00
    juvenile_dmi_ratio_per_day: float = 0.04
    adult_dmi_ratio_per_day: float = 0.025

    # Movement
    cell_size_m: float = 1.0
    cost_of_transport_J_per_kg_m: float = 2.0
    terrain_factor: float = 1.0

    # Maturity thresholds
    juvenile_maturity_threshold_J: float = 1_000_000.0
    adult_maturity_threshold_J: float = 10_000_000.0

    # Reproduction
    reproduction_cost_J: float = 8_000_000.0
    initial_birth_reserve_J: float = 2_000_000.0



def stage_from_structure(
    state: SheepState,
    params: SheepParams,
) -> SheepStage:
    if state.structure_cm3 < params.juvenile_structure_cm3:
        return SheepStage.NEW_BORN

    if state.structure_cm3 < params.adult_structure_cm3:
        return SheepStage.JUVENILE

    return SheepStage.ADULT

def stage_from_maturity(
    state: SheepState,
    params: SheepParams,
) -> SheepStage:
    if state.maturity_J < params.juvenile_maturity_threshold_J:
        return SheepStage.NEW_BORN

    if state.maturity_J < params.adult_maturity_threshold_J:
        return SheepStage.JUVENILE

    return SheepStage.ADULT


### feeding logic 

def body_mass_kg(state: SheepState) -> float:
    return state.structure_cm3 / 1000.0


def dmi_ratio_for_stage(
    stage: SheepStage,
    params: SheepParams,
) -> float:
    if stage == SheepStage.NEW_BORN:
        return params.newborn_dmi_ratio_per_day

    if stage == SheepStage.JUVENILE:
        return params.juvenile_dmi_ratio_per_day

    if stage == SheepStage.ADULT:
        return params.adult_dmi_ratio_per_day

    raise ValueError(f"Unknown stage: {stage}")


def feed_from_grass(
    state: SheepState,
    grass_kg_DM: float,
    params: SheepParams,
) -> tuple[float, float]:
    stage = stage_from_structure(state, params)

    intake_ratio = dmi_ratio_for_stage(stage, params)
    max_harvest_kg_DM = intake_ratio * body_mass_kg(state) * params.dt_days

    harvested_kg_DM = min(grass_kg_DM, max_harvest_kg_DM)

    assimilated_J = (
        harvested_kg_DM
        * params.grass_energy_density_J_per_kg_DM
        * params.assimilation_efficiency
    )

    state.reserve_J += assimilated_J
    grass_kg_DM -= harvested_kg_DM

    return grass_kg_DM, harvested_kg_DM


## mobilization logic and k split 
##NOTE pot prob
## maintenance + movement + growth

# bigger structure
# → bigger maintenance
# → bigger movement cost
# → bigger intake capacity



def mobilize_reserve(
    state: SheepState,
    mobilization_fraction_per_day: float,
    params: SheepParams,
) -> float:
    requested_J = (
        state.reserve_J
        * mobilization_fraction_per_day
        * params.dt_days
    )

    mobilized_J = min(state.reserve_J, requested_J)
    state.reserve_J -= mobilized_J

    return mobilized_J

mobilized_J = mobilize_reserve(
    state=state,
    mobilization_fraction_per_day=0.20,
    params=params,
)

somatic_branch_J = params.kappa * mobilized_J
development_branch_J = (1.0 - params.kappa) * mobilized_J


## Somatic branch 

def movement_cost_J(
    state: SheepState,
    distance_cells: float,
    params: SheepParams,
) -> float:
    stage = stage_from_structure(state, params)

    if stage == SheepStage.NEW_BORN:
        return 0.0

    distance_m = distance_cells * params.cell_size_m

    return (
        params.cost_of_transport_J_per_kg_m
        * body_mass_kg(state)
        * distance_m
        * params.terrain_factor
    )


def somatic_maintenance_J(
    state: SheepState,
    params: SheepParams,
) -> float:
    return (
        params.somatic_maintenance_J_per_day_cm3
        * state.structure_cm3
        * params.dt_days
    )


def apply_somatic_branch(
    state: SheepState,
    somatic_branch_J: float,
    distance_cells: float,
    params: SheepParams,
) -> None:
    maintenance_J = somatic_maintenance_J(state, params)
    move_J = movement_cost_J(state, distance_cells, params)

    required_J = maintenance_J + move_J
    surplus_J = somatic_branch_J - required_J

    if surplus_J < 0:
        deficit_J = -surplus_J

        if state.reserve_J >= deficit_J:
            state.reserve_J -= deficit_J
            surplus_J = 0.0
        else:
            state.alive = False
            return

    usable_growth_J = params.growth_efficiency * surplus_J

    delta_structure_cm3 = (
        usable_growth_J
        / params.structure_energy_density_J_per_cm3
    )

    state.structure_cm3 = min(
        state.structure_cm3 + delta_structure_cm3,
        params.max_structure_cm3,
    )


#### temp female cloning 

def maybe_reproduce(
    mother: SheepState,
    params: SheepParams,
) -> SheepState | None:
    """Temporary reproduction abstraction:
adult females reproduce clonally when the reproduction buffer reaches the offspring cost."""
    stage = stage_from_structure(mother, params)

    if stage != SheepStage.ADULT:
        return None

    if mother.repro_buffer_J < params.reproduction_cost_J:
        return None

    mother.repro_buffer_J -= params.reproduction_cost_J

    return SheepState(
        reserve_J=params.initial_birth_reserve_J,
        structure_cm3=params.birth_structure_cm3,
        maturity_J=0.0,
        repro_buffer_J=0.0,
        age_days=0.0,
        alive=True,
    )


## TICK DRAFT 

def step_sheep(
    state: SheepState,
    grass_kg_DM: float,
    distance_cells: float,
    params: SheepParams,
) -> tuple[float, SheepState | None]:
    if not state.alive:
        return grass_kg_DM, None

    # 1. Age
    state.age_days += params.dt_days

    # 2. Feed
    grass_kg_DM, harvested_kg_DM = feed_from_grass(
        state=state,
        grass_kg_DM=grass_kg_DM,
        params=params,
    )

    # 3. Mobilize reserve
    mobilized_J = mobilize_reserve(
        state=state,
        mobilization_fraction_per_day=0.20,
        params=params,
    )

    # 4. κ split
    somatic_branch_J = params.kappa * mobilized_J
    development_branch_J = (1.0 - params.kappa) * mobilized_J

    # 5. Pay somatic costs and grow
    apply_somatic_branch(
        state=state,
        somatic_branch_J=somatic_branch_J,
        distance_cells=distance_cells,
        params=params,
    )

    if not state.alive:
        return grass_kg_DM, None

    # 6. Pay development costs and mature/reproduce-buffer
    apply_development_branch(
        state=state,
        development_branch_J=development_branch_J,
        params=params,
    )

    if not state.alive:
        return grass_kg_DM, None

    # 7. Reproduce
    child = maybe_reproduce(state, params)

    return grass_kg_DM, child