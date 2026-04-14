
import numpy as np

from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, EXPERIMENT_DEFAULTS

def generate_run_sequences(master_seed: int = DEFAULT_MASTER_SEED, n_runs: int = EXPERIMENT_DEFAULTS["runs"]) -> dict[int, np.random.SeedSequence]:
    """ I do NOT return master seed, state mutation must be avoided, 
        therefore the master seed is used only to generate the run seeds.
        And NEVER touched again 
    """
    
    ss = np.random.SeedSequence(master_seed)
    seed_sequences = ss.spawn(n_runs)
    return {run_id: seq for run_id, seq in enumerate(seed_sequences, start=1)}
