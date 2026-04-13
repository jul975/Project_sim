"""Compile execution-stage plans from normalized service requests.

This module translates app-layer request models into workflow plans.
It does not execute runners, analytics, or presentation side effects.
"""

from __future__ import annotations



from ...service_models.default import EXPERIMENT_DEFAULTS, DEFAULT_MASTER_SEED, DEFAULT_REGIME_CONFIG
from ...service_models.features import ExecutionFeatures
from ...service_models.service_request_container import RunnerRequest, ServiceRequest, ServiceRequestMeta

from ....regimes.compiler import compile_regime
from ....regimes.registry import get_regime_spec

from dataclasses import dataclass, field
from ....regimes.compiled import CompiledRegime
from ....regimes.spec import RegimeSpec



"""
batch_plan
-> generate run seeds from batch_seed
-> combine each run seed with engine_template
-> produce SingleRunPlan / EngineBuildMap
-> SingleRunner builds and runs the engine
"""


@dataclass(frozen=True)
class EngineTemplate:
    """ Immutable template for engine construction, containing all configuration except the seed. """
    regime_config: CompiledRegime = DEFAULT_REGIME_CONFIG
    perf_flag: bool = False
    world_frame_flag: bool = False
    change_condition: bool = False



@dataclass(frozen=True)
class BatchPlan:
    ''' Plan for executing a batch of runs, containing the batch seed, number of runs, tick count, and engine template.
    Attributes: 
        batch_seed: master seed
        n_runs: number of runs
        engine_template: 
        '''
    engine_template: EngineTemplate

    batch_id: int = DEFAULT_MASTER_SEED
    n_runs: int = 10
    ticks : int = 1000
#######################################################################



@dataclass(frozen=True)
class AnalysisOptions:
    include_perf: bool = False
    include_world_frames: bool = False
    animate_run: bool = False

@dataclass(frozen=True)
class ProcessingPlan:
    """ Analysis context. 
    
    Attributes:
        - n_runs:               Number of runs.
        - total_tics:           Total number of ticks.
        - tail_fraction:        Tail fraction.
        - regime_label:         Regime label.
        - compiled_regime:      Compiled regime.
        - options:              Analysis options.
    """


    n_runs: int | None = None
    total_tics: int | None = None
    tail_fraction: float = 0.25

    regime_label: str | None = None
    compiled_regime: CompiledRegime | None = None

    options: AnalysisOptions = field(default_factory=AnalysisOptions)

    @property
    def tail_start(self, total_tics) -> int:
        return int(total_tics * (1.0 - self.tail_fraction))




#####################################################################




@dataclass
class PresentationPlan:
    pass 


@dataclass
class CompiledWorkflowPlan:
    running_plan : BatchPlan
    processing_plan: ProcessingPlan
    presentation_plan: PresentationPlan 



def _get_engine_template(service_request_meta : ServiceRequestMeta) -> EngineTemplate: 

    regime_spec: RegimeSpec = get_regime_spec(service_request_meta.regime)
    regime_config: CompiledRegime = compile_regime(regime_spec)



    execution_features: ExecutionFeatures = service_request_meta.execution_features

    perf_flag: bool = execution_features.perf_profiling
    world_frame: bool = execution_features.capture_world_frames
    change_condition: bool = execution_features.change_condition



    return EngineTemplate(
        regime_config=regime_config, 
        perf_flag=perf_flag, 
        world_frame_flag=world_frame,
        change_condition=change_condition 

    )    





def _get_runner_plan(workflow_request: ServiceRequest) -> BatchPlan:
    """ => single source of truth for runner"""
    runner_request: RunnerRequest = workflow_request.runner_request
    meta_request: ServiceRequestMeta = workflow_request.service_request_meta
    engine_template: EngineTemplate=_get_engine_template( service_request_meta=meta_request)
    
    ticks: int = runner_request.ticks if runner_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs: int = runner_request.runs if runner_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    return BatchPlan(
        batch_id=runner_request.seed,
        n_runs = runs,
        ticks=ticks,
        engine_template=engine_template
        )

def _get_processing_plan(workflow_request: ServiceRequest, engine_template : EngineTemplate) -> ProcessingPlan:
    """ => single source of truth for processing
    first draft version """
    
    n_runs: int  = workflow_request.runner_request.runs
    tail_fraction : float = workflow_request.processing_request.tail_fraction
    
    # NOTE: placeholder type regime label needs cleanup 
    regime_label: str = workflow_request.service_request_meta.regime
    compiled_regime : CompiledRegime = engine_template.regime_config

    options = AnalysisOptions(
        include_perf=engine_template.perf_flag,
        include_world_frames=engine_template.world_frame_flag
    ) 
    


    return ProcessingPlan(
        n_runs=n_runs,
        tail_fraction=tail_fraction,
        regime_label=regime_label,
        compiled_regime=compiled_regime,
        options=options
    )
















########################################################

def _get_presentation_plan(workflow_request: ServiceRequest) -> PresentationPlan:
    """ => single source of truth for presentation"""
    pass



def compile_workflow_plans(workflow_request: ServiceRequest) -> CompiledWorkflowPlan:

    

# def sep function for building and retuning batch 

    runner_plan: BatchPlan   = _get_runner_plan(workflow_request)
    processing_plan: ProcessingPlan = _get_processing_plan(workflow_request, runner_plan.engine_template)
    presentation_plan: PresentationPlan = _get_presentation_plan(workflow_request)

    return CompiledWorkflowPlan(
        running_plan=runner_plan,
        processing_plan=processing_plan,
        presentation_plan=presentation_plan    
    )













