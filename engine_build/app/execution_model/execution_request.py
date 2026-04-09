from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine_build.app.execution_model.features import ExecutionFeatures
from engine_build.app.execution_model.modes import ExecutionMode


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
class ExecutionRequest:
    """Immutable request describing one app-level execution workflow.

    Built by CLI/menu request builders and consumed by dispatch/services.
    Fields are mode-dependent: experiment/exploration use regime/run controls,
    while verification/validation use suite/pytest controls.
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