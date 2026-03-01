
## main entry point for runs
import numpy as np
from engine_build.core.config import SimulationConfig, REGIMES
from engine_build.runner.regime_runner import run_regime_batch
from engine_build.experiments.run_experiment import make_config

import argparse

## NOTE: 
    # would call either validation or experiment routines. 
    # everything else is handled internally.


# NOTE: 
        #   -   for now, will implement experiment routine first

# calls selected config from experiments experiments 

# calls runner with config and seeds 

def run_main(regime : str , seeds : list[np.int64], ticks : np.int64) -> None:
    regime_config = pass_regime(regime)
    aggregate_fingerprint, fingerprints_dict = run_regime_batch(regime_config, seeds, ticks)
    return aggregate_fingerprint, fingerprints_dict
    

def pass_regime(regime : str) -> SimulationConfig:
    return make_config(*REGIMES[regime])
    

def print_results(aggregate_fingerprint : dict, fingerprints_dict : dict, regime : str, seeds : list[np.int64]) -> None:
     # temp function during refactoring
    print("================================================================")
    print(f"Aggregate Fingerprint: ")
    for k, v in aggregate_fingerprint.items():
        print(f"    {k}: {v}")

    print("================================================================")






def main(regime : str = "stable", seeds : list[np.int64] = [42, 1234, 5678, 91011, 121314], ticks : np.int64 = 1000):
     aggregate_fingerprint, fingerprints_dict = run_main(regime, seeds, ticks)
     print_results(aggregate_fingerprint, fingerprints_dict, regime, seeds)
    



if __name__ == "__main__":
        
        main()
        
        
        """
        parser = argparse.ArgumentParser(description="Ecosystem Metrics Analysis Tool")

        parser.add_argument(
            "--regime",
            choices=["extinction", "stable", "saturated"],
            default="stable",
            help="Select regime type"
        )

        args = parser.parse_args()

        if args.regime == "extinction":
            main("extinction")
        elif args.regime == "stable":
            main("stable")
        elif args.regime == "saturated":
            main("saturated")"""