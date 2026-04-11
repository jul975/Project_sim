"""Run the simulation execution stage from a compiled runner plan.

This module owns runner construction and batch execution for workflow
plans. It returns raw execution artifacts without performing downstream
analysis or presentation.
"""

from __future__ import annotations

from engine_build.app.execution.workflows.compile_workflow import BatchPlan, CompiledWorkflowPlan


from engine_build.runner.batch_runner import BatchRunner, BatchRunResults



def Execute_workflow(workflow_plan: CompiledWorkflowPlan) -> BatchRunResults:
    """ build batch, run batch and return batch results from context. """

    runner_plan: BatchPlan = workflow_plan.running_plan
    # processing_plan = workflow_plan.processing_plan
    # presentation_plan = workflow_plan.presentation_plan



    # NOTE: temp need to move 
    # print_experiment_spec(regime_spec)

    runner : BatchRunner = BatchRunner(runner_plan)

    batch_results : BatchRunResults = runner.run_batch(ticks=ticks)

    # analysis_context = AnalysisContext(
    #     n_runs=runs,
    #     total_tics=ticks,
    #     tail_fraction=batch_request.tail_fraction,
    #     regime_label=batch_request.regime,
    #     compiled_regime=regime_config,
    #     options=AnalysisOptions(
    #         include_perf=batch_request.features.profiling,
    #         include_world_frames=batch_request.features.capture_world_frames,
    #     ),
    # )
    
    return batch_results


if __name__ == "__main__":
    pass