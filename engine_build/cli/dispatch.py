

# bridge, maps request to workflow

from __future__ import annotations

from engine_build.cli.requests import (
    ExperimentRequest,
    VerificationRequest,
    ValidationRequest,
    FertilityRequest,
)
from engine_build.experiments.run_experiment import run_experiment_mode
from engine_build.verification.run_verification import run_verification_mode
from engine_build.validation.run_validation import run_validation_mode
from engine_build.experiments.fertility_dist_plot import run_and_plot_population_dynamics


def dispatch(request) -> int:
    if isinstance(request, ExperimentRequest):
        return run_experiment_mode(request)

    if isinstance(request, VerificationRequest):
        return run_verification_mode(request)

    if isinstance(request, ValidationRequest):
        return run_validation_mode(request)

    if isinstance(request, FertilityRequest):
        # Temporary stub path:
        # the request object exists, but the underlying fertility workflow
        # does not yet consume the seed.
        run_and_plot_population_dynamics()
        return 0

    raise TypeError(f"Unsupported request type: {type(request)!r}")