from __future__ import annotations

from engine_build.app.execution_model.execution_request import ExecutionRequest
from engine_build.app.execution_model.modes import ExecutionMode
from engine_build.app.execution_model.features import ExecutionFeatures


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
) -> ExecutionRequest:
    return ExecutionRequest(
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
) -> ExecutionRequest:
    return ExecutionRequest(
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
) -> ExecutionRequest:
    return ExecutionRequest(
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
) -> ExecutionRequest:
    return ExecutionRequest(
        mode=ExecutionMode.EXPLORATION,
        regime=regime,
        seed=seed,
        ticks=ticks,
        features=ExecutionFeatures(animate=True),
    )