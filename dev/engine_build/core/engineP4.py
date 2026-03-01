import numpy as np
import hashlib

from .state_schema import get_state_bytes
from .seed_seq_utils import get_seed_seq_dict, reconstruct_seed_seq

from .agent import Agent
from .world import World

from .config import SimulationConfig, EnergyParams, DeathBucket

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
    def __init__(self, seed : np.int64 , config : SimulationConfig ,change_condition=False) -> None:

        self.config = config
                
        self.master_ss = np.random.SeedSequence(seed)
        
        self.next_agent_id = self.config.population_config.initial_agent_count
        self.max_age = self.config.population_config.max_age

        # create world
        world_seed: np.int64 = self.master_ss.spawn(1)[0]
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




    def step(self) -> tuple[np.int64, np.int64, dict[str, DeathBucket]]:
        """ restructuring step method in order to evaluate agents for death and birth together. 
            After evaluation, available capacity gets calculated to avoid undershoot of agent capacity."""
        

        pending_death: dict[str: [Agent]] = {
            "old_age" : DeathBucket(),
            "metabolic_starvation" : DeathBucket(),
            "post_harvest_starvation" : DeathBucket(),
            "post_reproduction_death" : DeathBucket()
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
        # single agent state update and interactions world

        # NOTE: 
        # implicit agent resource competition, 
        # Deterministic priority harvesting
        # Implicit age dominance
        for agent_id, agent in sorted_agents:
            # A
            # age check, if agent is older than max_age, agent.alive = False set on last agent tick 
            if not agent.alive:
                pending_death["old_age"].count += 1
                pending_death["old_age"].agents.append(agent_id)
                continue
            # M
            if not agent.move_agent():
                pending_death["metabolic_starvation"].count += 1
                pending_death["metabolic_starvation"].agents.append(agent_id)
                continue
                

            # H
            if not agent.harvest_resources():
                pending_death["post_harvest_starvation"].count += 1
                pending_death["post_harvest_starvation"].agents.append(agent_id)
                continue
            # spends energy and moves to new position.
            # potentially reproduces, store that

            # R
            if agent.can_reproduce():
                if agent.does_reproduce():
                    reproducing_agents.append(agent)
                    if agent.energy_level <= 0:
                        pending_death["post_reproduction_death"].count += 1
                        pending_death["post_reproduction_death"].agents.append(agent_id)
                        continue
            agent.step()

            
            
        
            
            


        

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
        
        return len(reproducers_to_commit), deaths_this_tick, pending_death




    

    
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
        engine_clone.energy_params = engine_clone._derive_energy_params()
        engine_clone.max_age = snapshot["max_age"]


        # engine master_ss doesnt need to be reconstructed.
        engine_clone.master_ss = reconstruct_seed_seq(snapshot["master_ss"], 1)

        # reconstruct world
        engine_clone.world = World.from_snapshot(snapshot["world"])
        

        engine_clone.next_agent_id = snapshot["next_agent_id"]

        engine_clone.agents = {agent_id : Agent.from_snapshot(agent_snapshot, engine_clone) for agent_id, agent_snapshot in snapshot["agents"].items()}
        




        
        return engine_clone





    def run(self, n_steps) -> dict[np.int64, Agent]:
        for _ in range(n_steps):
            self.step()

        return self.agents
    



"""    # NOTE: CAVE: 
            # method need to be removed in future !!!!
    def run_with_metrics(self, n_steps) -> dict[np.int64, Agent]:


        metrics = SimulationMetrics()

        for _ in range(n_steps):
            

            births_this_tick, deaths_this_tick, pending_death = self.step(run_metrics=True)

            metrics.record(self, births_this_tick, deaths_this_tick, pending_death)
        
        return metrics"""
    










if __name__ == "__main__":
    # testing => python -m engine_build.test.test_engine
    pass










