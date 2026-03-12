from engine_build.visualisation.plot_run import plot_metrics 
from engine_build.visualisation.dev_plot import plot_development_metrics

from engine_build.analytics.batch_analytics import analyze_batch


from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import Runner, BatchRunResults
from engine_build.execution.default import EXPERIMENT_DEFAULTS



from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime


from engine_build.analytics.fingerprint import AggregatedFingerprint
import numpy as np




def summarize_analytics(batch_analysis : BatchAnalysis , n_runs : int , ticks : int ) -> None:
    """ prints a summary of the results. """
    final_populations = []
    for _, run_results in batch_analysis.batch_metrics.items():
        final_populations.append(run_results.metrics.population[-1])

    final_populations = np.array(final_populations)

    mean_final = np.mean(final_populations)
    std_final = np.std(final_populations)

    print("============================================================")
    print(f"MODE: EXPERIMENT")
    print(f"REGIME: {batch_analysis.regime_label}")
    print(f"RUNS: {n_runs}")
    print(f"TICKS: {ticks}")
    print("")
    print("Final Population:")
    print(f"    mean: {mean_final:.2f}")
    print(f"    std : {std_final:.2f}")
    print(f"    cv : {( std_final / mean_final * 100 ):.2f} %")
    print(f"    ** cv = std/mean")
    print(f"        -   cv = 0.05 → strict equilibrium")
    print(f"        -   cv = 0.1 → moderate tolerance")
    print(f"        -   cv = 0.2 → loose tolerance")
    print("")
    print("Aggregate Fingerprint:")
    agg : AggregatedFingerprint = batch_analysis.aggregate_fingerprint

    print('Population Metrics:')
    print(f"    mean_population : {agg.mean_population_over_runs:.3f}")
    print(f"    std_population  : {agg.std_mean_population_over_runs:.3f}")
    print(f"    extinction_rate : {agg.extinction_rate:.3f}")
    print(f"    cap_hit_rate    : {agg.cap_hit_rate:.3f}")
    print(f"    birth_death_ratio: {agg.birth_death_ratio:.3f}")

    print('')
    print('Occupancy Metrics:')
    """print(f"    mean_occupied_cells: {agg.mean_occupied_cells:.3f}")
    print(f"    mean_mean_occupancy: {agg.mean_mean_occupancy:.3f}")
    print(f"    mean_max_occupancy: {agg.mean_max_occupancy:.3f}")
    print(f"    mean_ratio_t: {agg.mean_ratio_t:.3f}")"""
    print("============================================================")         


if __name__ == "__main__":
    pass


# NOTE: 
        #   DECLARATIVE EXPERIMENT DEFINITION ONLY
        # 
        #   -   No logic, no control flow, no dependencies, no implementation details.


def run_experiment_mode(args) -> None:
    regime_spec = get_regime_spec(args.regime)
    regime_config = compile_regime(regime_spec)

    ticks = args.ticks if args.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    n_runs = args.runs if args.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    runner = Runner(
        regime_config=regime_config,
        n_runs=n_runs,
        batch_id=args.seed
    )

    batch_results : BatchRunResults = runner.run_regime_batch(ticks=ticks)
    batch_analysis : BatchAnalysis = analyze_batch(batch_results, regime_label=args.regime)

    summarize_analytics(batch_analysis, ticks=ticks, n_runs=n_runs)

    if args.plot:
        plot_metrics({i: ra.metrics for i, ra in batch_results.runs.items()})

    if args.plot_dev:
        plot_development_metrics(batch_results, runner.batch_id)

"""
Spatial Concentration ratio:

| Ratio | Meaning               |
| ----- | --------------------- |
| ~1    | uniform distribution  |
| 2-4   | healthy clustering    |
| >6    | strong monopolization |

max_occupancy/mean_occupancy
"""



