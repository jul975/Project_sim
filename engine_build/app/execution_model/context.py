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
class ExecutionContext:
    mode: ExecutionMode

    regime: RegimeName | None = None
    suite: VerificationSuite | ValidationSuite | None = None

    seed: int | None = None
    runs: int | None = None
    ticks: int | None = None

    tail_fraction: float = 0.25

    verbose: bool = False
    fail_fast: bool = False
    pytest_args: tuple[str, ...] = field(default_factory=tuple)

    features: ExecutionFeatures = field(default_factory=ExecutionFeatures)



if __name__ == "__main__":
    pass