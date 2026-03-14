from engine_build.visualisation.plot_run import plot_metrics 
from engine_build.visualisation.dev_plot import plot_development_metrics

from engine_build.analytics.batch_analytics import analyze_batch


from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import Runner, BatchRunResults
from engine_build.execution.default import EXPERIMENT_DEFAULTS




from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime

from engine_build.analytics.regime_summery import summarise_regime, classify_regime, RegimeSummary, RegimeClass

from engine_build.analytics.fingerprint import AggregatedFingerprint
import numpy as np





def summarize_analytics(batch_analysis : BatchAnalysis , n_runs : int , ticks : int, regime_class : RegimeClass, summary : RegimeSummary ) -> None:
    """ prints a summary of the results. """
    final_populations = []
    for _, run_results in batch_analysis.batch_metrics.items():
        final_populations.append(run_results.metrics.population[-1])

    final_populations = np.array(final_populations)

    mean_final = np.mean(final_populations)
    std_final = np.std(final_populations)
    agg : AggregatedFingerprint = batch_analysis.aggregate_fingerprint

    print("============================================================")
    print("MODE: EXPERIMENT")
    print(f"REGIME: {regime_class.value}")
    print(f"RUNS: {n_runs}")
    print(f"BATCH_DURATION: {batch_analysis.batch_duration:.2f}s")
    print(f"TICKS: {ticks}")
    print(f"TAIL_START: {batch_analysis.tail_start}")
    print("")
    print("End-State Summary:")
    print(f"    final_population_mean : {mean_final:.2f}")
    print(f"    final_population_std  : {std_final:.2f}")
    print(f"    final_population_cv   : {std_final / mean_final:.4f}" if mean_final > 0 else "    final_population_cv   : nan")

    print("")
    print("Tail-Window Regime Summary:")
    print(f"    mean_population_over_runs     : {agg.mean_population_over_runs:.3f}")
    print(f"    std_mean_population_over_runs : {agg.std_mean_population_over_runs:.3f}")
    print(f"    extinction_rate               : {agg.extinction_rate:.3f}")
    print(f"    cap_hit_rate                  : {agg.cap_hit_rate:.3f}")
    print(f"    birth_death_ratio             : {agg.birth_death_ratio:.3f}")
    print(f"    mean_time_cv_over_runs        : {agg.mean_time_cv_over_runs:.3f}")
    print("\n")
    print(f"    batch_near_cap_rate           : {agg.batch_near_cap_rate:.3f}")
    print(f"    batch_low_population_rate     : {agg.batch_near_low_population_rate:.3f}")
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

    summary : RegimeSummary = summarise_regime(batch_analysis)
    regime_class : RegimeClass = classify_regime(summary)

    summarize_analytics(batch_analysis, ticks=ticks, n_runs=n_runs, regime_class=regime_class, summary=summary)

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




"""
============================================================
MODE: EXPERIMENT
REGIME: stable
RUNS: 10
TICKS: 1000
TAIL_START: 750

End-State Summary:
    final_population_mean : 114.50
    final_population_std  : 7.50
    final_population_cv   : 0.0655

Tail-Window Regime Summary:
    mean_population_over_runs     : 117.972
    std_mean_population_over_runs : 1.842
    extinction_rate               : 0.000
    cap_hit_rate                  : 0.000
    birth_death_ratio             : 0.999
    mean_time_cv_over_runs        : ...

============================================================




"""


