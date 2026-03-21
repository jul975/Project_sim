from __future__ import annotations

import pytest


def _run_pytest(paths: list[str], verbose: bool, fail_fast: bool) -> bool:
    args: list[str] = paths.copy()

    if verbose:
        args.append("-v")

    if fail_fast:
        args.append("-x")

    exit_code = pytest.main(args)
    return exit_code == 0


def run_all_validations(verbose: bool = False, fail_fast: bool = False) -> bool:
    return _run_pytest(
        paths=["tests/validation"],
        verbose=verbose,
        fail_fast=fail_fast,
    )


def run_regime_validations(verbose: bool = False, fail_fast: bool = False) -> bool:
    return _run_pytest(
        paths=["tests/test_regime_validation.py"],
        verbose=verbose,
        fail_fast=fail_fast,
    )


def run_regime_contracts_validation(verbose: bool = False, fail_fast: bool = False) -> bool:
    return _run_pytest(
        paths=["tests/validation/test_regime_contracts.py"],
        verbose=verbose,
        fail_fast=fail_fast,
    )