import numpy as np

"""
moving 



"""

class Agent:
    def __init__(self, id, starting_position, engine_rng):
        self.id = id
        self.position = starting_position
         


    def step(self, direction):        
        self.position += direction


class Engine:
    def __init__(self, seed, agent_count, reverse_order=False):
        
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = self.initialize_state(agent_count)
        if reverse_order:
            self.state = self.state[::-1]
        

    def initialize_state(self, agent_count):
        ''' 
        The engine should be deterministic, so the initial state should be determined by the seed.
        The seed should be used (or rng, need to clear up the difference between the two) to create the initial state.
        '''
        return [Agent(i, self.rng.integers(1, 30), self.rng) for i in range(agent_count)]





    def step(self):
        for agent in self.state:
            direction = self.rng.choice([-1, 1])
            agent.step(direction)
        self.tick += 1

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.state
    



if __name__ == "__main__":
    seed = 42
    agent_count = 5
    


    eng1 = Engine(seed, agent_count)
    eng1.run(10)

    eng2 = Engine(seed, agent_count)
    eng2.run(10)


    eng3 = Engine(seed, agent_count, reverse_order=True)
    eng3.run(10)




    # test 1: Same Seed → Identical World

    print("Testing Same Seed => Identical World...")
    print("================================================================")
    print("case 1 engine 1 and engine 2 should be the same with same seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print("Final positions eng1:")
    for agent in eng1.state:
        print(f"Agent {agent.id} position: {agent.position}")
    print("\n")
    print("Final positions eng2:")
    for agent in eng2.state:
        print(f"Agent {agent.id} position: {agent.position}")   
    



    # Shuffle Agent Iteration Order
    # Test 2: Order Matters
    print("\n")

    print("Shuffling Agent Iteration Order...")
    print("================================================================")
    print("case 2 engine 3 should be different from engine 1 and 2 because the agent iteration order is reversed")
    print("-----------------------------------------------------------------")
    print("\n")
    print("Final positions eng3:")
    for agent in eng3.state:
        print(f"Agent {agent.id} position: {agent.position}")   
    