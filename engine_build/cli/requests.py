from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RegimeName = Literal["stable", "fragile", "abundant", "saturated", "collapse", "extinction"]
VerificationSuite = Literal["all", "determinism", "regime", "invariants", "rng", "snapshots", ]
ValidationSuite = Literal["test_regime_contracts", "test_regime_separation"]

@dataclass(frozen=True)
class ExperimentRequest:
    regime: RegimeName
    seed: int | None = None
    runs: int | None = None
    ticks: int | None = None
    plot: bool = False
    plot_dev: bool = False
    perf_flag: bool = False



@dataclass(frozen=True)
class VerificationRequest:
    suite: Literal[
        "all",
        "determinism",
        "invariants",
        "rng",
        "snapshots",
        "regime",
    ]
    verbose: bool = True
    fail_fast: bool = True
    pytest_args: tuple[str, ...] = ()

@dataclass(frozen=True)
class ValidationRequest:
    suite: Literal[
        "test_regime_contracts",
        "test_regime_separation",
    ]
    verbose: bool = True    
    fail_fast: bool = True
    pytest_args: tuple[str, ...] = ()



@dataclass(frozen=True)
class FertilityRequest:
    seed: int | None = None