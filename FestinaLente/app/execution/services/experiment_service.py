"""Run experiment-mode execution workflows and present their results.

This module owns the experiment service boundary: execute the batch workflow,
derive analytics products, and trigger optional visual outputs.
"""

from __future__ import annotations


from FestinaLente.app.execution.workflows.compile_workflow import CompiledWorkflowPlan, compile_workflow_plans

from FestinaLente.app.service_models.service_request_container import PresentationRequest, ProcessingRequest, RunnerRequest, ServiceRequest, ServiceRequestMeta




# NOTE: Service should own the workflow, not build requests. --- IGNORE ---
# NOTE: Service should be changed to compute clean entry point for runner. 
        # => Runner should get clean entry package, WILL BE CENTRAL SOURCE OF TRUTH FOR ALL ENTRY POINTS. 



def experiment_service_call(experiment_request: ServiceRequest) -> CompiledWorkflowPlan:
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
    
    # 1) unpack service request for easy access to all layers of the request
    service_meta: ServiceRequestMeta = experiment_request.service_request_meta
    service_runner: RunnerRequest = experiment_request.runner_request
    service_processing: ProcessingRequest = experiment_request.processing_request
    service_presentation: PresentationRequest = experiment_request.presentation_request
    
    if experiment_request.service_request_meta.regime is None:
        raise ValueError("Experiment mode requires a regime.")
    

    return compile_workflow_plans(experiment_request)

    



"""
    # 2) Process service request into workflow plans.
    ################## SERVICE REQUEST Processing => COMPILE WORKFLOW PLANS
                     # => AFTER this point, Workflow Plans are source of truth for execution, processing and presentation.
 

    # 3) Execute workflow plans.
    ################## Workflow orchestration

    # NOTE: print entry point summary here
    ##################

    ################## EXEXCUTION PLAN  => RUN RUNNER
    # batch_results = execution_workflow.run()


    ################## PROCESSING PLAN => ANALYZE RESULTS
    # batch_analysis = processing_workflow.run(batch_results)
    # CLASSIFICATION, SUMMARIZATION, AND OTHER ANALYTIC DERIVATIONS SHOULD BE PART OF THIS WORKFLOW

    ################## PRESENTATION PLAN => PRESENT RESULTS
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

"""





if __name__ == "__main__":
    pass










