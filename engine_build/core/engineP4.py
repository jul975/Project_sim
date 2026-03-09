import numpy as np
import hashlib

from .state_schema import get_state_bytes

from .snapshots import engine_to_snapshot, engine_from_snapshot

from .agent import Agent
from .world import World


from .step_results import DeathBucket, StepMetrics

from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiled import EnergyParams, ReproductionParams, ResourceParams, LandscapeParams, PopulationParams, WorldParams

from dataclasses import asdict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .snapshots import EngineSnapshot


"""
    NOTE: 
            Engine invariants:
                                1) Spatial invariant
                                                    0 ≤ position < world_size

                                                    Because toroidal normalization guarantees this.

                                2) Identity invariant
                                                    agent.id matches dict key

                                                    Useful later when deletion/reordering occurs.

                                3) Population invariant
                                                    len(agents) ≤ max_agent_count

                                                    Prevents overflow bugs.

                                4) Energy invariant (optional)
                                                    energy_level ≥ 0  OR  agent.alive == False
"""

class Engine:
    def __init__(self, seed_seq : np.random.SeedSequence , config : CompiledRegime ,change_condition=False) -> None:


        self.master_ss = seed_seq
        world_seed: np.random.SeedSequence = self.master_ss.spawn(1)[0]

        self.config : CompiledRegime = config
        
        self.energy_params : EnergyParams = self.config.energy_params  
        self.reproduction_params : ReproductionParams = self.config.reproduction_params
        self.resource_params : ResourceParams = self.config.resource_params
        self.landscape_params : LandscapeParams = self.config.landscape_params
        self.population_params : PopulationParams = self.config.population_params
        self.world_params : WorldParams = self.config.world_params

        self.max_agent_count = self.population_params.max_agent_count
        self.next_agent_id = self.population_params.initial_agent_count
        self.max_age = self.population_params.max_age
        
        self.world = World( world_seed, self.config ,change_condition)
        
        self.agents : dict[int, Agent] = self.initialize_state(self.next_agent_id) 

        self._assert_invariants()


        
        
    def _assert_invariants(self) -> None:
        """Validate global engine state."""

        # population constraint
        assert len(self.agents) <= self.max_agent_count

        # ID allocation safety
        assert self.next_agent_id > max(self.agents, default=-1)

        # agent integrity
        for agent_id, agent in self.agents.items():

            # ID consistency
            assert agent_id == agent.id

            # spatial bounds
            x, y = agent.position
            assert 0 <= x < self.world_params.world_width
            assert 0 <= y < self.world_params.world_height

            # biological constraints
            assert agent.age >= 0
            assert agent.age <= self.max_age
            assert agent.energy_level >= 0 or not agent.alive

        # world compatibility
        assert self.world.world_width == self.world_params.world_width
        assert self.world.world_height == self.world_params.world_height

        # id allocation corruption
        assert all(agent.id < self.next_agent_id for agent in self.agents.values())



    def initialize_state(self, agent_count) -> dict[np.int64, Agent]:
        """ creates initial agent population. """
        agent_seeds = self.master_ss.spawn(agent_count)

        return {i : Agent(self, i, agent_seeds[i]) for i in range(agent_count)}
    


    # NOTE: temp 
    def check_initial_population_spread(self) -> None:
        """ checks initial population spread. => not wired yet, needs to check if it's necessary. """
        density = np.zeros((self.world_params.world_height, self.world_params.world_width))

        for agent in self.agents.values():
            x, y = agent.position
            density[y, x] += 1
    

    
    def create_new_agent(self, parent_agent : Agent) -> None:
        """ creates new agent from parent_agent. """
        

        child_seed = self.get_child_seed(parent_agent)
        
        self.agents[self.next_agent_id] = Agent( self , self.next_agent_id , child_seed)
        self.agents[self.next_agent_id].position = parent_agent.position
        self.next_agent_id += 1


    def get_child_seed(self, parent_agent : Agent) -> np.random.SeedSequence:
        """ gets child seed from parent_agent. """
        return parent_agent.reproduce()


    def get_agent_count(self) -> np.int64:
        """ returns agent count. """
        return len(self.agents)

    def __eq__(self, other) -> bool:
        """ compares two engine objects. """
        if not isinstance(other, Engine):
            return NotImplemented
        
        return self.get_state_hash() == other.get_state_hash()
        """        pending_death: dict[str: [Agent]] = {
            "old_age" : DeathBucket(),
            "metabolic_starvation" : DeathBucket(),
            "post_harvest_starvation" : DeathBucket(),
            "post_reproduction_death" : DeathBucket()
            }"""



    def step(self) -> tuple[np.int64, np.int64, dict[str, DeathBucket]]:
        """ restructuring step method in order to evaluate agents for death and birth together. 
            After evaluation, available capacity gets calculated to avoid undershoot of agent capacity."""
        

        pending_agent_iteration_death: dict[str: [DeathBucket]] = {
            "old_age" : DeathBucket(),
            "metabolic_starvation" : DeathBucket()
            }
        
        reproducing_agents: list[Agent] = []



        sorted_agents = sorted(self.agents.items())


        ''' NOTE: 

                Formal agent transition order: =>    T = Π ∘ B ∘ D ∘ H ∘ M ∘ A

            -   Agent state updated is followed by a state evaluation on engine level

            -   The evaluation does NOT influence determenism as it holds only references to the agents marked 
                for their respective state AFTER step is implemented, further processing happens after 
                all states have been updated 


            - CAVE: ORDERING OF DEATH AND BIRTH IS IMPORTANT! 
                    => RIGHT NOW, DEATH OCCURS BEFORE BIRTH. !!!!!!!

        
        
                    
            - CAVE: need to formulate engine stepping logic cleary in order to not introduce hidden sources of non-determinism.
        '''
            # M: move agents
            # H: world.resolve_harvest()
            # R: world.resolve_reproduction()
            # G: world.resolve_agent_aging()
            # Π: commit births/deaths

        occupied_positions : dict[tuple[np.int64, np.int64], list[Agent]] = {}


        for agent_id, agent in sorted_agents:
            # A
            # age check, if agent is older than max_age, agent.alive = False set on last agent tick 
            if not agent.alive:
                pending_agent_iteration_death["old_age"].count += 1
                pending_agent_iteration_death["old_age"].agents.append(agent_id)
                continue
            # M
            if not agent.move_agent():
                pending_agent_iteration_death["metabolic_starvation"].count += 1
                pending_agent_iteration_death["metabolic_starvation"].agents.append(agent_id)
                continue
            
            # move agents to positional dict 
            # NOTE: 
                # as agents get added by a sorted itererative process, order is preserved. 
                # However, this has to accounted for in the future by a check, as it can lead to hidden non-determinism even if stable for now
            if agent.position in occupied_positions:
                occupied_positions[agent.position].append(agent)
            else:
                occupied_positions[agent.position] = [agent]

        occupied_cells = len(occupied_positions)
        moved_surviving_agents  = sum(len(v) for v in occupied_positions.values())
        mean_occupancy = (moved_surviving_agents  / len(occupied_positions)) if occupied_positions else 0
        max_occupancy = max(len(v) for v in occupied_positions.values()) if occupied_positions else 0
        ratio_t = max_occupancy / mean_occupancy if mean_occupancy > 0 else 0

        occupancy_metrics : dict[str, np.float64] = {
            "occupied_cells" : occupied_cells,
            "mean_occupancy" : mean_occupancy,
            "max_occupancy" : max_occupancy,
            "ratio_t" : ratio_t
        }
        
        
        reproducing_agents , pending_world_death = self.world.resolve_harvest_world(occupied_positions)
        pending_death : dict[str, DeathBucket] = pending_agent_iteration_death | pending_world_death
        
            
            # agent_step gets called in world.harvest_world

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

        if __debug__:
            self._assert_invariants()


        results = StepMetrics(len(reproducers_to_commit), deaths_this_tick, pending_death, occupancy_metrics)
        return results




    

    
    def get_state_hash(self) -> str:
        """ returns state hash. """
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    


    def get_snapshot(self) -> "EngineSnapshot":
        """ returns engine snapshot. """
        return engine_to_snapshot(self)


    


    @classmethod
    def from_snapshot(cls, snapshot : "EngineSnapshot") -> "Engine":
        """ create engine from snapshot. """
        return engine_from_snapshot(cls, snapshot)
        







if __name__ == "__main__":
    pass










