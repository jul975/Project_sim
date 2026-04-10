

from archive.LEGACY_FILES.legacy_seed_logic.leagacy_engine_repro import Engine
from engine_build.analytics.observation.simulation_metrics import SimulationMetrics
from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.service_models.default import EXPERIMENT_DEFAULTS
from engine_build.core.contracts.step_results import StepReport
from engine_build.runner.factories import engine_factory
from engine_build.runner.results import RunArtifacts

import numpy as np

# NOTE: draft of separated runner



class SingleRunner:
    def __init__(self, compiled_workflow):
        self.compiled_workflow = compiled_workflow

        self.engine = engine_factory(compiled_workflow.runner_workflow.regime_config)

        self.metrics = SimulationMetrics(self.engine.max_agent_count)

    def run(self, ticks: int):
        """ => single source of truth for runner"""
        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report=step_report)
        return RunArtifacts(
            engine_final=self.engine,
            metrics=self.metrics,
            seed=self.engine.master_ss,
            phase_profile=None, # NOTE: add phase profile to single runner if needed
        )
    
    def continue_run(self, eng : Engine, metrics : SimulationMetrics, ticks : np.int64) -> RunArtifacts:
        """Continue an existing run using a live engine and metrics buffer."""
        for _ in range(ticks):
            step_report : StepReport = eng.step()
            metrics.record(step_report = step_report)

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



