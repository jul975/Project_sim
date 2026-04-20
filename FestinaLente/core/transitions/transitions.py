from dataclasses import dataclass , field
from typing import TYPE_CHECKING

from scipy import spatial

from FestinaLente.core.spatial.neighborhood import MovementRange
from FestinaLente.regimes.compiled import SpatialParams

from ..contracts.step_results import MovementReport, InteractionReport, BiologyReport
from ..spatial.occupancy_index import OccupancyIndex, Position


from collections.abc import Iterable
from ..spatial.neighborhood import sample_moves

from typing import List

if TYPE_CHECKING:
    from ..domains.agent import Agent
    from ..domains.world import World    
###############################################################################################
# Formal tick order: movement → interaction → biology → commit → tick increment
#
# TransitionContext holds intermediate phase results. See DETERMINISM.md for:
# - "World / OccupancyIndex / TransitionContext Contract" (State Freezing pattern)
# - "Explicit Local Ordering Guarantee" (deterministic iteration order)
###############################################################################################


@dataclass
class DeathBucket:
    """ DeathBucket: 
        - agent ids container, used as pending death value entry,
        - key is cause of death that gets defined upstream. """
    agents_ids: List[int] = field(default_factory=list)
    @property
    def count(self) -> int:
        return len(self.agents_ids)
    
    @classmethod
    def fill_bucket_from_ids(cls, agents_ids: List[int]) -> "DeathBucket":
        """ fill_bucket_from_ids(agents_ids):
        creates a DeathBucket from a list of agent ids. """
        return cls(agents_ids=agents_ids)




@dataclass
class TransitionContext:
    """TransitionContext: intermediate state holder for a single tick's phase computation.
    
    **Part of the State Freezing pattern** — see DETERMINISM.md "World / OccupancyIndex / 
    TransitionContext Contract".
    
    Lifecycle:
    - Created at start of Engine.step()
    - Populated by each phase (movement → interaction → biology)
    - Applied atomically in commit_phase()
    - Discarded at end of tick
    
    Responsibilities:
    - occupancy: spatial index (built in movement, frozen for rest of tick)
    - pending_deaths_by_cause: agent IDs queued for removal (categorized)
    - post_harvest_alive: agents surviving harvest
    - reproducing_agents: agents queued for birth
    
    Invariant: Never persisted. Always cleared at tick end.
    
    Commit order (deterministic):
    1. Remove all pending deaths
    2. Create births (limited by capacity)
    3. Regrow resources
    """
    spatial_params : SpatialParams = field(default_factory=SpatialParams)
    occupancy : OccupancyIndex = field(default_factory=OccupancyIndex)
    post_harvest_alive : list["Agent"] = field(default_factory=list)
    pending_deaths_by_cause: dict[str, DeathBucket] = field(default_factory=dict)
    reproducing_agents : list["Agent"] = field(default_factory=list)
    # energy_deltas : dict[int, int]





def movement_phase(
        agents : dict[int, "Agent"] , 
        context : TransitionContext, 
        world : "World"
        ) -> MovementReport:
    """Movement phase: update agent positions and build occupancy index for the tick.
    
    Steps:
    1. Age check: identify agents >= max_age (queued for death)
    2. Build fresh OccupancyIndex from agents in encounter order
    3. For each cell, sample movement candidates (softmax by resource + crowding)
    4. Move agents, deduct energy, check for metabolic death
    5. Update context.occupancy as agents move (frozen after this phase)
    
    Frozen at end of this phase: context.occupancy is used by interaction/biology phases.
    
    See DETERMINISM.md "World / OccupancyIndex / TransitionContext Contract" for 
    the occupancy freeze guarantee.
    """
    
    metabolic_deaths = DeathBucket()
    
    current_occupancy, age_dead_ids = OccupancyIndex.build_from_agents(agents)
    age_deaths = DeathBucket.fill_bucket_from_ids(age_dead_ids)

    occupied_cells : Iterable[tuple[Position, list["Agent"]]] = current_occupancy.occupied_items()
    for position, local_agents in occupied_cells:
        # note weights and temperature are hardcoded for now, 
        # need to be defined by regime compiler

        movement_range: MovementRange = sample_moves(position, world, current_occupancy, context.spatial_params)

        for agent in local_agents:
            if not agent.move_agent(movement_range.candidates, movement_range.probability):
                metabolic_deaths.agents_ids.append(agent.id)
                continue
            context.occupancy.add(agent)  # update occupancy with new position


        


    context.pending_deaths_by_cause["age_deaths"] = age_deaths
    context.pending_deaths_by_cause["metabolic_deaths"] = metabolic_deaths

    return MovementReport(
        metabolic_deaths_count = metabolic_deaths.count,
        age_deaths_count = age_deaths.count
        )


def interaction_phase(context : TransitionContext, world : "World") -> InteractionReport:
    """Interaction phase: harvest resources and check for starvation death.
    
    Steps:
    1. For each occupied cell (in order from OccupancyIndex):
       - Harvest resources deterministically (all agents in cell get share)
       - Remainder distributed to first r agents in local encounter order
    2. Check each agent's post-harvest energy
    3. Alive agents added to post_harvest_alive; dead queued for death
    
    Uses frozen context.occupancy (from movement phase).
    
    See DETERMINISM.md "Explicit Local Ordering Guarantee" for harvest distribution order.
    """
    pending_starvation_death = DeathBucket()

    occupied_positions : OccupancyIndex = context.occupancy

    for position, local_agents in occupied_positions.occupied_items():
        world.harvest(local_agents, position)

        for agent in local_agents:
            if agent.energy_reserve <= 0:
                
                pending_starvation_death.agents_ids.append(agent.id)
                continue
            
            context.post_harvest_alive.append(agent)
        
    context.pending_deaths_by_cause["post_harvest_starvation"] = pending_starvation_death
        
    return InteractionReport(
        pending_starvation_death_count = pending_starvation_death.count)



def biology_phase(context : TransitionContext) -> BiologyReport:
    """Biology phase: reproduction and aging.
    
    Steps:
    1. For each agent that survived harvest:
       - Check if can reproduce (energy >= reproduction_cost)
       - Sample reproduction Bernoulli
       - If reproducing: queue for birth, pay energy cost, check if energy <= 0
       - Age the agent (increment age counter)
    2. Agents dying from post-reproduction energy depletion queued for death
    
    Determinism: uses post_harvest_alive from interaction phase (in encounter order).
    Birth queue order determines child ID order during commit.
    """
    post_reproduction_death = DeathBucket()

    alive_agents = context.post_harvest_alive

    for agent in alive_agents:
        if agent.can_reproduce():
            if agent.does_reproduce():
                context.reproducing_agents.append(agent)
     
                if agent.energy_reserve <= 0:
                    post_reproduction_death.agents_ids.append(agent.id)

        agent.age_agent()
    context.pending_deaths_by_cause["post_reproduction_death"] = post_reproduction_death
    
    return BiologyReport(
        post_reproduction_death_count = post_reproduction_death.count,
        reproducing_agents_count = len(context.reproducing_agents) )
        
  
