
## main entry point for runs
import numpy as np
from engine_build.core.config import SimulationConfig, REGIMES
from engine_build.runner.regime_runner import BatchRunner, RegimeRunResults
from engine_build.experiments.run_experiment import make_config
from engine_build.visualisation.plot_run import plot_metrics

import argparse

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from engine_build.metrics.metrics import SimulationMetrics

## NOTE: 
    # would call either validation or experiment routines. 
    # everything else is handled internally.


# NOTE: 
        #   -   for now, will implement experiment routine first

# calls selected config from experiments experiments 

# calls runner with config and seeds 





def run_main(regime : str , ticks : np.int64 , n_runs : int = 5) -> RegimeRunResults:
    """ run and return results of regime run. , NOTE: still need to unpack results, review current solution."""
    regime_config = pass_regime(regime)
    br = BatchRunner(regime_config=regime_config,ticks = ticks,n_runs = n_runs)
    return br.run_regime_batch()
     
    

def pass_regime(regime : str) -> SimulationConfig:
    return make_config(*REGIMES[regime])
    

def plot_runs(batch_metrics : dict[np.int64, "SimulationMetrics"]) -> None:
    plot_metrics(batch_metrics)
     
    





def print_results(aggregate_fingerprint : dict, fingerprints_dict : dict, regime : str) -> None:
     # temp function during refactoring
    print("================================================================")
    print(f"Aggregate Fingerprint: ")
    print(f"Regime: {regime}")
    print(f"Number of runs: {len(fingerprints_dict)}")
    print(f"len of batch_metrics: {len(fingerprints_dict.keys())}")
    print(f"Aggregate Fingerprint: ")
    for k, v in aggregate_fingerprint.items():
        print(f"    {k}: {v}")

    print("================================================================")






def main(
        regime : str = "stable",

        n_runs : int = 5,
        ticks : np.int64 = 1000,
        plot : bool = False
        ):
     
     results : RegimeRunResults = run_main(regime=regime,ticks = ticks, n_runs = n_runs)

     print_results(results.aggregate_fingerprint, results.fingerprints_dict, regime)

     if plot:
        plot_runs(results.batch_metrics)
    



if __name__ == "__main__":
        
        
        
        
        
        
        
    parser = argparse.ArgumentParser(description="Ecosystem Metrics Analysis Tool")

    parser.add_argument(
        "--regime",
        choices=["extinction", "stable", "saturated"],
        default="stable",
        help="Select regime type"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot results"
    )

    args = parser.parse_args()

    main(args.regime, plot=args.plot)