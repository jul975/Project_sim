"""Run the simulation execution stage from a compiled runner plan.

This module owns runner construction and batch execution for workflow
plans. It returns raw execution artifacts without performing downstream
analysis or presentation.
"""

from __future__ import annotations

from FestinaLente.app.execution.workflows.compile_workflow import BatchPlan


from FestinaLente.runner.batch_runner import BatchRunner, BatchRunResults



def Execute_workflow(runner_plan: BatchPlan) -> BatchRunResults:
    """ build batch, run batch and return batch results from context. """

    
    # processing_plan = workflow_plan.processing_plan
    # presentation_plan = workflow_plan.presentation_plan





    runner : BatchRunner = BatchRunner(runner_plan)

    batch_results : BatchRunResults = runner.run_batch(ticks=BatchPlan.ticks)


    
    return batch_results


if __name__ == "__main__":
    pass