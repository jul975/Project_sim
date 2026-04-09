from __future__ import annotations


from engine_build.app.service_models.service_request_container import ServiceRequest

from engine_build.app.execution.presenters.console import (
    print_experiment_spec,
    print_summarize_analytics,
)
from engine_build.visualisation.plot_run import (
    plot_batch_metrics,
    plot_single_run_metrics,
    plot_world_view_summary,
    plot_world_view_samples,
)

from engine_build.analytics.pipelines.analyze_batch import BatchAnalysis

def present_experiment(experiment_request: ServiceRequest , batch_analysis: BatchAnalysis) -> int:
    
    if experiment_request.features.plotting:
        plot_batch_metrics(batch_analysis)

    if experiment_request.features.plot_dev:
        first_metrics = batch_analysis.all_runs[0].metrics
        if first_metrics is None:
            raise ValueError("Missing metrics for run 0")
        plot_single_run_metrics(first_metrics, run_id=0)

        if experiment_request.features.capture_world_frames:
            plot_world_view_summary(first_metrics)
            plot_world_view_samples(first_metrics)