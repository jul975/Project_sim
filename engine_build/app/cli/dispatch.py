"""Dispatch normalized execution service_requests to the correct service entry point.

This module is the app-layer routing boundary between service_request construction and
mode-specific execution services.
"""

from __future__ import annotations

from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.service_models.modes import ExecutionMode

from engine_build.app.execution.services.experiment_service import experiment_service_call
from engine_build.app.execution.services.verification_service import verification_service_call
from engine_build.app.execution.services.validation_service import validation_service_call
from engine_build.app.execution.services.exploration_service import exploration_service_call


def dispatch(service_request: ServiceRequest) -> int:
    """Route an execution service_request to the matching service implementation.

    Args:
        service_request: Normalized execution service_request built by the CLI or menu layer.

    Returns:
        Integer process-style exit code returned by the selected service.

    Raises:
        ValueError: If the service_request contains an unsupported execution mode.

    Notes:
        This function only performs mode dispatch. It does not validate CLI
        inputs, build service_requests, or implement workflow logic.
    """
    service_type = service_request.service_request_meta.mode
    if service_type is ExecutionMode.EXPERIMENT:
        return experiment_service_call(service_request)

    if service_type is ExecutionMode.VERIFICATION:
        return verification_service_call(service_request)

    if service_type is ExecutionMode.VALIDATION:
        return validation_service_call(service_request)

    if service_type is ExecutionMode.EXPLORATION:
        return exploration_service_call(service_request)

    raise ValueError(f"Unsupported execution mode: {service_type!r}")



if __name__ == "__main__":
    pass
