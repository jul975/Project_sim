

from engine_build.analytics.observation.simulation_metrics import SimulationMetrics

from engine_build.app.execution.workflows.compile_workflow import EngineTemplate
from engine_build.core.contracts.step_results import StepReport
from engine_build.runner.batch_runner import add_perf_to_profile
from engine_build.runner.factories import build_engine
from engine_build.runner.results import PhaseProfile, RunArtifacts
from .factories import EngineBuildMap
from ..core.engine import Engine


import numpy as np

# NOTE: draft of separated runner



class SingleRunner:
    def __init__(self, engine_build_map : EngineBuildMap) -> None:

        engine_template: EngineTemplate = engine_build_map.engine_template
        
        self.perf_flag : bool = engine_template.perf_flag
        self.world_frame : bool = engine_template.world_frame_flag
        self.change_condition : bool = engine_template.change_condition
        

        self.engine : Engine = Engine(EngineBuildMap)

        # pass metrics-config obj in future
        self.metrics = SimulationMetrics(self.engine.max_agent_count)

    # conditional run definition for perf

    def _run_quick(self, ticks) -> RunArtifacts:
        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report=step_report)
        return RunArtifacts(
            engine_final=self.engine,
            metrics=self.metrics,
            seed=self.engine.master_ss,
            phase_profile=None, # NOTE: add phase profile to single runner if needed
        )
    
    def _run_perf_profiling(self, ticks) -> RunArtifacts:
        """ run with performance flag on """
        # NOTE: engine config needs to pass profiling flag, is done now
        phase_profile : PhaseProfile = PhaseProfile()

        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report=step_report)
        return RunArtifacts(
            engine_final=self.engine,
            metrics=self.metrics,
            seed=self.engine.master_ss,
            phase_profile=None, # NOTE: add phase profile to single runner if needed
        )
    
    

    def run(self, ticks: int) -> RunArtifacts:
        """ => single source of truth for runner"""
        if self.perf_flag:
            return self._run_perf_profiling(self, ticks)
        return self._run_quick(self, ticks)
            
    



    def continue_run(self, ticks : np.int64) -> RunArtifacts:
        """Continue an existing run using a live engine and metrics buffer."""
        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report = step_report)

        return RunArtifacts(engine_final=eng, 
                            metrics= metrics, 
                            seed= eng.master_ss,
                            phase_profile= None, # NOTE: add phase profile to single runner if needed
                            )
    



#############################################################
    # NOTE: world_frames is a temp solution, the flag is getting drilled from to high up 
    def run_single(self, seed: np.random.SeedSequence, ticks: int) -> RunArtifacts:
        """Run one seeded engine instance for a fixed number of ticks.

        Args:
            seed: Seed sequence used to initialize the engine.
            ticks: Number of ticks to execute.

        Returns:
            Run artifacts containing the final engine, collected metrics, and
            optional phase profile.
        """
        eng = Engine(
            seed,
            self.regime_config,
            perf_flag=self.include_perf,
            world_frame_flag=self.include_world_frames,
        )
        metrics = SimulationMetrics(eng.max_agent_count)
         if self.include_perf else None

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
        """Continue an existing run using a live engine and metrics buffer.

        Args:
            eng: Existing engine state to continue stepping.
            metrics: Metrics object that should continue recording into the
                same run history.
            ticks: Additional number of ticks to execute.

        Returns:
            Run artifacts containing the updated engine and metrics objects.
        """
        phase_profile = PhaseProfile()
        for _ in range(ticks):
            step_report : StepReport = eng.step()
            metrics.record(step_report = step_report)

        return RunArtifacts(engine_final=eng, 
                            metrics= metrics, 
                            seed= eng.master_ss,
                            phase_profile= phase_profile,
                            
                            )



