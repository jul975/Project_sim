import numpy as np
import hashlib

from .state_schema import get_state_bytes
from .rng_utils import reconstruct_rng
from .seed_seq_utils import get_seed_seq_dict, reconstruct_seed_seq

from .agent import Agent
from .world import World
from .metrics import SimulationMetrics

from .config import SimulationConfig

from dataclasses import asdict














class Engine:
    def __init__(self, seed : np.int64 , config : SimulationConfig ,change_condition=False) -> None:

        self.config = config
                
        self.master_ss = np.random.SeedSequence(seed)
        self.next_agent_id = self.config.initial_agent_count
        

        self.world = World(change_condition)
        
        self.agents : dict[np.int64, Agent] = self.initialize_state(self.config.initial_agent_count)  
        
        
        
        



    def initialize_state(self, agent_count) -> dict[np.int64, Agent]:
        agent_seeds = self.master_ss.spawn(agent_count)

        return {i : Agent(self, i, agent_seeds[i]) for i in range(agent_count)}
    










    
    def create_new_agent(self, child_seed : np.random.SeedSequence) -> None:

                
        # parent_agent.agent_seed.spawn(1)[0]

        # child_seed = parent_agent.reproduce()


        
        self.agents[self.next_agent_id] = Agent( self , self.next_agent_id , child_seed)
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




    def step(self, run_metrics : bool = False) -> None | tuple[np.int64, np.int64]:
        """ restructuring step method in order to evaluate agents for death and birth together. 
            After evaluation, available capacity gets calculated to avoid undershoot of agent capacity."""
        
        # if metrics are run, len(births_to_commit) and len(pending_death) are returned.
        # should simplify light weight metrics collection. without interference
        

        pending_death: list[np.int64] = []
        pending_birth: list[np.int64] = []



        sorted_agents = sorted(self.agents.items())


        ''' NOTE: 
            -   Agent state updated is followed by a state evaluation on engine level

            -   The evaluation does NOT influence determenism as it holds only references to the agents marked 
                for their respective state AFTER step is implemented, further processing happens after 
                all states have been updated 


            - CAVE: ORDERING OF DEATH AND BIRTH IS IMPORTANT! 
                    => RIGHT NOW, DEATH OCCURS BEFORE BIRTH. !!!!!!!
        
        '''
        # state update and classification 
        for agent_id, agent in sorted_agents:

            if not agent.alive:
                pending_death.append(agent_id)
            

            elif agent.step():
                # creation of child rng, 
                pending_birth.append(self.get_child_seed(agent))
                # self.create_new_agent( agent)

            
        # capacity calculations
        effective_population = len(self.agents) - len(pending_death)
        available_capacity = self.config.max_agent_count - effective_population
        births_to_commit = pending_birth[:available_capacity]
       
       
       
        # commit to population changes
        # NOTE: Keep an eye on this step!! 
        for agent_id in pending_death:
            del self.agents[agent_id]
        for child_seed in births_to_commit:
            self.create_new_agent(child_seed)

        self.world.tick += 1


        # metrics return 
        if run_metrics:
            return len(births_to_commit), len(pending_death)




    

    
    def get_state_hash(self) -> str:
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    






    def get_snapshot(self) -> dict:
        engine_snapshot = {
            
            "master_ss" : get_seed_seq_dict(self.master_ss),
            "next_agent_id" : self.next_agent_id,
            "config": asdict(self.config),


            "world" : {
                "tick" : self.world.tick,
                "change_condition" : self.world.change_condition
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

            "agent_seed" : get_seed_seq_dict(agent.agent_seed),
            
            # redundant clones 
            #"move_ss" : get_seed_seq_dict(agent.move_ss),
            #"repro_ss" : get_seed_seq_dict(agent.repro_ss),
            #"energy_ss" : get_seed_seq_dict(agent.energy_ss),

            "move_rng" : agent.move_rng.bit_generator.state,
            "repro_rng" : agent.repro_rng.bit_generator.state,
            "energy_rng" : agent.energy_rng.bit_generator.state
        }
    
    @classmethod
    def from_snapshot(cls, snapshot : dict) -> "Engine":

        """ create engine from snapshot. """
        engine_clone = object.__new__(cls)

        engine_clone.config = SimulationConfig(**snapshot["config"])


        # engine master_ss doesnt need to be reconstructed.
        engine_clone.master_ss = reconstruct_seed_seq(snapshot["master_ss"], 0)

        # reconstruct world
        engine_clone.world = World.from_snapshot(snapshot["world"])
        

        engine_clone.next_agent_id = snapshot["next_agent_id"]

        engine_clone.agents = {agent_id : Agent.from_snapshot(agent_snapshot, engine_clone) for agent_id, agent_snapshot in snapshot["agents"].items()}
        




        
        return engine_clone





    def run(self, n_steps) -> dict[np.int64, Agent]:
        for _ in range(n_steps):
            self.step()

        return self.agents

    # NOTE: CAVE: 
            # method need to be removed in future !!!!
    def run_with_metrics(self, n_steps) -> dict[np.int64, Agent]:
        """ runs engine for n_steps and returns metrics. """
        """ NOTE: (copy from metrics.py)
                -   as of now I'm using 4 lists to store the metrics, need to make sure that no ticks are missed. 
                    => should be ok as is, as the recording is done after the tick is completed.
                    => but keep in mind  

            
        """

        metrics = SimulationMetrics()

        for _ in range(n_steps):
            

            births_this_tick, deaths_this_tick = self.step(run_metrics=True)

            metrics.record(self, births_this_tick, deaths_this_tick)
        
        return metrics
    










if __name__ == "__main__":
    # testing => python -m engine_build.test.test_engine
    pass










