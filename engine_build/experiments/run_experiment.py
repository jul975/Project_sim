from engine_build.visualisation.plot_run import plot_metrics 
from engine_build.runner.regime_runner import BatchRunner, RegimeBatchResults
from engine_build.regimes.registry import get_regime_config
from engine_build.execution.default import EXPERIMENT_DEFAULTS
from engine_build.analytics.fingerprint import AggregatedFingerprint
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
    # NOTE: 
        #   -   want to standerdize default beheavior and not let that be controled by main.py

    ticks = args.ticks if args.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    n_runs = args.runs if args.runs is not None else EXPERIMENT_DEFAULTS["runs"]
    
    runner = BatchRunner(
        regime_config = regime_config,
        ticks = ticks,
        n_runs = n_runs,
        batch_id = args.seed
        
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
    agg : AggregatedFingerprint = results.aggregate_fingerprint

    print(f"    mean_population : {agg.mean_population_over_runs:.3f}")
    print(f"    std_population  : {agg.std_mean_population_over_runs:.3f}")
    print(f"    extinction_rate : {agg.extinction_rate:.3f}")
    print(f"    cap_hit_rate    : {agg.cap_hit_rate:.3f}")
    print(f"    birth_death_ratio: {agg.birth_death_ratio:.3f}")
    print("============================================================")         


if __name__ == "__main__":
    pass