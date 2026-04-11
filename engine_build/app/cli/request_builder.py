"""Build normalized execution requests from CLI or menu inputs.

This module centralizes app-layer request construction so every entry point
produces the same immutable ``ServiceRequest`` shape before dispatch.
"""

from __future__ import annotations

from engine_build.app.service_models.service_request_container import (
    PresentationRequest, 
    ProcessingRequest, 
    RunnerRequest, 
    ServiceRequest, 
    ServiceRequestMeta
)
from engine_build.app.service_models.modes import ExecutionMode
from engine_build.app.service_models.features import ExecutionFeatures



def _build_runner_request(
    *,
    seed: int | None = None,
    runs: int | None = None,
    ticks: int | None = None,
) -> RunnerRequest:
    """Build the runner controls component of a service request."""
    return RunnerRequest(
        seed=seed,
        runs=runs,
        ticks=ticks,
    )

def _build_processing_request(
    *,
    tail_fraction: float = 0.25,
    verbose: bool = False,
    fail_fast: bool = False,
    pytest_args: tuple[str, ...] = (),
) -> ProcessingRequest:
    """Build the processing controls component of a service request."""
    return ProcessingRequest(
        tail_fraction=tail_fraction,
        verbose=verbose,
        fail_fast=fail_fast,
        pytest_args=pytest_args,
    )

def _build_presentation_request() -> PresentationRequest:
    """Build the presentation controls component of a service request."""
    
    return PresentationRequest()

def _build_experiment_features(
    *,
    plot: bool = False,
    plot_dev: bool = False,
    profiling: bool = False,
    capture_world_frames: bool = False,
    animate: bool = False,
    change_condition: bool = False
) -> ExecutionFeatures:
    """Build the execution features for an experiment request."""
    return ExecutionFeatures(
        plotting=plot,
        plot_dev=plot_dev,
        perf_profiling=profiling,
        capture_world_frames=capture_world_frames,
        animate=animate,
        change_condition=change_condition
    )


def _build_service_request_meta(
    *,
    mode: ExecutionMode,
    regime: str | None = None,
    suite: str | None = None,
    # features flags need cleanup
    features: ExecutionFeatures = ExecutionFeatures(),
) -> ServiceRequestMeta:
    """Build the metadata component of a service request."""
    return ServiceRequestMeta(
        mode=mode,
        regime=regime,
        suite=suite,
        execution_features=features,
    )




# NOTE: can be unified upstream leaving it temp for now



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
    change_conditions: bool = False
) -> ServiceRequest:
    """Build a complete service request for an experiment execution."""
    meta: ServiceRequestMeta = _build_service_request_meta(
        mode=ExecutionMode.EXPLORATION,
        regime=regime,
        features=_build_experiment_features(
            plot=plot,
            plot_dev=plot_dev,
            profiling=profiling,
            capture_world_frames=capture_world_frames,
            animate=animate,
            change_condition=change_conditions
        ),
    )
    runner_req = _build_runner_request(seed=seed, runs=runs, ticks=ticks)
    processing_req = _build_processing_request(tail_fraction=tail_fraction)
    presentation_req = _build_presentation_request()

    return ServiceRequest(
        service_request_meta=meta, 
        runner_request=runner_req, 
        processing_request=processing_req,
        presentation_request=presentation_req
        
    )




def build_verification_request(
    *,
    suite: str,
    verbose: bool = False,
    fail_fast: bool = False,
    pytest_args: tuple[str, ...] = (),
) -> ServiceRequest:
    """Build a complete service request for a verification execution."""
    meta = _build_service_request_meta(
        mode=ExecutionMode.VERIFICATION,
        suite=suite,
    )
    processing_req = _build_processing_request(
        verbose=verbose,
        fail_fast=fail_fast,
        pytest_args=pytest_args,
    )
    presentation_req = _build_presentation_request()

    return ServiceRequest(
        **meta.__dict__,
        **processing_req.__dict__,
        **presentation_req.__dict__,
    )


def build_validation_request(
    *,
    suite: str,
    verbose: bool = False,
    fail_fast: bool = False,
    pytest_args: tuple[str, ...] = (),
) -> ServiceRequest:
    """Build a complete service request for a validation execution."""
    meta = _build_service_request_meta(
        mode=ExecutionMode.VALIDATION,
        suite=suite,
    )
    processing_req = _build_processing_request(
        verbose=verbose,
        fail_fast=fail_fast,
        pytest_args=pytest_args,
    )
    presentation_req = _build_presentation_request()

    return ServiceRequest(
        **meta.__dict__,
        **processing_req.__dict__,
        **presentation_req.__dict__,
    )

def build_exploration_request(
    *,
    regime: str,
    seed: int | None = None,
    ticks: int | None = None,
) -> ServiceRequest:
    """Build an exploration-mode execution request."""
    meta = _build_service_request_meta(
        mode=ExecutionMode.EXPLORATION,
        regime=regime,
        features=ExecutionFeatures(animate=True),
    )
    runner_req = _build_runner_request(seed=seed, ticks=ticks)
    processing_req = _build_processing_request()
    presentation_req = _build_presentation_request()

    return ServiceRequest(
        **meta.__dict__,
        **runner_req.__dict__,
        **processing_req.__dict__,
        **presentation_req.__dict__,
    )


if __name__ == "__main__":
    pass