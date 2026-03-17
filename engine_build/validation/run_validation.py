from __future__ import annotations


"""
Instead, engine_build/validation/ should contain library code used by tests and CLI wrappers, for example:

engine_build/validation/
  contracts.py        # thresholds/envelopes for canonical regimes
  assertions.py       # reusable behavioral assertions
  baselines.py        # fixed seed panels / validation defaults
  report.py           # human-readable validation summaries

So the pattern becomes:

engine_build/validation/ = reusable validation machinery

tests/validation/ = pytest pass/fail checks using that machinery











"""














from engine_build.cli.requests import ValidationRequest
from engine_build.validation.suites import (
    run_all_validations,
    run_determinism_validations,
    run_regime_validations,
    run_invariant_validations,
)


def run_validation_mode(request: ValidationRequest) -> int:
    if request.verbose:
        print(f"[validation] suite={request.suite} fail_fast={request.fail_fast}")

    if request.suite == "all":
        success = run_all_validations(
            verbose=request.verbose,
            fail_fast=request.fail_fast,
        )
    elif request.suite == "determinism":
        success = run_determinism_validations(
            verbose=request.verbose,
            fail_fast=request.fail_fast,
        )
    elif request.suite == "regime":
        success = run_regime_validations(
            verbose=request.verbose,
            fail_fast=request.fail_fast,
        )
    elif request.suite == "invariants":
        success = run_invariant_validations(
            verbose=request.verbose,
            fail_fast=request.fail_fast,
        )
    else:
        raise ValueError(f"Unknown validation suite: {request.suite}")

    return 0 if success else 1