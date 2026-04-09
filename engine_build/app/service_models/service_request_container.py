from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine_build.app.service_models.features import ExecutionFeatures
from engine_build.app.service_models.modes import ExecutionMode


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
class ServiceRequest:
    """Immutable request describing one app-level execution workflow.

    Built by CLI/menu request builders and consumed by dispatch/services.
    The active mode determines which fields are relevant for downstream
    execution.

    Attributes:
        mode: Top-level execution workflow to run.
        regime: Regime identifier for experiment or exploration workflows.
        suite: Verification or validation suite identifier.
        seed: Optional deterministic seed for simulation workflows.
        runs: Optional batch run count for experiment workflows.
        ticks: Optional tick limit for experiment or exploration workflows.
        tail_fraction: Fraction of each run treated as the analysis tail.
        verbose: Enables verbose pytest output for verification/validation.
        fail_fast: Stops pytest after the first failure when enabled.
        pytest_args: Additional pytest arguments forwarded to the test runner.
        features: Optional execution feature flags.

    Notes:
        Experiment/exploration requests use regime/run controls.
        Verification/validation requests use suite/pytest controls.
    """
    mode: ExecutionMode

    # Experiment / exploration selection
    regime: RegimeName | None = None
    suite: VerificationSuite | ValidationSuite | None = None

    # Shared run controls
    seed: int | None = None
    runs: int | None = None
    ticks: int | None = None

    # Experiment analysis controls
    tail_fraction: float = 0.25

    # Verification / validation controls
    verbose: bool = False
    fail_fast: bool = False
    pytest_args: tuple[str, ...] = field(default_factory=tuple)

    # Optional execution features
    features: ExecutionFeatures = field(default_factory=ExecutionFeatures)



if __name__ == "__main__":
    pass
