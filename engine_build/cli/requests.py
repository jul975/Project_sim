from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RegimeName = Literal["extinction", "stable", "saturated"]
ValidationSuite = Literal["all", "determinism", "regime", "invariants"]


@dataclass(frozen=True)
class ExperimentRequest:
    regime: RegimeName
    seed: int | None = None
    runs: int | None = None
    ticks: int | None = None
    plot: bool = False
    plot_dev: bool = False


@dataclass(frozen=True)
class ValidationRequest:
    suite: ValidationSuite = "all"
    verbose: bool = False
    fail_fast: bool = False


@dataclass(frozen=True)
class FertilityRequest:
    seed: int | None = None