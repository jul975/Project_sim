from engine_build.core.engine import Engine
from engine_build.execution.default import DEFAULT_MASTER_SEED
from engine_build.core.step_results import StepReport


from engine_build.regimes.compiled import CompiledRegime

from engine_build.metrics.metrics import SimulationMetrics
import numpy as np
from dataclasses import dataclass
from typing import Dict

from engine_build.core.step_results import WorldView
import time
"""
    'the runner should own orchestration and lifecycle, not interpretation.'
CAVE:
        No math.
        No policy.
        No regime logic.
        No state.
        Just orchestration.


        input: config, seeds, ticks
        output: structured result object

        (master_seed)
              ↓
        SeedSequence
            ↓ spawn(n)
        ┌────┬────┬────┬────┬────┐
        SS0  SS1  SS2  SS3  SS4
        └────┴────┴────┴────┴────┘
            ↓     ↓     ↓     ↓
        run  run  run  run  run

        on engine level we have:
            SS2
              ↓ spawn(...)
            world_ss
            move_ss
            repro_ss
            energy_ss


"""



@dataclass
class PhaseProfile:
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0

    commit_setup: float = 0.0
    commit_deaths: float = 0.0
    commit_births: float = 0.0
    commit_resource_regrowth: float = 0.0






 
# raw one run results
@dataclass
class RunArtifacts:
    engine_final : Engine | None = None
    metrics : SimulationMetrics | None = None
    seed : np.random.SeedSequence | None = None
    phase_profile : PhaseProfile | None = None

    # world frames optional 
    # NOTE: world frames part of metrics now (SimulationMetrics.world_view)
    # world_frames : WorldFrames | None = None


# raw batch results
@dataclass
class BatchRunResults:
    runs : Dict[np.int64, RunArtifacts]
    batch_id : int | None = None
    regime_config : CompiledRegime | None = None
    ticks : np.int64 | None = None
    batch_duration : float | None = None
    max_agent_count : int | None = None



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



def generate_run_sequences(master_seed: int, n_runs: int) -> list[np.random.SeedSequence]:
    """ I do NOT return master seed, state mutation must be avoided, 
        therefore the master seed is used only to generate the run seeds.
        And NEVER touched again 
    """
    ss = np.random.SeedSequence(master_seed)
    return ss.spawn(n_runs)


class Runner:
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
    def run_regime_batch(self, 
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
