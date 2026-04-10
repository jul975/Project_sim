"""Run deterministic experiment batches and collect per-run artifacts.

This module bridges compiled regimes and batch-level analytics by creating
seeded engines, stepping them for a fixed number of ticks, and packaging the
results into batch containers.
"""

from engine_build.app.service_models.default import DEFAULT_MASTER_SEED
from engine_build.core.contracts.step_results import StepReport



import numpy as np


import time

from engine_build.runner.results import PhaseProfile, RunArtifacts, BatchRunResults
from engine_build.app.execution.workflows.compile_workflow import BatchPlan, EngineTemplate
from engine_build.runner.seeds import generate_run_sequences





def reset_phase_profile(phase_profile : PhaseProfile) -> None:
    """Clear accumulated timing fields on a phase profile.

    Args:
        phase_profile: Mutable profile that stores cumulative per-phase timing
            totals for one run.
    """
    phase_profile.movement = 0.0
    phase_profile.interaction = 0.0
    phase_profile.biology = 0.0
    phase_profile.commit = 0.0

    phase_profile.commit_setup = 0.0
    phase_profile.commit_deaths = 0.0
    phase_profile.commit_births = 0.0
    phase_profile.commit_resource_regrowth = 0.0
    

def add_perf_to_profile(phase_profile : PhaseProfile, step_report : StepReport) -> None:
    """Accumulate step-level timing data into a run-level phase profile.

    Args:
        phase_profile: Mutable profile receiving cumulative timing totals.
        step_report: Per-step report produced by the engine.
    """

    phase_profile.movement += step_report.step_profile.movement
    phase_profile.interaction += step_report.step_profile.interaction
    phase_profile.biology += step_report.step_profile.biology
    phase_profile.commit += step_report.step_profile.commit

    phase_profile.commit_setup += step_report.commit_report.commit_profile.setup
    phase_profile.commit_deaths += step_report.commit_report.commit_profile.deaths
    phase_profile.commit_births += step_report.commit_report.commit_profile.births
    phase_profile.commit_resource_regrowth += step_report.commit_report.commit_profile.resource_regrowth

# NOTE: batch runner should create either all single runners or all engines directly on init, and then run them in sequence in run batch. This will allow for more flexible runner orchestration and clearer separation of concerns.




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

        self.all_batch_seeds : dict = generate_run_sequences(self.batch_id, self.n_runs)


        # if self.include_perf: 
        #     print("Performance flag is set. Running with performance profiling.")

        # if self.include_world_frames:
        #     print("World frame flag is set. Running with world frame capture.")

        # NOTE: still thinking about creating all single_runner class instance on init, wait for now

        







    def run_batch(self, 
                         ticks : np.int64, 

                         ) -> BatchRunResults:
        """Run all configured seeds for the batch and collect their outputs.

        Args:
            ticks: Number of ticks to execute per run.

        Returns:
            Batch-level result container holding per-run artifacts and total
            batch duration.
        """

        batch_start_time = time.perf_counter()

        # NOTE: tmp entry point connection help. 


        


        batch_data: BatchRunResults = BatchRunResults(runs={}, batch_id= self.batch_id, regime_config= self.regime_config, ticks= ticks, batch_duration= None)

        for i, seed in enumerate(self.run_seeds):

            run_results : RunArtifacts = self.run_single(seed, ticks)
            batch_data.runs[i] = run_results  

            


            

        batch_end_time = time.perf_counter()
        batch_duration = batch_end_time - batch_start_time
        batch_data.batch_duration = batch_duration

        batch_data.max_agent_count = batch_data.runs[0].engine_final.max_agent_count



        return batch_data



if __name__ == "__main__":
    pass
