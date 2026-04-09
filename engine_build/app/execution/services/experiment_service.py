"""Run experiment-mode execution workflows and present their results.

This module owns the experiment service boundary: execute the batch workflow,
derive analytics products, and trigger optional visual outputs.
"""

from __future__ import annotations

from engine_build.analytics.summaries.regime_summary import summarise_regime
from engine_build.analytics.classification.regime_classification import classify_regime
from engine_build.app.execution.presenters.experiment_presenters import present_experiment
from engine_build.app.execution.workflows.compile_workflow import compile_workflow
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
from engine_build.app.execution.workflows.workflow_runner import build_and_run_batch

from engine_build.analytics.pipelines.analyze_batch import analyze_batch, BatchAnalysis

# NOTE: Service should own the workflow, not build requests. --- IGNORE ---
# NOTE: Service should be changed to compute clean entry point for runner. 
        # => Runner should get clean entry package, WILL BE CENTRAL SOURCE OF TRUTH FOR ALL ENTRY POINTS. 



def experiment_service_call(experiment_request: ServiceRequest) -> int:
    """Run an experiment workflow from a normalized service request.

    Args:
        context: Execution request carrying experiment settings, analysis
            controls, and optional presentation features.

    Returns:
        ``0`` when the experiment workflow completes successfully.

    Raises:
        ValueError: If experiment mode is requested without a regime, or if
            required metrics are missing for requested plot outputs.

    Notes:
        The request is expected to be pre-normalized by the app layer. This
        service owns orchestration of the experiment workflow but does not
        construct requests itself.
    """
    if experiment_request.regime is None:
        raise ValueError("Experiment mode requires a regime.")
    ################################ NEw #####################

    ################## SERVICE REQUEST PARSING
    execution_workflow = compile_workflow(experiment_request)    
    processing_workflow = compile_workflow(experiment_request)    
    presentation_workflow = compile_workflow(experiment_request)    

    ################## Workflow orchestration

    # NOTE: print entry point summary here
    ##################

    ################## WORKFLOW: RUN RUNNER
    # batch_results = execution_workflow.run()


    ################## WORKFLOW: ANALYZE RESULTS
    # batch_analysis = processing_workflow.run(batch_results)
    # CLASSIFICATION, SUMMARIZATION, AND OTHER ANALYTIC DERIVATIONS SHOULD BE PART OF THIS WORKFLOW

    ################## WORKFLOW: PRESENT RESULTS
    # presentation_workflow.run(batch_analysis)

    ################################ OLD #####################
    batch_results, analysis_context = build_and_run_batch(experiment_request)

    batch_analysis : BatchAnalysis = analyze_batch(batch_results, analysis_context)

        
    summary = summarise_regime(batch_analysis)
    regime_class = classify_regime(summary)

    print_summarize_analytics(
        batch_analysis=batch_analysis,


        regime_class=regime_class,
        summary=summary,
    )

    present_experiment(experiment_request, batch_analysis)


    return 0







if __name__ == "__main__":
    pass










