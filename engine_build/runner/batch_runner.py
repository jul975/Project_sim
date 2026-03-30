from engine_build.core.engine import Engine
from engine_build.app.execution_model.default import DEFAULT_MASTER_SEED
from engine_build.core.step_results import StepReport


from engine_build.regimes.compiled import CompiledRegime

from engine_build.analytics.metrics.metrics import SimulationMetrics
import numpy as np


import time

from engine_build.runner.results import PhaseProfile, RunArtifacts, BatchRunResults
from engine_build.runner.seeds import generate_run_sequences
"""
 


"""





def reset_phase_profile(phase_profile : PhaseProfile) -> None:
    """ resets phase profile. """
    phase_profile.movement = 0.0
    phase_profile.interaction = 0.0
    phase_profile.biology = 0.0
    phase_profile.commit = 0.0

    phase_profile.commit_setup = 0.0
    phase_profile.commit_deaths = 0.0
    phase_profile.commit_births = 0.0
    phase_profile.commit_resource_regrowth = 0.0
    

def add_perf_to_profile(phase_profile : PhaseProfile, step_report : StepReport) -> None:
    """ adds tick level perf to run profile. """

    phase_profile.movement += step_report.step_profile.movement
    phase_profile.interaction += step_report.step_profile.interaction
    phase_profile.biology += step_report.step_profile.biology
    phase_profile.commit += step_report.step_profile.commit

    phase_profile.commit_setup += step_report.commit_report.commit_profile.setup
    phase_profile.commit_deaths += step_report.commit_report.commit_profile.deaths
    phase_profile.commit_births += step_report.commit_report.commit_profile.births
    phase_profile.commit_resource_regrowth += step_report.commit_report.commit_profile.resource_regrowth





class BatchRunner:
    def __init__(
            self, 
            regime_config : CompiledRegime , 
            n_runs : int, 
            batch_id : int| None = None,
            include_world_frames : bool = False,
            include_perf : bool = False,
            ) -> None:
        """ 
            set up batch run with batch_id == batch_seed. 
            will set up run seeds internally at initialization.
         """
        
        self.regime_config = regime_config
        self.n_runs = n_runs
        self.batch_id = batch_id if batch_id is not None else DEFAULT_MASTER_SEED

        self.run_seeds = generate_run_sequences(self.batch_id , n_runs)

        self.include_world_frames = include_world_frames
        self.include_perf = include_perf


#############################################################
    # NOTE: world_frames is a temp solution, the flag is getting drilled from to high up 
    def run_single(self, seed: np.random.SeedSequence, ticks: int) -> RunArtifacts:
        eng = Engine(
            seed,
            self.regime_config,
            perf_flag=self.include_perf,
            world_frame_flag=self.include_world_frames,
        )
        metrics = SimulationMetrics(eng.max_agent_count)
        phase_profile = PhaseProfile() if self.include_perf else None

        if phase_profile is not None:
            reset_phase_profile(phase_profile)

        for _ in range(ticks):
            step_report = eng.step()
            metrics.record(step_report=step_report)

            if phase_profile is not None:
                if step_report.step_profile is None:
                    raise ValueError("Expected step_profile when include_perf=True")
                add_perf_to_profile(phase_profile, step_report)

        return RunArtifacts(
            engine_final=eng,
            metrics=metrics,
            seed=seed,
            phase_profile=phase_profile,
        )
    


#############################################################
    def _continue_run(self, eng : Engine, metrics : SimulationMetrics, ticks : np.int64) -> RunArtifacts:
        """ continues a run for a given engine and metrics. """
        phase_profile = PhaseProfile()
        for _ in range(ticks):
            step_report : StepReport = eng.step()
            metrics.record(step_report = step_report)

        return RunArtifacts(engine_final=eng, 
                            metrics= metrics, 
                            seed= eng.master_ss,
                            phase_profile= phase_profile,
                            
                            )



#############################################################
    def run_batch(self, 
                         ticks : np.int64, 

                         ) -> BatchRunResults:
        """ only return aggregates and results."""

        batch_start_time = time.perf_counter()

        # NOTE: tmp entry point connection help. 
        if self.include_perf: 
            print("Performance flag is set. Running with performance profiling.")

        if self.include_world_frames:
            print("World frame flag is set. Running with world frame capture.")

        


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
