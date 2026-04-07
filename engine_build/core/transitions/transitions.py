from dataclasses import dataclass , field
from typing import TYPE_CHECKING

from ..contracts.step_results import MovementReport, InteractionReport, BiologyReport
from ..spatial.occupancy_index import OccupancyIndex

from typing import List

if TYPE_CHECKING:
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
    """ DeathBucket: holds agent ids container for a given death cause. """
    agents_ids: List[int] = field(default_factory=list)
    @property
    def count(self) -> int:
        return len(self.agents_ids)




@dataclass
class TransitionContext:
    ''' TransitionContext:
        - holds intermediate data during transition phases
        - should be cleared at the end of each tick. 
        
    ---'''
    occupancy : OccupancyIndex = field(default_factory=OccupancyIndex)
    post_harvest_alive : list["Agent"] = field(default_factory=list)
    pending_deaths_by_cause: dict[str, DeathBucket] = field(default_factory=dict)
    reproducing_agents : list["Agent"] = field(default_factory=list)
    # energy_deltas : dict[int, int]





def movement_phase(agents : dict[int, "Agent"] , context : TransitionContext) -> MovementReport:
    """ movement_phase(agents, world, context):
    """

    
    age_deaths = DeathBucket()
    metabolic_deaths = DeathBucket()


    for agent_id,  agent in agents.items():
        # A
        # age check, if agent is older than max_age, agent.alive = False set on last agent tick 
        if not agent.alive:
            age_deaths.agents_ids.append(agent_id)
            continue
        # M
        if not agent.move_agent():
            metabolic_deaths.agents_ids.append(agent_id)
            continue

        context.occupancy.add(agent)


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
        
  