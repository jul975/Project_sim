from __future__ import annotations

import pytest

from engine_build.cli.requests import VerificationRequest
from engine_build.cli.spec import VERIFICATION_SUITES


def run_verification_mode(request: VerificationRequest) -> int:
    targets = VERIFICATION_SUITES.get(request.suite)
    if targets is None:
        valid = ", ".join(sorted(VERIFICATION_SUITES))
        raise ValueError(
            f"Unknown verification suite: {request.suite!r}. Valid suites: {valid}"
        )

    pytest_args: list[str] = []

    if request.verbose:
        pytest_args.append("-v")

    if request.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(request.pytest_args)

    print(f"[verification] Running verification suite: {request.suite}")
    if request.verbose:
        print(f"[verification] pytest args: {pytest_args}")

    result = pytest.main(pytest_args)
    return int(result)