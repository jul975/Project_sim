import numpy as np
import hashlib



from state_schema import get_state_bytes

from agent import Agent





MAX_AGENT_COUNT = 200






class Engine:
    def __init__(self, seed, agent_count : np.int64, change_condition=False):
        
                
        self.master_ss = np.random.SeedSequence(seed)
        self.change_condition = change_condition


        self.tick : np.int64 = 0
        


        self.agents = self.initialize_state(agent_count)  



    def initialize_state(self, agent_count):
        agent_seeds = self.master_ss.spawn(agent_count)
        return [Agent(self, i, agent_seeds[i]) for i in range(agent_count)]
    
    def create_new_agent(self, parent_agent_seed):

        ## ==>  need fix here, indexing prob not future proof as deaths will potentially 
        #       change the order of agents.

        
        self.agents.append(Agent( self , len(self.agents) , parent_agent_seed.spawn(1)[0]))

    def get_agent_count(self):
        return len(self.agents)

    def __eq__(self, other):
        return self.get_state_hash() == other.get_state_hash()

    def step(self):
        for agent in sorted(self.agents, key=lambda a: a.id):
            if agent.step() and len(self.agents) < MAX_AGENT_COUNT:
                self.create_new_agent(agent.agent_seed)
        self.tick += 1


# get_state_bytes() and get_state_hash() are not used in the current version. 

    

    
    def get_state_hash(self):
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    






    def get_snapshot(self):
        engine_snapshot = {
            "tick" : self.tick,
            "master_ss" : self.master_ss,
            "agent_count" : len(self.agents),
            "agents" : [self.get_agent_snapshot(agent) for agent in self.agents]
        }
        return engine_snapshot
        
        


        

    def get_agent_snapshot(self, agent):
        return {
            "id" : agent.id, 
            "position" : agent.position,
            "energy_level" : agent.energy_level,
            "alive" : agent.alive,
            "agent_seed" : agent.agent_seed,
            "move_rng" : agent.move_rng,
            "repro_rng" : agent.repro_rng,
            "energy_rng" : agent.energy_rng
        }
    
    @classmethod
    def from_snapshot(cls, snapshot):
        """ create engine from snapshot. """
        engine = cls(snapshot["master_ss"].entropy, snapshot["agent_count"])
        engine.tick = snapshot["tick"]





    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.agents

    










if __name__ == "__main__":





    eng1 = Engine(42, 10)
    eng1.run(100)


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






