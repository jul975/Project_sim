import numpy as np
import hashlib

from state_schema import get_state_bytes
from rng_utils import reconstruct_rng
from seed_seq_utils import get_seed_seq_dict, reconstruct_seed_seq

from agent import Agent





MAX_AGENT_COUNT = 200






class Engine:
    def __init__(self, seed : np.int64, agent_count : np.int64 = None, change_condition=False) -> None:
        
                
        self.master_ss = np.random.SeedSequence(seed)
        self.change_condition = change_condition


        self.tick : np.int64 = 0

        self.next_agent_id = agent_count
        

        # agents are stored in a dict with id as key for fast access.
        self.agents : dict[np.int64, Agent] = self.initialize_state(agent_count)  



    def initialize_state(self, agent_count) -> dict[np.int64, Agent]:
        agent_seeds = self.master_ss.spawn(agent_count)

        return {i : Agent(self, i, agent_seeds[i]) for i in range(agent_count)}
    










    
    def create_new_agent(self, parent_agent : Agent) -> None:

                
        # parent_agent.agent_seed.spawn(1)[0]

        child_seed = parent_agent.reproduce()


        
        self.agents[self.next_agent_id] = Agent( self , self.next_agent_id , child_seed)
        self.next_agent_id += 1














    def get_agent_count(self) -> np.int64:
        return len(self.agents)

    def __eq__(self, other) -> bool:
        # guard suggested by chatgpt, sounded reasonnable.
        if not isinstance(other, Engine):
            return NotImplemented
        
        return self.get_state_hash() == other.get_state_hash()

    def step(self) -> None:
        for agent_id, agent in sorted(self.agents.items()):
            if agent.step() and len(self.agents) < MAX_AGENT_COUNT:
                

                # creation of child rng, 
                self.create_new_agent( agent)
        self.tick += 1


# get_state_bytes() and get_state_hash() are not used in the current version. 

    

    
    def get_state_hash(self) -> str:
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    






    def get_snapshot(self) -> dict:
        engine_snapshot = {
            "tick" : self.tick,
            "master_ss" : get_seed_seq_dict(self.master_ss),
            "change_condition" : self.change_condition,
            "next_agent_id" : self.next_agent_id,
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
    def from_snapshot(cls, snapshot) -> "Engine":

        """ create engine from snapshot. """
        engine_clone = object.__new__(cls)


        # engine master_ss doesnt need to be reconstructed.
        engine_clone.master_ss = reconstruct_seed_seq(snapshot["master_ss"], 0)
        engine_clone.change_condition = snapshot["change_condition"]
        engine_clone.tick = snapshot["tick"]

        engine_clone.next_agent_id = snapshot["next_agent_id"]

        engine_clone.agents = {agent_id : Agent.from_snapshot(agent_snapshot, engine_clone) for agent_id, agent_snapshot in snapshot["agents"].items()}
        




        
        return engine_clone





    def run(self, n_steps) -> dict[np.int64, Agent]:
        for _ in range(n_steps):
            self.step()

        return self.agents

    










if __name__ == "__main__":





    eng1 = Engine(42, 10)
    eng1.run(50)

    clone = Engine.from_snapshot(eng1.get_snapshot())
    clone.run(50)
    eng1.run(50)


    eng2 = Engine(42, 10)
    eng2.run(100)

    eng3 = Engine(42, 10, change_condition=True)
    eng3.run(100)

    
    

    


    # test 1 
    print("Testing Same Seed => Identical World...")
    print("================================================================")
    print("case 1 engine 1 and engine 2 should be the same with same seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print("\n")
    print(f"final agent count eng1: {eng1.get_agent_count()}")
    print("\n")
    print(f"final agent count eng2: {eng2.get_agent_count()}")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"eng2 hash: {eng2.get_state_hash()}")
    print("\n")


    # test 2
    print("\n")
    print("testing different seed => different world...")
    print("================================================================")
    print("case 2 engine 1 and engine 3 should be different because of different seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"final agent count eng1: {eng1.get_agent_count()}")
    print("\n")
    print(f"final agent count eng3: {eng3.get_agent_count()}")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"eng3 hash: {eng3.get_state_hash()}")
    print("\n") 


    # test 3
    print("\n")
    print("testing snapshot and rebuild...")
    print("================================================================")
    print("case 3 engine 1 and clone should be the same because clone is a rebuild from eng1 snapshot")
    print("-----------------------------------------------------------------")
    status_clone_vs_source = "PASSED" if eng1 == clone else "FAILED"
    status_eng1_vs_eng2 = "PASSED" if eng1 == eng2 and eng1 == clone else "FAILED"

    print("\n")
    print("-----------------------------------------------------------------")
    print(f"test status clone vs source : {status_clone_vs_source}")
    print(f"test status eng1 vs ref_eng vs clone : {status_eng1_vs_eng2}")
    print("\n")
    print(f"final agent count eng1: {eng1.get_agent_count()}")
    print(f"final agent count clone: {clone.get_agent_count()}")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"clone hash: {clone.get_state_hash()}")
    print("\n")






