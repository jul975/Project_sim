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

    runner : BatchRunner = BatchRunner(runner_plan)

    batch_results : BatchRunResults = runner.run_batch(ticks=runner_plan.ticks)


    
    return batch_results


if __name__ == "__main__":
    pass
