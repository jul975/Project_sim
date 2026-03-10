from dataclasses import dataclass
from typing import TYPE_CHECKING

from .step_results import DeathBucket, MovementReport, InteractionReport, BiologyReport
from .world import World

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


# NOTE: is deachtbucket relevant here? I think not but keep it for now
@dataclass
class TransitionContext:
    occupied_positions : dict[tuple[int, int], list["Agent"]] 
    pending_agent_iteration_death: dict[str: DeathBucket]
    reproducing_agents : list["Agent"] 
    # energy_deltas : dict[int, int] 


###############################################################################################


"""
        context = TransitionContext()

        movement_report = movement_phase(context)
        interaction_report = interaction_phase(context)
        biology_report = biology_phase(context)

        commit(context)

        step_result = StepResult.from_phase_reports(...)
                
        return step_result
        
        
        
        """




        # M: move agents
        # H: world.resolve_harvest()
        # R: world.resolve_reproduction()
        # G: world.resolve_agent_aging()
        # Π: commit births/deaths






##############################################################################################


def movement_phase(agents : dict[int, Agent], world : World , context : TransitionContext) -> MovementReport:

    
    age_deaths = DeathBucket()
    metabolic_deaths = DeathBucket()

    sorted_agents = sorted(agents.items())

    for agent_id, agent in sorted_agents:
        # A
        # age check, if agent is older than max_age, agent.alive = False set on last agent tick 
        if not agent.alive:
            age_deaths.count += 1
            age_deaths.agents.append(agent_id)
            continue
        # M
        if not agent.move_agent():
            metabolic_deaths.count += 1
            metabolic_deaths.agents.append(agent_id)
            continue

        if agent.position in context.occupied_positions:
            context.occupied_positions[agent.position].append(agent)
        else:
            context.occupied_positions[agent.position] = [agent]

    return MovementReport(metabolic_deaths, age_deaths)

###########################################################
def interaction_phase(context : TransitionContext) -> InteractionReport:
    """ 
    interaction_phase(context):

    for position, agents in occupied_positions:

        harvest = world.harvest(...)

        evaluate starvation

        evaluate reproduction

        evaluate aging"""
    
        reproducing_agents , pending_world_death = self.world.resolve_harvest_world(occupied_positions)
        pending_death : dict[str, DeathBucket] = pending_agent_iteration_death | pending_world_death
        
            


            
            


###########################################################################        
def biology_phase(context : TransitionContext) -> BiologyReport:
        # agents state updates
            
        # capacity calculations
        # NOTE: 
            # Take sum of all bucket counts to get total death count
        deaths_this_tick = sum(death_bucket.count for death_bucket in pending_death.values())
        effective_population = len(self.agents) - deaths_this_tick 
        available_capacity = self.max_agent_count - effective_population
        reproducers_to_commit = reproducing_agents[:available_capacity]

        
       
       
       
        # commit to population changes
        # NOTE: Keep an eye on this step!! 
            # CAVE: current system logic regarding age incrementation, 
            # currently agents live through ticks, the "delta t" their transitioning over is defined by the end of the last step. 
            # as agent.alive gets evaluated at the beginning of the step, they die at the beginning of the tick.
            # => agents die at the beginning of the tick, but their death is only committed at the end of the tick. 

        # D

########################################################################
def commit_phase(context : TransitionContext) -> None:
        for death_bucket in pending_death.values():
            for agent_id in death_bucket.agents:
                assert agent_id in self.agents
                del self.agents[agent_id]
                

        # B
        for parent_agent in reproducers_to_commit:
            self.create_new_agent(parent_agent)


        # world state update 
        self.world.regrow_resources()
        self.world.tick += 1





































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
            
        