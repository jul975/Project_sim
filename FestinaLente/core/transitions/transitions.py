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
    from core import Engine
    from ..domains.agent import Agent
    from ..domains.world import World    
###############################################################################################
# Formal agent transition order: =>    T = Π ∘ B ∘ D ∘ H ∘ M ∘ A

        # M: move agents
        # H: world.resolve_harvest()
        # R: world.resolve_reproduction()
        # G: world.resolve_agent_aging()
        # Π: commit births/deaths

# NOTE: 
    # - transition context holds intermediate data during transition phases, should be cleared at the end of each tick. 
    # - transition reports hold data about the outcomes of each phase, to be used for reporting and analytics.

##############################################################################################
# Regarding determinism:
    # - OccupancyIndex is a critical component regarding percervance of determinism, 
    
    # - OccupancyIndex gets created by iterating over sorted agents.id, insertion order is
    # preserved during the tick, and iteration order is deterministic as it relies on the underlying dict order, 
    # which is deterministic in python 3.7+.


##############################################################################################


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
    ''' TransitionContext:
        - holds intermediate data during transition phases
        - should be cleared at the end of each tick. 
        
    ---'''

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
    """ movement_phase(agents, world, context):
    """
    
    metabolic_deaths = DeathBucket()
    
    current_occupancy, age_dead_ids = OccupancyIndex.build_from_agents(agents)
    age_deaths = DeathBucket.fill_bucket_from_ids(age_dead_ids)
        # M

    occupied_cells : Iterable[tuple[Position, list["Agent"]]] = current_occupancy.occupied_items()
    for position, local_agents in occupied_cells:
        # note weights and temperature are hardcoded for now, 
        # need to be defined by regime compiler

        movement_range: MovementRange = sample_moves(position, world, current_occupancy, context.spatial_params)

        for agent in local_agents:
            if not agent.move_agent(movement_range.candidates, movement_range.probability):
                metabolic_deaths.agents_ids.append(agent.id)
                continue
            # NOTE: context.occupancy is still empty at this point,
            context.occupancy.add(agent)  # update occupancy with new position


        


    context.pending_deaths_by_cause["age_deaths"] = age_deaths
    context.pending_deaths_by_cause["metabolic_deaths"] = metabolic_deaths

    return MovementReport(
        metabolic_deaths_count = metabolic_deaths.count,
        age_deaths_count = age_deaths.count
        )


def interaction_phase(context : TransitionContext, world : "World") -> InteractionReport:
    """ 
    interaction_phase(context):
    """
    pending_starvation_death = DeathBucket()

    occupied_positions : OccupancyIndex = context.occupancy


    # H
    # NOTE: loop will need simplification, but for now this is the cleanest way to distribute resources while conserving energy and ensuring deterministic distribution of remainders.
    for position, local_agents in occupied_positions.occupied_items():
        world.harvest(local_agents, position)

        for agent in local_agents:
            if agent.energy_level <= 0:
                
                pending_starvation_death.agents_ids.append(agent.id)
                continue
            
            context.post_harvest_alive.append(agent)
        
    context.pending_deaths_by_cause["post_harvest_starvation"] = pending_starvation_death
        
    return InteractionReport(
        pending_starvation_death_count = pending_starvation_death.count)



def biology_phase(context : TransitionContext) -> BiologyReport:
    """ 
    biology_phase(context):
    """
    post_reproduction_death = DeathBucket()

    alive_agents = context.post_harvest_alive

    for agent in alive_agents:
        if agent.can_reproduce():
            if agent.does_reproduce():
                context.reproducing_agents.append(agent)
     
                if agent.energy_level <= 0:
                    post_reproduction_death.agents_ids.append(agent.id)

        agent.age_agent()
    context.pending_deaths_by_cause["post_reproduction_death"] = post_reproduction_death
    
    return BiologyReport(
        post_reproduction_death_count = post_reproduction_death.count,
        reproducing_agents_count = len(context.reproducing_agents) )
        
  
