from __future__ import annotations

from engine_build.analytics.summaries.regime_summary import summarise_regime
from engine_build.analytics.classification.regime_classification import classify_regime
from engine_build.app.execution_model.execution_context import ExecutionContext
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
from engine_build.app.execution.execute_service.execute import build_and_run_batch

from engine_build.analytics.pipelines.analyze_batch import analyze_batch, BatchAnalysis

# NOTE: Service should own the workflow, not build requests.



def run_experiment(context: ExecutionContext) -> int:
    if context.regime is None:
        raise ValueError("Experiment mode requires a regime.")

    

    batch_results, analysis_context = build_and_run_batch(context)

    batch_analysis : BatchAnalysis = analyze_batch(batch_results, analysis_context)

        
    summary = summarise_regime(batch_analysis)
    regime_class = classify_regime(summary)

    print_summarize_analytics(
        batch_analysis=batch_analysis,


        regime_class=regime_class,
        summary=summary,
    )

    if context.features.plotting:
        plot_batch_metrics(batch_analysis)

    if context.features.plot_dev:
        first_metrics = batch_analysis.all_runs[0].metrics
        if first_metrics is None:
            raise ValueError("Missing metrics for run 0")
        plot_single_run_metrics(first_metrics, run_id=0)

        if context.features.capture_world_frames:
            plot_world_view_summary(first_metrics)
            plot_world_view_samples(first_metrics)

    return 0







if __name__ == "__main__":
    pass











