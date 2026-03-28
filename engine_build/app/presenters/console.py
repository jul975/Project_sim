
from engine_build.experiments.experiment_output import print_summarize_analytics
from engine_build.visualisation.plot_run import plot_batch_metrics, plot_single_run_metrics, plot_world_view_summary, plot_world_view_samples 

from engine_build.analytics.summaries.regime_summary import (
    summarise_regime,
    classify_regime,
    RegimeSummary,
    RegimeClass,
)
from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import BatchRunResults




from engine_build.app.cli.requests import ExperimentRequest
from engine_build.app.execution.context import ExecutionContext
from engine_build.app.execution.modes import ExecutionMode


def present_experiment_results(batch_analysis, ticks, n_runs, regime_class, summary, request):

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