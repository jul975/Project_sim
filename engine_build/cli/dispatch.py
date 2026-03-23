

# bridge, maps request to workflow

from __future__ import annotations

from engine_build.cli.requests import (
    ExperimentRequest,
    VerificationRequest,
    ValidationRequest,
)
from engine_build.experiments.run_experiment import run_experiment_mode
from engine_build.verification.run_verification import run_verification_mode
from engine_build.validation.run_validation import run_validation_mode


def dispatch(request) -> int:
    if isinstance(request, ExperimentRequest):
        return run_experiment_mode(request)

    if isinstance(request, VerificationRequest):
        return run_verification_mode(request)

    if isinstance(request, ValidationRequest):
        return run_validation_mode(request)


    raise TypeError(f"Unsupported request type: {type(request)!r}")