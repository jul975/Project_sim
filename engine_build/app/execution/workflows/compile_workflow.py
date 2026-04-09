from __future__ import annotations

from dataclasses import dataclass


from engine_build.app.service_models.default import EXPERIMENT_DEFAULTS
from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.spec import RegimeSpec




@dataclass
class RunnerWorkflow:
    regime_spec: RegimeSpec
    regime_config: CompiledRegime
    ticks: int
    runs: int


@dataclass
class ProcessingWorkflow:
    pass


@dataclass
class PresentationWorkflow:
    pass 


@dataclass
class CompiledWorkflow:
    runner_workflow: RunnerWorkflow
    processing_workflow: ProcessingWorkflow
    presentation_workflow: PresentationWorkflow 


def _get_runner_workflow(workflow_request: ServiceRequest) -> RunnerWorkflow:
    """ => single source of truth for runner"""
    regime_spec = get_regime_spec(workflow_request.regime)
    regime_config = compile_regime(regime_spec)

    ticks = workflow_request.ticks if workflow_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = workflow_request.runs if workflow_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    return RunnerWorkflow(
        regime_spec=regime_spec,
        regime_config=regime_config,
        ticks=ticks,
        runs=runs
    )

def _get_processing_workflow(workflow_request: ServiceRequest) -> ProcessingWorkflow:
    """ => single source of truth for processing"""
    pass

def _get_presentation_workflow(workflow_request: ServiceRequest) -> PresentationWorkflow:
    """ => single source of truth for presentation"""
    pass



def compile_workflow(workflow_request: ServiceRequest) -> CompiledWorkflow:
    

# def sep function for building and retuning batch 

    runner_workflow  = _get_runner_workflow(workflow_request)
    processing_workflow = _get_processing_workflow(workflow_request)
    presentation_workflow = _get_presentation_workflow(workflow_request)

    return CompiledWorkflow(
        runner_workflow=runner_workflow,
        processing_workflow=processing_workflow,
        presentation_workflow=presentation_workflow,
    )