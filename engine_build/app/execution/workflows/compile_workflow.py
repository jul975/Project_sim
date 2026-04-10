from __future__ import annotations

from numpy.random import SeedSequence

from engine_build.app.service_models.default import EXPERIMENT_DEFAULTS, DEFAULT_MASTER_SEED, DEFAULT_REGIME_CONFIG
from engine_build.app.service_models.service_request_container import RunnerRequest, ServiceRequest, ServiceRequestMeta

from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec

from dataclasses import dataclass
from engine_build.regimes.compiled import CompiledRegime



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
        ticks: number of ticks
        engine_template: 
        '''
    batch_id: int = DEFAULT_MASTER_SEED
    n_runs: int = 10
    ticks: int = 1000
    engine_template: EngineTemplate


@dataclass
class ProcessingPlan:
    pass


@dataclass
class PresentationPlan:
    pass 


@dataclass
class CompiledWorkflowPlan:
    running_plan : BatchPlan
    processing_plan: ProcessingPlan
    presentation_plan: PresentationPlan 



def _get_engine_template(runner_request : RunnerRequest, service_request_meta : ServiceRequestMeta) -> EngineTemplate: 

    regime_spec = get_regime_spec(service_request_meta.regime)
    regime_config = compile_regime(regime_spec)



    execution_features = service_request_meta.execution_features

    perf_flag = execution_features.perf_profiling
    world_frame = execution_features.capture_world_frames
    change_condition = execution_features.change_condition



    return EngineTemplate(
        regime_config=regime_config, 
        perf_flag=perf_flag, 
        world_frame_flag=world_frame,
        change_condition=change_condition 

    )    





def _get_runner_plan(workflow_request: ServiceRequest):
    """ => single source of truth for runner"""
    runner_request = workflow_request.runner_request
    meta_request = workflow_request.service_request_meta
    engine_template=_get_engine_template(runner_request=runner_request, service_request_meta=meta_request)
    
    ticks = runner_request.ticks if runner_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = runner_request.runs if runner_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    return BatchPlan(
        batch_seed = runner_request.seed,
        n_runs = runs,
        ticks = ticks,
        engine_template=engine_template
        )

def _get_processing_plan(workflow_request: ServiceRequest) -> ProcessingPlan:
    """ => single source of truth for processing"""
    pass

def _get_presentation_plan(workflow_request: ServiceRequest) -> PresentationPlan:
    """ => single source of truth for presentation"""
    pass



def compile_workflow_plans(workflow_request: ServiceRequest) -> CompiledWorkflowPlan:

    

# def sep function for building and retuning batch 

    runner_plan  = _get_runner_plan(workflow_request)
    processing_plan = _get_processing_plan(workflow_request)
    presentation_plan = _get_presentation_plan(workflow_request)

    return CompiledWorkflowPlan(
        running_plan=runner_plan,
        processing_plan=processing_plan,
        presentation_plan=presentation_plan    
    )













