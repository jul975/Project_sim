from __future__ import annotations

import pytest

from engine_build.cli.requests import ValidationRequest
from engine_build.cli.spec import VALIDATION_SUITES, resolve_validation_suite_name


def run_validation_mode(request: ValidationRequest) -> int:
    suite_name = resolve_validation_suite_name(request.suite)
    targets = VALIDATION_SUITES.get(suite_name)

    if targets is None:
        valid = ", ".join(sorted(VALIDATION_SUITES))
        raise ValueError(
            f"Unknown validation suite: {request.suite!r}. Valid suites: {valid}"
        )

    pytest_args: list[str] = []

    if request.verbose:
        pytest_args.append("-v")

    if request.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(request.pytest_args)

    print(f"[validation] Running validation suite: {suite_name}")
    if request.verbose:
        print(f"[validation] pytest args: {pytest_args}")

    result = pytest.main(pytest_args)
    return int(result)