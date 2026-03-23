from engine_build.visualisation.plot_run import plot_batch_metrics
from engine_build.visualisation.plot_run import plot_single_run_metrics, plot_world_view_summary, plot_world_view_samples

from engine_build.analytics.batch_analytics import analyze_batch
from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import Runner, BatchRunResults
from engine_build.execution.default import EXPERIMENT_DEFAULTS

from engine_build.experiments.experiment_output import print_experiment_spec, print_summarize_analytics

from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.compiled import CompiledRegime

from engine_build.analytics.regime_summery import (
    summarise_regime,
    classify_regime,
    RegimeSummary,
    RegimeClass,
)
from engine_build.analytics.batch_analytics import AnalysisConfig





def run_experiment_mode(request) -> int:
    regime_spec = get_regime_spec(request.regime)
    regime_config : CompiledRegime = compile_regime(regime_spec)
    print_experiment_spec(regime_spec)

    ticks = request.ticks if request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    n_runs = request.runs if request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    runner = Runner(
        regime_config=regime_config,
        n_runs=n_runs,
        batch_id=request.seed,

        include_world_frames=request.world_frame_flag,
        include_perf=request.perf_flag,
    )

    batch_results: BatchRunResults = runner.run_regime_batch(
        ticks=ticks
    )

    batch_analysis: BatchAnalysis = analyze_batch(
        batch_results,
        AnalysisConfig(
            
            include_perf=request.perf_flag,
            include_world_frames=request.world_frame_flag,
            regime_label=request.regime,

        ),

    )

    summary: RegimeSummary = summarise_regime(batch_analysis)
    regime_class: RegimeClass = classify_regime(summary)

    print_summarize_analytics(
        batch_analysis,
        ticks=ticks,
        n_runs=n_runs,
        regime_class=regime_class,
        summary=summary,

    )

    if request.plot:
        plot_batch_metrics({i: ra.metrics for i, ra in batch_results.runs.items()})

    if request.plot_dev:
        first_metrics = batch_results.runs[0].metrics
        if first_metrics is None:
            raise ValueError("Missing metrics for run 0")

        plot_single_run_metrics(first_metrics, run_id=0)

        if request.world_frame_flag:
            plot_world_view_summary(first_metrics)
            plot_world_view_samples(first_metrics)
    return 0


if __name__ == "__main__":
    pass
