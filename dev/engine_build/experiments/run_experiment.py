from engine_build.visualisation.plot_run import plot_metrics 
from engine_build.runner.regime_runner import BatchRunner, RegimeBatchResults
from engine_build.regimes.registry import get_regime_config
from engine_build.execution.default import EXPERIMENT_DEFAULTS
import numpy as np



# NOTE: 
        #   DECLARATIVE EXPERIMENT DEFINITION ONLY
        # 
        #   -   No logic, no control flow, no dependencies, no implementation details.
        #  
        #   -   STABLE_REGIME = SimulationConfig(...)
        #   -   GROWTH_REGIME = SimulationConfig(...)
        #   -   COLLAPSE_REGIME = SimulationConfig(...)

def run_experiment_mode(args) -> None:
    """ main entry point """
    regime_config = get_regime_config(args.regime)
    ticks, n_runs = EXPERIMENT_DEFAULTS["ticks"], EXPERIMENT_DEFAULTS["runs"]
    
    runner = BatchRunner(
        regime_config = regime_config,
        ticks = ticks,
        n_runs = n_runs
        
    )

    results : RegimeBatchResults = runner.run_regime_batch()
    summarize_results(results, ticks, n_runs, args.regime)

    if args.plot:
        plot_metrics(results.batch_metrics)








def summarize_results(results, ticks, n_runs, regime):
    final_pops = [
        m.population[-1] for m in results.batch_metrics.values()
    ]

    mean_final = np.mean(final_pops)
    std_final = np.std(final_pops)

    print("============================================================")
    print(f"MODE: EXPERIMENT")
    print(f"REGIME: {regime}")
    print(f"RUNS: {n_runs}")
    print(f"TICKS: {ticks}")
    print("")
    print("Final Population:")
    print(f"    mean: {mean_final:.2f}")
    print(f"    std : {std_final:.2f}")
    print("")
    print("Aggregate Fingerprint:")
    for k, v in results.aggregate_fingerprint.items():
        print(f"    {k}: {v:.3f}")
    print("============================================================")         


if __name__ == "__main__":
    pass