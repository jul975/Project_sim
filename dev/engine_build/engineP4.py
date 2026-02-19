import numpy as np
import hashlib

from state_schema import get_state_bytes
from rng_utils import reconstruct_rng

from agent import Agent





MAX_AGENT_COUNT = 200






class Engine:
    def __init__(self, seed, agent_count : np.int64 = None, change_condition=False) -> None:
        
                
        self.master_ss = np.random.SeedSequence(seed)
        self.change_condition = change_condition


        self.tick : np.int64 = 0
        


        self.agents = self.initialize_state(agent_count)  



    def initialize_state(self, agent_count) -> list[Agent]:
        agent_seeds = self.master_ss.spawn(agent_count)
        return [Agent(self, i, agent_seeds[i]) for i in range(agent_count)]
    










    
    def create_new_agent(self, parent_agent : Agent) -> None:

        ## ==>  need fix here, indexing prob not future proof as deaths will potentially 
        #       change the order of agents.


        # seed sequence for new agent is not necessary, rng can be used to simulate determinism 
        # current idea => | Parent RNG → draw value → use value to seed new independent RNG
        child_seed_int = parent_agent.repro_rng.bit_generator.random_raw()
        
        #note on 63: 2**63 is the maximum value for a signed 64 bit integer.
        
        



        
        self.agents.append(Agent( self , len(self.agents) , child_seed_int))














    def get_agent_count(self) -> np.int64:
        return len(self.agents)

    def __eq__(self, other) -> bool:
        return self.get_state_hash() == other.get_state_hash()

    def step(self) -> None:
        for agent in sorted(self.agents, key=lambda a: a.id):
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
            "master_ss" : self.master_ss,
            "change_condition" : self.change_condition,
            "agent_count" : len(self.agents),
            "agents" : [self.get_agent_snapshot(agent) for agent in self.agents]
        }
        return engine_snapshot
        
        


        

    def get_agent_snapshot(self, agent) -> dict:
        return {
            "id" : agent.id, 
            "position" : agent.position,
            "energy_level" : agent.energy_level,
            "alive" : agent.alive,
            "agent_seed" : agent.agent_seed,
            "move_rng" : agent.move_rng.bit_generator.state,
            "repro_rng" : agent.repro_rng.bit_generator.state,
            "energy_rng" : agent.energy_rng.bit_generator.state
        }
    
    @classmethod
    def from_snapshot(cls, snapshot) -> "Engine":
        """ create engine from snapshot. """
        engine = cls(snapshot["master_ss"].entropy, snapshot["agent_count"])
        engine.tick = snapshot["tick"]
        engine.change_condition = snapshot["change_condition"]
        
        engine.agents = [Agent.from_snapshot(agent_snapshot, engine) for agent_snapshot in snapshot["agents"]]
        return engine





    def run(self, n_steps) -> list[Agent]:
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




    # test 2
    print("\n")
    print("Testing Change Only Reproduction Seed...")
    print("================================================================")
    print("case 2 engine 1 and engine 3 should be different because of change in reproduction seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"final agent count eng3: {eng3.get_agent_count()}")


    # test 3
    print("\n")

    print("================================================================")
    print("case 3 engine 1 and engine 2 should have the same hash")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"eng2 hash: {eng2.get_state_hash()}")    
    print(f"eng3 hash: {eng3.get_state_hash()}")


    # test 4
    print("\n")
    print("================================================================")
    print("case 4 engine 1 and engine 4 should have the same hash, engine 4 is a clone of engine 1 at t = 50 => snapshot and rebuild")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"clone hash: {clone.get_state_hash()}")






