import numpy as np
import hashlib


"""
State Schema v1:
    basic first layout of state. 
    should be used to set up get_state_bytes() for "canonical serialization"
    this should feed the buffer feeding the get_hash() function.

State Schema v1
---------------
tick: int64
agent_count: uint64
agent:
    id: int64
    position: int64
    energy: int64
    alive: uint8
    
"""


MAX_AGENT_COUNT = 200


# helpers 
def set_int64(x, signed=False):
    # position can be negative so use signed=True
    return int(x).to_bytes(8, 'big', signed=signed)

def set_uint8(x):
    return int(x).to_bytes(1, 'big', signed=False)






class Engine:
    def __init__(self, seed, agent_count : np.int64, change_condition=False):
        self.master_ss = np.random.SeedSequence(seed)
        self.change_condition = change_condition


        self.tick : np.int64 = 0
        self.agent_count = agent_count


        self.state = self.initialize_state(self.agent_count)



    def initialize_state(self, agent_count):
        ''' 
        The engine should be deterministic, so the initial state should be determined by the seed.
        The seed should be used (or rng, need to clear up the difference between the two) to create the initial state.
        '''
        agent_seeds = self.master_ss.spawn(agent_count)
        return [Agent(self, i, agent_seeds[i]) for i in range(agent_count)]
    
    def create_new_agent(self, parent_agent_seed):
        # get agent_seed from parent_rng => idea is that the determinism of the engine is preserved.
        # also the new agent rng is deterministicly linked to it's parent but still different from parent and other children.
        # kinda like high level simulation of genetic inheritance.

        self.agent_count += 1
        self.state.append(Agent( self , self.agent_count , parent_agent_seed.spawn(1)[0]))



    def step(self):
        """ future proving deterministic agent order. not relevant for current problem but will help in future."""
        for agent in sorted(self.state, key=lambda a: a.id):
            # agent step returns true if agent reproduces.
            if agent.step() and self.agent_count < MAX_AGENT_COUNT:
                self.create_new_agent(agent.agent_seed)
        self.tick += 1


    def get_state_bytes(self):
        """ canonical serialization of state. """
        """ Right now:  
                - S(t) = 
                        {
                        world state: tick, agent_count
                        + 
                        n_agents * (agent state: id, position, energy, alive)
                        }
        """



        # tick, agent_count, agent: id, position, energy, alive
        buffer = bytearray()

        buffer += set_int64(self.tick)

        buffer += set_int64(self.agent_count)

        for agent in sorted(self.state, key=lambda a: a.id):
            buffer += set_int64(agent.id)
            # position can be negative so use signed=True
            buffer += set_int64(agent.position, signed=True)
            buffer += set_int64(agent.energy_level)
            buffer += set_uint8(agent.alive)


        return bytes(buffer)
    
    def get_state_hash(self):
        return hashlib.sha256(self.get_state_bytes()).hexdigest()


    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.state

    





class Agent:
    ''' agents should be a subclass in order to acces span new agent functionality cleanly. '''
    def __init__(self, engine : Engine , id : np.int64, agent_seed : np.random.SeedSequence) -> None:
        
        """ engine: Engine
        
                        id: np.int64
                agent_seed: np.random.SeedSequence
        """
        self.engine= engine
        self.id = id
        self.agent_seed = agent_seed

        self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)


        # create rngs for movement and reproduction.


        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)
        self.energy_rng = np.random.default_rng(self.energy_ss)


        # initialize position
        self.position : np.int64 = self.move_rng.integers(1, 30)
        self.alive : np.uint8 = True

        # setup energy level as static variable for now. 
        # current idea is that on initialization each agent has a certain energy range
        # gives it a inborn "fitness" will be used later
        self.energy_level = self.energy_rng.integers(20, 40)



        # idea is that this would create a 10% chance of reproducing per tick.
        self.p = 0.01 if not engine.change_condition else 0.02


    
         

    def step(self):        
        self.position += self.move_rng.choice([-1, 1])

        reproduce = self.repro_rng.random()
        if reproduce < self.p:
            ## create new agent => how to update sequence? => i would use parent_agents rng as a base so it is deterministic but different from parent and other children.
            return True
        return False

            







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
    print("Final positions eng1:")
    for agent in eng1.state:
        print(f"Agent {agent.id} position: {agent.position}")
    print("\n")
    print(f"final agent count eng1: {eng1.agent_count}")
    print("\n")
    print("Final positions eng2:")
    for agent in eng2.state:
        print(f"Agent {agent.id} position: {agent.position}")   
    print("\n")
    print(f"final agent count eng2: {eng2.agent_count}")




    # test 2
    print("\n")
    print("Testing Change Only Reproduction Seed...")
    print("================================================================")
    print("case 2 engine 1 and engine 3 should be different because of change in reproduction seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print("Final positions eng3:")
    for agent in eng3.state:
        print(f"Agent {agent.id} position: {agent.position}")   
    print("\n")
    print(f"final agent count eng3: {eng3.agent_count}")


    # test 3
    print("\n")
    print("Testing get_state_hash() functionality...")
    print("================================================================")
    print("case 3 engine 1 and engine 2 should have the same hash")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng1 hash: {eng1.get_state_hash()}")
    print(f"eng2 hash: {eng2.get_state_hash()}")    
    print(f"eng3 hash: {eng3.get_state_hash()}")






