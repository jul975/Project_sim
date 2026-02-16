import numpy as np

"""
Problem 4 — Dual RNG Streams (Hierarchical Determinism)

Objective
---------
Separate randomness into independent subsystems.

Use TWO RNG streams:

    movement_rng
    reproduction_rng

Both derived from a single master seed using SeedSequence.spawn().


System State
------------

S(t) = {
    position_i(t),
    alive_i(t)
}

Each timestep:

1) Movement phase:
    position_i += movement_rng.choice([-1, 1])

2) Reproduction phase:
    if reproduction_rng.random() < p:
        spawn new agent


Core Constraints
----------------
1. Use numpy.random.SeedSequence(seed)
2. Spawn two child sequences:
       ss.spawn(2)
3. Create two independent RNG streams
4. Movement must not depend on reproduction RNG
5. Reproduction must not depend on movement RNG


Required Experiments
--------------------

Experiment 1 — Same Master Seed
    Entire world identical.

Experiment 2 — Change Only Reproduction Seed
    Movement trajectory remains identical.
    Reproduction behavior differs.

Experiment 3 — Collapse to Single RNG
    Movement becomes coupled to reproduction.
    Removing reproduction changes movement.


What This Teaches
-----------------
1. Controlled independence
2. Hierarchical deterministic randomness
3. Subsystem separation
4. Why seed splitting must be explicit
5. How professional simulation engines isolate randomness


Goal
----
Understand how to control independence without losing determinism.

The system evolves in expanded state:

    (S(t), r_movement(t), r_reproduction(t))

You now control multiple deterministic random timelines.
"""


MAX_AGENT_COUNT = 200






class Engine:
    def __init__(self, seed, agent_count, change_condition=False):
        self.master_ss = np.random.SeedSequence(seed)
        self.change_condition = change_condition


        self.tick = 0
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

        for agent in list(self.state):
            # agent step returns true if agent reproduces.
            if agent.step() and self.agent_count < MAX_AGENT_COUNT:
                self.create_new_agent(agent.agent_seed)
        self.tick += 1


    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.state

    





class Agent:
    ''' agents should be a subclass in order to acces span new agent functionality cleanly. '''
    def __init__(self, engine , id, agent_seed):
        self.engine = engine
        self.id = id
        self.agent_seed = agent_seed

        self.move_ss, self.repro_ss = self.agent_seed.spawn(2)


        # create rngs for movement and reproduction.
        self.move_rng = np.random.default_rng(self.move_ss)
        self.repro_rng = np.random.default_rng(self.repro_ss)


        # initialize position
        self.position = self.move_rng.integers(1, 30)
        self.alive = True



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






