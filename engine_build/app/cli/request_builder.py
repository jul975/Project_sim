"""Build normalized execution requests from CLI or menu inputs.

This module centralizes app-layer request construction so every entry point
produces the same immutable ``ServiceRequest`` shape before dispatch.
"""

from __future__ import annotations

from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.service_models.modes import ExecutionMode
from engine_build.app.service_models.features import ExecutionFeatures


def build_experiment_request(
    *,
    regime: str,
    seed: int | None = None,
    runs: int | None = None,
    ticks: int | None = None,
    tail_fraction: float = 0.25,
    plot: bool = False,
    plot_dev: bool = False,
    profiling: bool = False,
    capture_world_frames: bool = False,
    animate: bool = False,
) -> ServiceRequest:
    """Build an experiment-mode execution request.

    Args:
        regime: Regime identifier to compile and run.
        seed: Optional deterministic seed for the batch.
        runs: Optional number of runs to execute.
        ticks: Optional tick limit per run.
        tail_fraction: Fraction of each run treated as the analysis tail.
        plot: Enables batch plotting outputs.
        plot_dev: Enables developer-oriented plot outputs.
        profiling: Enables performance profiling features.
        capture_world_frames: Enables world-frame capture for visualization.
        animate: Enables animation-oriented features.

    Returns:
        Immutable service request normalized for experiment dispatch.
    """
    return ServiceRequest(
        mode=ExecutionMode.EXPERIMENT,
        regime=regime,
        seed=seed,
        runs=runs,
        ticks=ticks,
        tail_fraction=tail_fraction,
        features=ExecutionFeatures(
            plotting=plot,
            plot_dev=plot_dev,
            profiling=profiling,
            capture_world_frames=capture_world_frames,
            animate=animate,
        ),
    )


def build_verification_request(
    *,
    suite: str,
    verbose: bool = False,
    fail_fast: bool = False,
    pytest_args: tuple[str, ...] = (),
) -> ServiceRequest:
    """Build a verification-mode execution request.

    Args:
        suite: Verification suite name to run.
        verbose: Enables verbose pytest output.
        fail_fast: Stops pytest after the first failure.
        pytest_args: Extra pytest arguments to forward unchanged.

    Returns:
        Immutable service request normalized for verification dispatch.
    """
    return ServiceRequest(
        mode=ExecutionMode.VERIFICATION,
        suite=suite,
        verbose=verbose,
        fail_fast=fail_fast,
        pytest_args=tuple(pytest_args),
    )


def build_validation_request(
    *,
    suite: str,
    verbose: bool = False,
    fail_fast: bool = False,
    pytest_args: tuple[str, ...] = (),
) -> ServiceRequest:
    """Build a validation-mode execution request.

    Args:
        suite: Validation suite name to run.
        verbose: Enables verbose pytest output.
        fail_fast: Stops pytest after the first failure.
        pytest_args: Extra pytest arguments to forward unchanged.

    Returns:
        Immutable service request normalized for validation dispatch.
    """
    return ServiceRequest(
        mode=ExecutionMode.VALIDATION,
        suite=suite,
        verbose=verbose,
        fail_fast=fail_fast,
        pytest_args=tuple(pytest_args),
    )


def build_exploration_request(
    *,
    regime: str,
    seed: int | None = None,
    ticks: int | None = None,
) -> ServiceRequest:
    """Build an exploration-mode execution request.

    Args:
        regime: Regime identifier to compile and explore.
        seed: Optional deterministic seed for the exploration run.
        ticks: Optional tick limit for the exploration run.

    Returns:
        Immutable service request normalized for exploration dispatch.
    """
    return ServiceRequest(
        mode=ExecutionMode.EXPLORATION,
        regime=regime,
        seed=seed,
        ticks=ticks,
        features=ExecutionFeatures(animate=True),
    )



if __name__ == "__main__":
    pass