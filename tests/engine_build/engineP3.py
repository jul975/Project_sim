"""
Problem 3 — Branch-Dependent RNG Consumption (Subtle Divergence)

Objective
---------
Simulate N agents with an energy level.

Global system state:

    S(t) = { energy_i(t) } for i in {1,...,N}

Each timestep:

    If agent.energy > 0:
        agent.energy += δ_i(t)

    where:
        δ_i(t) ∈ {-1, +1}
        chosen randomly from a single master RNG.

Agents "die" when energy <= 0.
Dead agents no longer consume RNG calls.


Core Constraints
----------------
1. Use ONE master RNG at the engine level.
2. No per-agent RNG instances.
3. Deterministic iteration order.
4. Exactly one RNG call per alive agent per tick.
5. run(seed, steps) must be reproducible.


Required Experiments
--------------------

Experiment 1 — Determinism

    Engine(seed=42).run(100)
    Engine(seed=42).run(100)

Expected:
    Identical extinction times and final energy vector.


Experiment 2 — Branch Condition Modification

Change this:

    if agent.energy > 0:

to:

    if agent.energy >= 0:

Run again with the same seed.

Expected:
    Entire trajectory shifts.
    Extinction times change.
    Final world diverges.


Why This Happens
----------------
The branch condition changes how many RNG calls occur.

Original:
    Dead agents stop consuming RNG.

Modified:
    Agents at energy == 0 still consume RNG once more.

This shifts the RNG state timeline:

    r(t) ≠ r'(t)

Which changes all future randomness.

This divergence grows over time.


What This Problem Teaches
-------------------------

1. RNG call count is part of world state.
2. Branch conditions implicitly change RNG evolution.
3. Two logically similar programs can produce completely different worlds.
4. Deterministic systems can still be extremely sensitive to small structural changes.


Questions You Must Be Able To Answer
------------------------------------

1. What is S(t)?
2. What is r(t)?
3. How many RNG calls happen per tick?
4. When does that number change?
5. Why does a small condition change cause massive divergence?


Goal
----
Understand that conditional logic affects RNG consumption,
and therefore affects the entire future of the simulation.

The system evolves in joint space:

    (S(t), r(t))

If you change how often r(t) advances,
you change the entire future trajectory.
"""



import numpy as np

"""
Problem 3 — Branch-Dependent RNG Consumption (Subtle Divergence)

Objective
---------
Simulate N agents with an energy level.

Global system state:

    S(t) = { energy_i(t) } for i in {1,...,N}

Each timestep:

    If agent.energy > 0:
        agent.energy += δ_i(t)

    where:
        δ_i(t) ∈ {-1, +1}
        chosen randomly from a single master RNG.

Agents "die" when energy <= 0.
Dead agents no longer consume RNG calls.


Core Constraints
----------------
1. Use ONE master RNG at the engine level.
2. No per-agent RNG instances.
3. Deterministic iteration order.
4. Exactly one RNG call per alive agent per tick.
5. run(seed, steps) must be reproducible.


"""

class Agent:
    def __init__(self, id, starting_energy):
        self.id = id
        self.energy_level = starting_energy
         

    # set condition for agent to be alive on agent level or engine level?


    def step(self, energy_change):        
        self.energy_level += energy_change


class Engine:
    def __init__(self, seed, agent_count, change_condition=False):
        
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = self.initialize_state(agent_count)

        self.extinction_record = {}

        
        self.change_condition = change_condition
        

    def initialize_state(self, agent_count):
        ''' 
        The engine should be deterministic, so the initial state should be determined by the seed.
        The seed should be used (or rng, need to clear up the difference between the two) to create the initial state.


        energy level should be an integer between 1 and 20. simulates diff starting conditions and hit dead state in in small sample size.
        '''
        return [Agent(i, self.rng.integers(1, 20)) for i in range(agent_count)]





    def step(self):
        # rng used on engine level 
        for agent in self.state:
            if self.change_condition:
                if agent.energy_level < 0:
                    continue
            else:
                if agent.energy_level <= 0:
                    if agent.id not in self.extinction_record:
                        self.extinction_record[agent.id] = self.tick
                    
                    continue

            energy_change = self.rng.choice([-1, 1])
            agent.step(energy_change)
        self.tick += 1

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.state
    



if __name__ == "__main__":
    seed = 42
    agent_count = 5




    eng1 = Engine(seed, agent_count)
    eng1.run(100)

    eng2 = Engine(seed, agent_count)
    eng2.run(100)   


    eng3 = Engine(seed, agent_count, change_condition=True)
    eng3.run(100)

    # Test 1: Same Seed → Identical World
    print("Testing Same Seed => Identical World...")
    print("================================================================")
    print("case 1 engine 1 and engine 2 should be the same with same seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print("Final energy levels eng1:")
    for agent in eng1.state:
        print(f"Agent {agent.id} energy level: {agent.energy_level}")
        
    print("\n")
    print("Final energy levels eng2:")
    for agent in eng2.state:
        print(f"Agent {agent.id} energy level: {agent.energy_level}")   
    print("\n")


    print("Extinction record eng1:")
    for agent in eng1.extinction_record.items():
        print(f"Agent {agent[0]} died at tick {agent[1]}")
    print("\n")

    print("Extinction record eng2:")
    for agent in eng2.extinction_record.items():
        print(f"Agent {agent[0]} died at tick {agent[1]}")
        
    print("\n")



    # Test 2: Branch Condition Modification
    print("Testing Branch Condition Modification...")
    print("================================================================")
    print("case 2 engine 3 should be different from engine 1 and 2 because of branch condition modification")
    print("-----------------------------------------------------------------")
    print("\n")
    print("Final energy levels eng3:")
    for agent in eng3.state:
        print(f"Agent {agent.id} energy level: {agent.energy_level}")   
    print("\n")