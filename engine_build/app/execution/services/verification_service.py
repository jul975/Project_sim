from __future__ import annotations

import pytest

from engine_build.app.execution_model.execution_request import ExecutionRequest
from engine_build.app.execution_model.suite_registry import VERIFICATION_SUITES


def run_verification(context: ExecutionRequest) -> int:
    if context.suite is None:
        raise ValueError("Verification mode requires a suite.")

    targets = VERIFICATION_SUITES.get(str(context.suite))
    if targets is None:
        valid = ", ".join(sorted(VERIFICATION_SUITES))
        raise ValueError(f"Unknown verification suite: {context.suite!r}. Valid suites: {valid}")

    pytest_args: list[str] = []
    if context.verbose:
        pytest_args.append("-v")
    if context.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(context.pytest_args)

    print(f"[verification] Running verification suite: {context.suite}")
    result = pytest.main(pytest_args)
    return int(result)


if __name__ == "__main__":
    pass