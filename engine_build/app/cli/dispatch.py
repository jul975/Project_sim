

# bridge, maps request to workflow

# NOTE: Dispatch should only route to services, not build requests.

from __future__ import annotations

from engine_build.app.execution_model.execution_request import ExecutionRequest
from engine_build.app.execution_model.modes import ExecutionMode
from engine_build.app.execution.services.experiment_service import run_experiment
from engine_build.app.execution.services.verification_service import run_verification
from engine_build.app.execution.services.validation_service import run_validation
from engine_build.app.execution.services.exploration_service import run_exploration


def dispatch(context: ExecutionRequest) -> int:
    if context.mode is ExecutionMode.EXPERIMENT:
        return run_experiment(context)

    if context.mode is ExecutionMode.VERIFICATION:
        return run_verification(context)

    if context.mode is ExecutionMode.VALIDATION:
        return run_validation(context)

    if context.mode is ExecutionMode.EXPLORATION:
        return run_exploration(context)

    raise ValueError(f"Unsupported execution mode: {context.mode!r}")



if __name__ == "__main__":
    pass