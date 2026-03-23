from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

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
class ExperimentRequest:
    regime: RegimeName
    seed: int | None = None
    runs: int | None = None
    ticks: int | None = None
    plot: bool = False
    plot_dev: bool = False
    perf_flag: bool = False
    world_frame_flag: bool = False
    tail_fraction: float = 0.25


@dataclass(frozen=True)
class VerificationRequest:
    suite: VerificationSuite
    verbose: bool = False
    fail_fast: bool = False
    pytest_args: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationRequest:
    suite: ValidationSuite
    verbose: bool = False
    fail_fast: bool = False
    pytest_args: tuple[str, ...] = ()


