from __future__ import annotations

from engine_build.app.execution_model.execution_request import ExecutionRequest
from engine_build.app.execution_model.modes import ExecutionMode
from engine_build.app.execution.services.experiment_service import run_experiment
from engine_build.app.execution.services.verification_service import run_verification
from engine_build.app.execution.services.validation_service import run_validation
from engine_build.app.execution.services.exploration_service import run_exploration


def dispatch(request: ExecutionRequest) -> int:
    if request.mode is ExecutionMode.EXPERIMENT:
        return run_experiment(request)

    if request.mode is ExecutionMode.VERIFICATION:
        return run_verification(request)

    if request.mode is ExecutionMode.VALIDATION:
        return run_validation(request)

    if request.mode is ExecutionMode.EXPLORATION:
        return run_exploration(request)

    raise ValueError(f"Unsupported execution mode: {request.mode!r}")



if __name__ == "__main__":
    pass