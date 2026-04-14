
from numpy.random import SeedSequence

from FestinaLente.analytics.observation.simulation_metrics import SimulationMetrics

from FestinaLente.app.execution.workflows.compile_workflow import EngineTemplate
from FestinaLente.core.contracts.step_results import StepReport

from .utils.results import PhaseProfile, RunArtifacts
from .utils.factories import EngineBuildMap
from ..core.engine import Engine



class SingleRunner:
    def __init__(self, engine_build_map : EngineBuildMap) -> None:
        engine_template: EngineTemplate = engine_build_map.engine_template
        self.run_seed: SeedSequence = engine_build_map.run_seed
        
        self.perf_flag : bool = engine_template.perf_flag
        self.world_frame : bool = engine_template.world_frame_flag
        self.change_condition : bool = engine_template.change_condition
        

        self.engine = Engine(engine_template, self.run_seed , self.perf_flag, self.world_frame)

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
        phase_profile = PhaseProfile()

        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report=step_report)
            phase_profile.add_perf_to_profile(step_report=step_report)

        return RunArtifacts(
            engine_final=self.engine,
            metrics=self.metrics,
            seed=self.engine.master_ss,
            phase_profile=phase_profile
        )
    
    

    def run(self, ticks: int) -> RunArtifacts:
        """ => single source of truth for runner"""
        if self.perf_flag:
            return self._run_perf_profiling(ticks)
        return self._run_quick(ticks)
            
    



    def continue_run(self, ticks : int) -> RunArtifacts:
        """Continue an existing run using a live engine and metrics buffer."""
        for _ in range(ticks):
            step_report : StepReport = self.engine.step()
            self.metrics.record(step_report = step_report)

        return RunArtifacts(engine_final=self.engine, 
                            metrics= self.metrics, 
                            seed= self.engine.master_ss,
                            phase_profile= None, # NOTE: add phase profile to single runner if needed
                            )
   
