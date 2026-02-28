from engine_build.core.config import REGIMES
from .run_experiment import run_experiment
from engine_build.metrics.metrics import compute_fingerprint, aggregate_fingerprints

# setup runs over seed range and collect metrics => process metrics => validate => visualize


def run_batch_validation(regime: str = "stable"):

    seeds = [42, 1234, 5678, 91011, 121314]
    
    fingerprints_dict = {}

    for seed in seeds:
        fingerprint = compute_fingerprint(run_experiment(*REGIMES[regime], seed=seed), tail_start=300)
        fingerprints_dict[seed] = fingerprint
        
    
    aggregate_fingerprint = aggregate_fingerprints(fingerprints_dict.values())

    return regime, aggregate_fingerprint, fingerprints_dict



def main():
    


    regime, aggregate_fingerprint, fingerprints_dict = run_batch_validation("stable")
    print("================================================================")
    print(f"Regime: {regime}")
    print(f"Aggregate Fingerprint: ")
    for k, v in aggregate_fingerprint.items():
        print(f"    {k}: {v}")

    print("================================================================")
    print(f"Individual Fingerprints: ")
    for seed, fingerprint in fingerprints_dict.items():
        print(f"    Seed: {seed}")
        for k, v in fingerprint.items():
            print(f"        {k}: {v}")
        print("----------------------------------------------------------------")
    
    

if __name__ == "__main__":
    main()

