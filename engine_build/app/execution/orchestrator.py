"""Coordinate end-to-end execution for app-level service requests.

This module owns high-level execution flow across workflow compilation,
runner execution, processing, and presentation. It does not parse CLI
inputs or implement mode-specific request validation.
"""




from dataclasses import dataclass

from engine_build.app.execution.workflows.compile_workflow import CompiledWorkflowPlan
from engine_build.app.service_models.modes import ExecutionMode
from engine_build.app.service_models.service_request_container import ServiceRequest

from .services import (
    experiment_service_call, 
    verification_service_call , 
    validation_service_call, 
    exploration_service_call
    ) 



@dataclass
class OrchestratorResult:
    pass


def get_workflow_plan(service_request : ServiceRequest) -> CompiledWorkflowPlan:
    # NOTE: need to make validation more explicit
    service_type: ExecutionMode = service_request.service_request_meta.mode

    if service_type is ExecutionMode.EXPERIMENT:
        return experiment_service_call(service_request)
    if service_type is ExecutionMode.VERIFICATION:
        return verification_service_call(service_request)

    if service_type is ExecutionMode.VALIDATION:
        return validation_service_call(service_request)

    if service_type is ExecutionMode.EXPLORATION:
        return exploration_service_call(service_request)

    raise ValueError(f"Unsupported execution mode: {service_type!r}")





def orchestrate(service_request : ServiceRequest) -> int | OrchestratorResult:


    # validate generic app invariants
    # compile plan
    workflow_plan: CompiledWorkflowPlan = get_workflow_plan(service_request=service_request)

    # execute running workflow
    
    # execute processing workflow
    
    # execute presentation workflow
    
    # return exit code or rich result


    return 0