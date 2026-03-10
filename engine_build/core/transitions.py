from dataclasses import dataclass , field
from typing import TYPE_CHECKING

from .step_results import MovementReport, InteractionReport, BiologyReport
from .world import World

from typing import List

if TYPE_CHECKING:
    from .agent import Agent
    

"""


            Formal agent transition order: =>    T = Π ∘ B ∘ D ∘ H ∘ M ∘ A



Transition layer: the engine's authoritative view of world-state mutation.

Engine.step()
    orchestrates transitions

Transitions
    compute state changes

Engine
    commits changes

Execution flow:
    Agents + World (state_t)
        -> Transition functions
        -> Pending state changes
        -> Commit
        -> Agents + World (state_t+1)

Treat each tick as a transaction log.

Example (tick 1023):
- Deaths: starvation [4, 9, 22]
- Births: parents 11, 17
- Energy changes: agent 3 +2, agent 7 +1
- World changes: cell (10, 4) -3 resources

Apply the transaction only at commit.

Conceptual engine-loop order:
1. Move agents
2. Build spatial groups
3. Harvest resources
4. Determine reproduction
5. Age agents
6. Aggregate death buckets
7. Compute capacity
8. Commit births
9. Commit deaths
10. Regrow resources
11. Advance tick



Engine.step()

    context = TransitionContext()

    movement_phase(context)

    interaction_phase(context)

    biology_phase(context)

    commit(context)

    world_update()

TransitionContext
    occupied_positions
    death_buckets
    reproducing_agents
    energy_deltas
    metrics
"""


# Phase 1 — Movement

#     occupied_positions
#     metabolic deaths

# Phase 2 — Local Interactions

#     harvest plants
#     predation
#     competition
#     resource consumption
# Phase 3 — Biological Updates
# => individual bilogical processes
#     aging
#     disease progression
#     fertility changes
#     reproduction eligibility
# Phase 4 — Structural Commit

#     delete dead agents
#     create new agents
#     update world
#     increment tick


@dataclass
class DeathBucket:
    """ DeathBucket: holds agent ids container for a given death cause. """
    agents_ids: List[int] = field(default_factory=list)
    @property
    def count(self) -> int:
        return len(self.agents_ids)




@dataclass
class TransitionContext:
    occupied_positions : dict[tuple[int, int], list["Agent"]] = field(default_factory=dict)
    post_harvest_alive : list["Agent"] = field(default_factory=list)
    pending_deaths_by_cause: dict[str, DeathBucket] = field(default_factory=dict)
    reproducing_agents : list["Agent"] = field(default_factory=list)
    # energy_deltas : dict[int, int] 



###############################################################################################

        # M: move agents
        # H: world.resolve_harvest()
        # R: world.resolve_reproduction()
        # G: world.resolve_agent_aging()
        # Π: commit births/deaths

##############################################################################################


def movement_phase(agents : list[int, Agent] , context : TransitionContext) -> MovementReport:
    """ movement_phase(agents, world, context):
    """

    
    age_deaths = DeathBucket()
    metabolic_deaths = DeathBucket()

    sorted_agents = sorted(agents.items())

    for agent_id, agent in sorted_agents:
        # A
        # age check, if agent is older than max_age, agent.alive = False set on last agent tick 
        if not agent.alive:
            age_deaths.agents_ids.append(agent_id)
            continue
        # M
        if not agent.move_agent():
            metabolic_deaths.agents_ids.append(agent_id)
            continue

        if agent.position in context.occupied_positions:
            context.occupied_positions[agent.position].append(agent)
        else:
            context.occupied_positions[agent.position] = [agent]


    context.pending_deaths_by_cause["age_deaths"] = age_deaths
    context.pending_deaths_by_cause["metabolic_deaths"] = metabolic_deaths

    return MovementReport(
        metabolic_deaths_count = metabolic_deaths.count,
        age_deaths_count = age_deaths.count
        )

###########################################################
def interaction_phase(context : TransitionContext, world : World) -> InteractionReport:
    """ 
    interaction_phase(context):
    """
    pending_starvation_death = DeathBucket()

    occupied_positions = context.occupied_positions


    # H
    for position, local_agents in occupied_positions.items():
        world.harvest(local_agents, position)
        
        
        for agent in local_agents:
            if agent.energy_level <= 0:
                
                pending_starvation_death.agents_ids.append(agent.id)
                continue
            
            context.post_harvest_alive.append(agent)
        
    context.pending_deaths_by_cause["post_harvest_starvation"] = pending_starvation_death
        
    return InteractionReport(
        reproducing_agents_count = len(context.reproducing_agents),
        pending_starvation_death_count = pending_starvation_death.count)
    

        
            


            
            


###########################################################################        
def biology_phase(context : TransitionContext) -> BiologyReport:

    post_reproduction_death = DeathBucket()

    alive_agents = context.post_harvest_alive

    for agent in alive_agents:
        if agent.can_reproduce():
            if agent.does_reproduce():
                context.reproducing_agents.append(agent)
     
                if agent.energy_level <= 0:
                    post_reproduction_death.agents_ids.append(agent.id)
                continue

        agent.age_agent()
        context.pending_deaths_by_cause["post_reproduction_death"] = post_reproduction_death
    
    return BiologyReport(
        post_reproduction_death_count = post_reproduction_death.count,
        reproducing_agents_count = len(context.reproducing_agents) )
        
        
    ########################### NOTE: BELOW THIS line is not yet implemented, will be part of the metrics pipline  !! 
        
        
        
        # agents state updates
            
        # capacity calculations
        # NOTE: 
            # Take sum of all bucket counts to get total death count

       
        # commit to population changes
        # NOTE: Keep an eye on this step!! 
            # CAVE: current system logic regarding age incrementation, 
            # currently agents live through ticks, the "delta t" their transitioning over is defined by the end of the last step. 
            # as agent.alive gets evaluated at the beginning of the step, they die at the beginning of the tick.
            # => agents die at the beginning of the tick, but their death is only committed at the end of the tick. 

        # D

########################################################################






























    """NOTE:
        1) Mutation is localised

            World → resources mutate
            Agent → energy mutates
            Engine → population mutates

        2) Commit still happens only at engine level

            Births/deaths are still pending collections, not immediate structural mutations.

        3) Ordering is explicit

            Move → Harvest → Reproduce → Age → Commit
            So should ensure architectural stability.
            
            """
        
    