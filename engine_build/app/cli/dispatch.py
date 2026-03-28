

# bridge, maps request to workflow

from __future__ import annotations

from engine_build.cli.requests import (
    ExperimentRequest,
    VerificationRequest,
    ValidationRequest,
    DynamicRunRequest,
)
from engine_build.app.services.experiment_service import run_experiment_mode
from engine_build.verification.run_verification import run_verification_mode
from engine_build.validation.run_validation import run_validation_mode
from engine_build.run_dynamicaly.run_dynamic_single import run_dynamic_mode


def dispatch(request) -> int:
    if isinstance(request, ExperimentRequest):
        return run_experiment_mode(request)

    if isinstance(request, VerificationRequest):
        return run_verification_mode(request)

    if isinstance(request, ValidationRequest):
        return run_validation_mode(request)
    
    if isinstance(request, DynamicRunRequest):
        return run_dynamic_mode(request)


    raise TypeError(f"Unsupported request type: {type(request)!r}")