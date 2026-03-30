
import numpy as np

def generate_run_sequences(master_seed: int, n_runs: int) -> list[np.random.SeedSequence]:
    """ I do NOT return master seed, state mutation must be avoided, 
        therefore the master seed is used only to generate the run seeds.
        And NEVER touched again 
    """
    ss = np.random.SeedSequence(master_seed)
    return ss.spawn(n_runs)
