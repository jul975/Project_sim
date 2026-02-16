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
    def __init__(self, seed, starting_energy):
        """ starting energy is used as placeholder for more complex state"""
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = starting_energy

    def step(self):
        # next_state = self.compute_next_state(self.state)
        self.random_integer = self.rng.integers(1, 101)
        self.state += self.random_integer
        self.tick += 1

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

        return self.random_integer, self.state



if __name__ == "__main__":
    seed_1 = 42
    seed_2 = 43

    n_steps = 10


    eng1 = Engine( seed_1, starting_energy=10)
    eng1.run(n_steps)

    eng2 = Engine(seed_1, starting_energy=10)
    eng2.run(n_steps)

    eng3 = Engine(seed_2, starting_energy=10)
    eng3.run(n_steps)

    eng4 = Engine(seed_1, starting_energy=10)
    eng4.run(n_steps + 1)

    eng5 = Engine(seed_1, starting_energy=10)
    eng5.run(n_steps)

    # Test 1: Deterministic Ghost (Problem 1)
    print("Testing Deterministic Ghost...")
    print("================================================================")
    print("case 1 engine 1 and engine 2 should be the same with same seed")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng1: {seed_1} n_steps: {n_steps}")
    print(f"eng1.state: {eng1.state}")
    print(f"eng2: {seed_1} n_steps: {n_steps}")
    print(f"eng2.state: {eng2.state}")
    print("\n")


    assert eng1.random_integer == eng2.random_integer, "FAILED: Runs with same seed must be identical!"
    print("SUCCESS: Determinism confirmed.\n")
    print(f"eng1.random_integer: {eng1.random_integer} eng2.random_integer: {eng2.random_integer}")
    print(f"eng1.state: {eng1.state} eng2.state: {eng2.state}")
    print("\n")
    print("\n")


    # Test 2: Different seeds should give different results
    print("Testing Different Seeds...")
    print("-----------------------------------------------------------------")
    print("case 2 engine 1 and engine 3 should be different with different seeds")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng1: {seed_1} n_steps: {n_steps}")
    print(f"eng3: {seed_2} n_steps: {n_steps}")
    print("\n")
    assert eng1.random_integer != eng3.random_integer, "FAILED: Runs with different seeds must be different!"
    print("SUCCESS: Different seeds produce different results.\n")
    print(f"eng1.random_integer: {eng1.random_integer} eng3.random_integer: {eng3.random_integer}") 
    print(f"eng1.state: {eng1.state} eng3.state: {eng3.state}")
    print("\n")
    print("\n")


    # Test 3: Test rerunning eng1 and eng2 with different n_steps should give different results

    print("Testing Different n_steps...")
    print("-----------------------------------------------------------------")
    print("case 3 engine 4 and engine 5 should be different with different n_steps")
    print("-----------------------------------------------------------------")
    print("\n")
    print(f"eng4: {seed_1} n_steps: {n_steps + 1}")
    print(f"eng5: {seed_1} n_steps: {n_steps}")
    print("\n")

    print(f"eng4.random_integer: {eng4.random_integer} eng5.random_integer: {eng5.random_integer}")
    print(f"eng4.state: {eng4.state} eng5.state: {eng5.state}")
    assert eng4.random_integer != eng5.random_integer, "FAILED: Runs with different n_steps must be different!"
    print("SUCCESS: Different n_steps produce different results.\n")
    

