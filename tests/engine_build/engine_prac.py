import numpy as np

class EntropyError(Exception):
    """Custom error for when a system invariant is violated."""
    pass

class Engine:
    def __init__(self, seed, initial_energies):
        # PROBLEM 1: RNG Isolation
        # We create a private 'tank' of randomness tied only to this instance
        self.rng = np.random.default_rng(seed)
        
        # State Initialization
        self.tick = 0
        self.total_sum = 0
        self.energies = initial_energies # This is our 'S(t)'
        
    def validate_invariants(self):
        # PROBLEM 2: The Invariant Gatekeeper
        # Check if any energy value is negative
        for energy in self.energies:
            if energy < 0:
                raise EntropyError(f"Invariant Violated: Energy dropped to {energy} at tick {self.tick}")

    def step(self, metabolic_rate):
        """Advances the universe by one discrete time step."""
        # 1. Generate random integer (Problem 1)
        # Note: we use self.rng, NOT np.random.randint
        random_val = self.rng.integers(1, 101) 
        self.total_sum += random_val
        
        # 2. Update agent energies (Problem 2)
        # S(t+1) calculation
        self.energies = [e - metabolic_rate for e in self.energies]
        
        # 3. Enforce the laws of the universe
        self.validate_invariants()
        
        # 4. Advance logical time
        self.tick += 1

    def run(self, n_steps, metabolic_rate):
        """Runs the simulation loop."""
        for _ in range(n_steps):
            self.step(metabolic_rate)
        return self.total_sum, self.energies

# --- TESTING THE IMPLEMENTATION ---

if __name__ == "__main__":
    # Test 1: Deterministic Ghost (Problem 1)
    seed_val = 42
    steps = 10
    
    eng1 = Engine(seed=seed_val, initial_energies=[10, 10])
    sum1, energies1 = eng1.run(steps, metabolic_rate=0.5)
    
    eng2 = Engine(seed=seed_val, initial_energies=[10, 10])
    sum2, energies2 = eng2.run(steps, metabolic_rate=0.5)
    
    print(f"Run 1 Sum: {sum1}")
    print(f"Run 2 Sum: {sum2}")
    print(f"Run 1 Energies: {energies1}")
    print(f"Run 2 Energies: {energies2}")
    assert sum1 == sum2, "FAILED: Runs with same seed must be identical!"
    print("SUCCESS: Determinism confirmed.\n")

    # Test 2: Invariant Gatekeeper (Problem 2)
    print("Testing Invariants...")
    try:
        # Starting with 5 energy, losing 2 per tick. 
        # Should crash on tick 3 (5 -> 3 -> 1 -> -1)
        crash_engine = Engine(seed=1, initial_energies=[5])
        crash_engine.run(n_steps=10, metabolic_rate=2)
    except EntropyError as e:
        print(f"SUCCESS: Caught expected error: {e}")