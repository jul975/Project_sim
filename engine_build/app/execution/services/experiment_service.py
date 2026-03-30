from __future__ import annotations

from engine_build.analytics.batch_analytics import AnalysisConfig, analyze_batch
from engine_build.analytics.regime_summary import summarise_regime, classify_regime
from engine_build.app.execution.context import ExecutionContext
from engine_build.app.execution.defaults import EXPERIMENT_DEFAULTS
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.runner.batch_runner import BatchRunner
from engine_build.app.presentation.experiment_console import (
    print_experiment_spec,
    print_summarize_analytics,
)
from engine_build.visualisation.plot_run import (
    plot_batch_metrics,
    plot_single_run_metrics,
    plot_world_view_summary,
    plot_world_view_samples,
)


def run_experiment(context: ExecutionContext) -> int:
    if context.regime is None:
        raise ValueError("Experiment mode requires a regime.")

    regime_spec = get_regime_spec(context.regime)
    regime_config = compile_regime(regime_spec)

    ticks = context.ticks if context.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = context.runs if context.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    print_experiment_spec(regime_spec)

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=runs,
        batch_id=context.seed,
        include_world_frames=context.features.capture_world_frames,
        include_perf=context.features.profile,
    )

    batch_results = runner.run_batch(ticks=ticks)

    batch_analysis = analyze_batch(
        batch_results,
        AnalysisConfig(
            include_perf=context.features.profile,
            include_world_frames=context.features.capture_world_frames,
            regime_label=context.regime,
        ),
    )

    summary = summarise_regime(batch_analysis)
    regime_class = classify_regime(summary)

    print_summarize_analytics(
        batch_analysis=batch_analysis,
        n_runs=runs,
        ticks=ticks,
        regime_class=regime_class,
        summary=summary,
    )

    if context.features.plot:
        plot_batch_metrics({i: ra.metrics for i, ra in batch_results.runs.items()})

    if context.features.plot_dev:
        first_metrics = batch_results.runs[0].metrics
        if first_metrics is None:
            raise ValueError("Missing metrics for run 0")
        plot_single_run_metrics(first_metrics, run_id=0)

        if context.features.capture_world_frames:
            plot_world_view_summary(first_metrics)
            plot_world_view_samples(first_metrics)

    return 0
























"""from engine_build.visualisation.plot_run import plot_batch_metrics
from engine_build.visualisation.plot_run import plot_single_run_metrics, plot_world_view_summary, plot_world_view_samples

from engine_build.analytics.batch_analytics import analyze_batch
from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import Runner, BatchRunResults
from engine_build.app.execution.default import EXPERIMENT_DEFAULTS

from engine_build.experiments.experiment_output import print_experiment_spec, print_summarize_analytics

from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.compiled import CompiledRegime

from engine_build.app.cli.requests import ExperimentRequest




Owns:
        compile regime
        build runner
        run batch
        call analytics
        build report object

from engine_build.analytics.summaries.regime_summary import (
    summarise_regime,
    classify_regime,
    RegimeSummary,
    RegimeClass,
)
from engine_build.analytics.batch_analytics import AnalysisConfig




## return report object
def run_experiment_mode(request : ExperimentRequest) -> int:

    # 1. compile regime
    regime_spec = get_regime_spec(request.regime)
    regime_config : CompiledRegime = compile_regime(regime_spec)
    print_experiment_spec(regime_spec)

    ticks = request.ticks if request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    n_runs = request.runs if request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    # 2. build runner
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

    # 3. analyze batch
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

    # 4. build report object

    return 0


if __name__ == "__main__":
    pass"""
