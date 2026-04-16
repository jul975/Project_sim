"""Present processed workflow outputs to the selected user-facing surfaces.

This module owns presentation-stage side effects such as console output,
plots, and animations. It does not execute simulations or derive
analytics from raw run artifacts.
"""



from __future__ import annotations

from FestinaLente.app.execution.workflows.compile_workflow import PresentationPlan


from ...service_models.service_request_container import ServiceRequest

from app.execution.presenters.console import (
    print_experiment_spec,
    print_summarize_analytics,
)
from app.execution.presenters.plotting.plot_run import (
    plot_batch_metrics,
    plot_single_run_metrics,
    plot_world_view_summary,
    plot_world_view_samples,
)

from analytics.processing.process_batch import BatchAnalysis

def present_experiment(presentation_plan: PresentationPlan , batch_analysis: BatchAnalysis) -> None:
    
    
    if presentation_plan.plotting:
        plot_batch_metrics(batch_analysis)

    if presentation_plan.dev_plotting:
        first_metrics = batch_analysis.all_runs[0].metrics
        if first_metrics is None:
            raise ValueError("Missing metrics for run 0")
        plot_single_run_metrics(first_metrics, run_id=0)

    # if experiment_request.features.capture_world_frames:
    if presentation_plan.world_view:
        plot_world_view_summary(first_metrics)
        plot_world_view_samples(first_metrics)


    return None