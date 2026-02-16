import numpy as np

# first sketch of design to make concepts clear
"""
Engine testing plan:

- Test that the engine runs without error
- Test that the engine produces the correct output shape and type
- Test that the engine produces deterministic output
- Test that the engine produces different output with different seeds
- Test that the engine produces the correct output for a given seed and config

Practice problems to solve here: 

    Level 1: The Deterministic Ghost

        a) Focus: RNG Isolation and Reproducibility.
        b) The Goal: Prove that your engine owns the randomness, not the global Python environment.

        Input Description: * An integer seed.
                           * An integer n_steps.

        The Task:   Create an Engine class. Upon initialization, it creates a numpy.random.default_rng(seed). 
                    In each step, the engine should generate one random integer between 1 and 100 and add it to a total_sum variable.

        Output Description:

            * The total_sum after n_steps.

        Constraint: 
        
            1. The engine must be deterministic. That is, given the same seed and number of steps, it must always produce the same output.

            * If you run Engine(seed=42).run(10) and Engine(seed=42).run(10) in two different scripts, 
            the output must be identical. If you change the seed to 43, the output must differ.


"""


class Engine:
    def __init__(self, seed, config):
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = self.initialize_state(config)

    def step(self):
        next_state = self.compute_next_state(self.state)
        self.state = next_state
        self.tick += 1

    def run(self, steps):
        for _ in range(steps):
            self.step()