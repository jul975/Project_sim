from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED
from FestinaLente.app.service_models.features import ExecutionFeatures
from FestinaLente.app.service_models.modes import ExecutionMode


RegimeName = Literal[
    "stable",
    "fragile",
    "abundant",
    "saturated",
    "collapse",
    "extinction",
]

VerificationSuite = Literal[
    "all",
    "determinism",
    "invariants",
    "rng",
    "snapshots",
]

ValidationSuite = Literal[
    "all",
    "contracts",
    "separation",
]

@dataclass(frozen=True)
class ServiceRequestMeta:
    '''Metadata describing the execution workflow to run and its parameters.'''
    mode: ExecutionMode 
    regime : RegimeName | None = None 
    suite : VerificationSuite | ValidationSuite | None = None

    # Optional execution controls
    execution_features: ExecutionFeatures = field(default_factory=ExecutionFeatures)


@dataclass(frozen=True)
class RunnerRequest:
    ''' Shared run controls for experiment/exploration workflows. '''
    seed: int = DEFAULT_MASTER_SEED
    runs: int = 10
    ticks: int = 1000

@dataclass(frozen=True)
class ProcessingRequest:
    ''' Placeholder for processing-specific request parameters. '''
    tail_fraction: float = 0.25

    # Verification / validation controls
    verbose: bool = False
    fail_fast: bool = False
    pytest_args: tuple[str, ...] = field(default_factory=tuple)    

@dataclass(frozen=True)
class PresentationRequest:
    """Placeholder for presentation-specific request parameters. now inside execution features, but may need to be expanded for more complex presentation controls."""
    pass


@dataclass(frozen=True)
class ServiceRequest:
    """Immutable request describing one app-level execution workflow.

    Built by CLI/menu request builders and consumed by dispatch/services.
    The active mode determines which fields are relevant for downstream
    execution.

    Attributes:
        meta: Metadata describing the execution workflow to run and its parameters.
        runner_request: Shared run controls for experiment/exploration workflows.
        processing_request: Placeholder for processing-specific request parameters.
        presentation_request: Placeholder for presentation-specific request parameters.

    Notes:
        Experiment/exploration requests use regime/run controls.
        Verification/validation requests use suite/pytest controls.
    """
    service_request_meta: ServiceRequestMeta
    runner_request: RunnerRequest = field(default_factory=RunnerRequest)
    processing_request: ProcessingRequest = field(default_factory=ProcessingRequest)


    presentation_request: PresentationRequest = field(default_factory=PresentationRequest)

    


if __name__ == "__main__":
    pass
