import numpy as np

"""
moving 



"""

class Agent:
    def __init__(self, id, starting_position, engine_rng):
        self.id = id
        self.position = starting_position
        self.rng = np.random.default_rng(engine_rng)  

    def step(self):
        ## (partly fixed need clearing up ) bug is here, choosing direction and moving are two separate rng calls, so the order of the calls matters.
        ## fix is to make one call to rng.integers(1, 3) * rng.choice([-1, 1])
        # Question, should the agent have its own rng? or do the rng calls need to be made on an engine level? if so how to ensure each agent gets a unique seed?

        # -> should the engine make the rng call and then pass the value to the agent?
        # -> what is the point of having an rng on the agent if the engine is going to make the call?
        # -> should all rng calls be made on the engine level?


        self.direction = self.rng.choice([-1, 1])
        self.position += (self.rng.integers(1, 3) * self.direction)


class Engine:
    def __init__(self, seed, agent_count ,starting_positions):
        
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = starting_positions
        self.agents = [Agent(i, starting_positions, self.rng) for i in range(agent_count)]

    def step(self):
        # next_state = self.compute_next_state(self.state)
        self.random_integer = self.rng.integers(1, 101)

        for agent in self.agents:
            agent.step()

        self.state += self.random_integer
        self.tick += 1

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.random_integer, self.state
    



if __name__ == "__main__":
    seed = 42
    agent_count = 5
    starting_positions = 0

    eng1 = Engine(seed, agent_count, starting_positions)
    eng1.run(10)

    eng2 = Engine(seed, agent_count, starting_positions)
    eng2.run(10)


    print("Final positions eng1:")
    for agent in eng1.agents:
        print(f"Agent {agent.id} position: {agent.position}")
    print("\n")
    print("Final positions eng2:")
    for agent in eng2.agents:
        print(f"Agent {agent.id} position: {agent.position}")