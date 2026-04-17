"""Coordinate end-to-end execution for app-level service requests.

This module owns high-level execution flow across workflow compilation,
runner execution, processing, and presentation. It does not parse CLI
inputs or implement mode-specific request validation.
"""




from dataclasses import dataclass

from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.app.execution.presenters.presentation_router import present_output
from FestinaLente.app.execution.workflows.compile_workflow import BatchPlan, CompiledWorkflowPlan, PresentationPlan, ProcessingPlan
from FestinaLente.app.execution.workflows.processing_workflow import process_workflow
from FestinaLente.app.execution.workflows.runner_workflow import Execute_workflow
from FestinaLente.app.service_models.modes import ExecutionMode
from FestinaLente.app.service_models.service_request_container import ServiceRequest
from FestinaLente.runner.utils.results import BatchRunResults

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
    service_type: ExecutionMode = service_request.service_request_meta.mode

    if service_type is ExecutionMode.EXPERIMENT:
        return experiment_service_call(service_request)
    if service_type is ExecutionMode.EXPLORATION:
        return exploration_service_call(service_request)

    raise ValueError(f"Execution mode {service_type!r} does not compile a simulation workflow.")





def orchestrate(service_request : ServiceRequest) -> int | OrchestratorResult:
    service_type: ExecutionMode = service_request.service_request_meta.mode

    if service_type is ExecutionMode.VERIFICATION:
        return verification_service_call(service_request)
    if service_type is ExecutionMode.VALIDATION:
        return validation_service_call(service_request)

    workflow_plan : CompiledWorkflowPlan = get_workflow_plan(service_request=service_request)

    running_plan: BatchPlan = workflow_plan.running_plan
    processing_plan: ProcessingPlan =workflow_plan.processing_plan
    presentation_plan: PresentationPlan = workflow_plan.presentation_plan

    executed_workflow : BatchRunResults = Execute_workflow(runner_plan=running_plan)

    processed_workflow : AnalyticsBundle = process_workflow(processing_plan=processing_plan, batch_results=executed_workflow)    

    present_output(presentation_plan, processed_workflow)    

    return 0
