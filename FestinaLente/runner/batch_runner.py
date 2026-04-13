"""Run deterministic experiment batches and collect per-run artifacts.

This module bridges compiled regimes and batch-level analytics by creating
seeded engines, stepping them for a fixed number of ticks, and packaging the
results into batch containers.
"""

from __future__ import annotations



import time

from FestinaLente.runner.factories import EngineBuildMap, SingleRunPlans, build_single_run_plans, build_single_runner
from FestinaLente.app.execution.workflows.compile_workflow import BatchPlan, EngineTemplate
from FestinaLente.runner.single_runner import SingleRunner



from FestinaLente.runner.results import BatchRunResults


class BatchRunner:
    """Execute multiple deterministic runs for a single compiled regime.

    Attributes:
        regime_config: Compiled regime shared by every run in the batch.
        n_runs: Number of runs to execute.
        batch_id: Batch-level seed used to derive per-run seed sequences.
        run_seeds: Deterministic per-run seed sequences generated from
            ``batch_id``.
        include_world_frames: Enables world-frame capture during execution.
        include_perf: Enables per-phase timing collection.
    """

    def __init__(
            self, 
            batch_plan : BatchPlan
            ) -> None:
        """Initialize a batch runner for one compiled regime configuration.

        Args:
            
        """
        

        self.batch_id : int = batch_plan.batch_id
        self.n_runs : int = batch_plan.n_runs
        self.run_tick_count : int = batch_plan.ticks

        self.engine_template : EngineTemplate = batch_plan.engine_template

        self.perf_profiling : bool = self.engine_template.perf_flag


        self.batch_run_plans : SingleRunPlans = build_single_run_plans(self.batch_id, self.n_runs ,self.engine_template)


        # if self.include_perf: 
        #     print("Performance flag is set. Running with performance profiling.")

        # if self.include_world_frames:
        #     print("World frame flag is set. Running with world frame capture.")

        # NOTE: still thinking about creating all single_runner class instance on init, wait for now

        
    def _run_batch_quick(self, ticks : int) -> BatchRunResults:

        batch_results: dict = {}
        
        plans_to_execute: dict[int, EngineBuildMap] = self.batch_run_plans.single_run_plans

        for run_index, runner_plan in plans_to_execute.items():
            single_runner: SingleRunner = build_single_runner(runner_plan)
            batch_results[run_index] = single_runner.run(ticks)

        return BatchRunResults(
            runs=batch_results, 
            batch_id= self.batch_id, 
            regime_config= self.engine_template.regime_config, 
            ticks= ticks, 
            batch_duration= None)




    def _run_batch_perf_profiling(self, ticks : int) -> BatchRunResults:
        """Run all configured seeds for the batch and collect their outputs.

        Args:
            ticks: Number of ticks to execute per run.

        Returns:
            Batch-level result container holding per-run artifacts and total
            batch duration.
        """

        

        batch_results: dict = {}

        batch_start_time: float = time.perf_counter()

        # NOTE: tmp entry point connection help. 

        plans_to_execute: dict[int, EngineBuildMap] = self.batch_run_plans.single_run_plans

        for run_index, runner_plan in plans_to_execute.items():
            single_runner: SingleRunner = build_single_runner(runner_plan)
            batch_results[run_index] = single_runner.run(ticks)

        batch_end_time: float = time.perf_counter()
        batch_duration: float = batch_end_time - batch_start_time
        
        return BatchRunResults(
            runs=batch_results, 
            batch_id= self.batch_id, 
            regime_config= self.engine_template.regime_config, 
            ticks= ticks, 
            batch_duration= batch_duration)
    

    def run_batch(self, ticks) -> BatchRunResults:
        if self.perf_profiling:
            return self._run_batch_perf_profiling(ticks)
        return self._run_batch_quick(ticks)



if __name__ == "__main__":
    pass
