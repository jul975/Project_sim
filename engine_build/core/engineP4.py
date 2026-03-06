import numpy as np
import hashlib

from .state_schema import get_state_bytes
from .seed_seq_utils import get_seed_seq_dict, reconstruct_seed_seq

from .agent import Agent
from .world import World

from .config import SimulationConfig, EnergyParams, DeathBucket, PopulationConfig

from dataclasses import asdict


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
    def __init__(self, seed_seq : np.random.SeedSequence , config : SimulationConfig ,change_condition=False) -> None:

        self.config = config
                
        self.master_ss = seed_seq
        
        self.next_agent_id = self.config.population_config.initial_agent_count
        self.max_age = self.config.population_config.max_age

        # create world
        world_seed: np.random.SeedSequence = self.master_ss.spawn(1)[0]
        # create new seed, for world setup

        self.world = World( world_seed, self.config ,change_condition)
        self.energy_params = self._derive_energy_params()
        
        self.agents : dict[np.int64, Agent] = self.initialize_state(self.config.population_config.initial_agent_count) 


        
        
    def _assert_invariants(self) -> None:
        assert len(self.agents) <= self.config.population_config.max_agent_count, "Agent count exceeds max_agent_count"
        for agent_id, agent in self.agents.items():
            assert agent_id == agent.id, "Agent id does not match dict key"
            assert 0 <= agent.position < self.config.world_size, "Agent position out of bounds"
        
        

    def initialize_state(self, agent_count) -> dict[np.int64, Agent]:
        agent_seeds = self.master_ss.spawn(agent_count)

        return {i : Agent(self, i, agent_seeds[i]) for i in range(agent_count)}
    

    ## NOTE:
    ## config -> engine -> subsystem delegation

    @property
    def world_size(self) -> np.int64:
        return self.config.world_size
    
    @property
    def max_resource_level(self) -> np.int64:
        return self.config.max_resource_level
    
    @property
    def resource_regen_rate(self) -> np.int64:
        return self.config.resource_regen_rate

    
    ## derive energy config to be passed on to agents
    def _derive_energy_params(self) -> EnergyParams:
        """ derives energy parameters from config rations, and max_harvest. """
        max_h = self.config.energy_config.max_harvest
        r = self.config.energy_config.ratios

        movement_cost = int(r.alpha * max_h)
        reproduction_threshold = int(r.gamma * movement_cost)
        reproduction_cost = int(r.beta * reproduction_threshold)

        return EnergyParams(movement_cost, reproduction_threshold, reproduction_cost)









    
    def create_new_agent(self, parent_agent : Agent) -> None:

                
        # parent_agent.agent_seed.spawn(1)[0]

        # child_seed = parent_agent.reproduce()
        

        child_seed = self.get_child_seed(parent_agent)
        
        self.agents[self.next_agent_id] = Agent( self , self.next_agent_id , child_seed)
        self.agents[self.next_agent_id].position = parent_agent.position
        self.next_agent_id += 1


    def get_child_seed(self, parent_agent : Agent) -> np.random.SeedSequence:
        return parent_agent.reproduce()














    def get_agent_count(self) -> np.int64:
        return len(self.agents)

    def __eq__(self, other) -> bool:
        # guard suggested by chatgpt, sounded reasonnable.
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

        occupied_positions : dict[np.int64, list[Agent]] = {}


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

        occupancy_metrics = {
            "occupied_cells" : occupied_cells,
            "mean_occupancy" : mean_occupancy,
            "max_occupancy" : max_occupancy,
            "ratio_t" : ratio_t
        }
        
        
        reproducing_agents, pending_world_death = self.world.resolve_harvest_world(occupied_positions)
        pending_death = pending_agent_iteration_death | pending_world_death
        
            
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
        available_capacity = self.config.population_config.max_agent_count - effective_population
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


        # metrics return 
        
        return len(reproducers_to_commit), deaths_this_tick, pending_death, occupancy_metrics




    

    
    def get_state_hash(self) -> str:
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    






    def get_snapshot(self) -> dict:
        engine_snapshot = {
            
            "master_ss" : get_seed_seq_dict(self.master_ss),
            "next_agent_id" : self.next_agent_id,
            "config": asdict(self.config),
            "energy_params" : asdict(self.energy_params),
            "max_age" : self.max_age,




            "world" : {
                "tick" : self.world.tick,
                "change_condition" : self.world.change_condition,
                "world_size" : self.world.world_size,

                "rng_world": self.world.rng_world.bit_generator.state,

                "resources" : self.world.resources,
                "fertility" : self.world.fertility,
                "max_harvest" : self.world.max_harvest,
                "resource_regen_rate" : self.world.resource_regen_rate
            },
            "agents" : {agent_id : self.get_agent_snapshot(agent) for agent_id, agent in self.agents.items()}
        }
        return engine_snapshot
        
        


        

    def get_agent_snapshot(self, agent) -> dict:
        return {
            "id" : agent.id, 
            "agent_spawn_count" : agent.agent_spawn_count,
            "position" : agent.position,
            "energy_level" : agent.energy_level,
            "alive" : agent.alive,
            "age" : agent.age,

            "agent_seed" : get_seed_seq_dict(agent.agent_seed),

            
            

            "move_rng" : agent.move_rng.bit_generator.state,
            "repro_rng" : agent.repro_rng.bit_generator.state,
            "energy_rng" : agent.energy_rng.bit_generator.state
        }
    


    @classmethod
    def from_snapshot(cls, snapshot : dict) -> "Engine":

        """ create engine from snapshot. """
        engine_clone = object.__new__(cls)

        engine_clone.config = SimulationConfig.from_dict(snapshot["config"]) 
        # assert isinstance(engine_clone.config, SimulationConfig), type(engine_clone.config)
        assert isinstance(engine_clone.config.population_config, PopulationConfig), type(engine_clone.config.population_config)
        
        
        engine_clone.energy_params = engine_clone._derive_energy_params()
        engine_clone.max_age = snapshot["max_age"]
        


        # engine master_ss doesnt need to be reconstructed.
        engine_clone.master_ss = reconstruct_seed_seq(snapshot["master_ss"], 1)

        # reconstruct world
        engine_clone.world = World.from_snapshot(snapshot["world"])
        

        engine_clone.next_agent_id = snapshot["next_agent_id"]

        engine_clone.agents = {agent_id : Agent.from_snapshot(agent_snapshot, engine_clone) for agent_id, agent_snapshot in snapshot["agents"].items()}
        




        
        return engine_clone







if __name__ == "__main__":
    pass










