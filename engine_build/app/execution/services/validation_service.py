from __future__ import annotations

import pytest

from engine_build.app.execution_model.context import ExecutionContext
from engine_build.app.execution_model.suite_registry import (
    VALIDATION_SUITES,
    resolve_validation_suite_name,
)


def run_validation(context: ExecutionContext) -> int:
    if context.suite is None:
        raise ValueError("Validation mode requires a suite.")

    suite_name = resolve_validation_suite_name(str(context.suite))
    targets = VALIDATION_SUITES.get(suite_name)

    if targets is None:
        valid = ", ".join(sorted(VALIDATION_SUITES))
        raise ValueError(f"Unknown validation suite: {context.suite!r}. Valid suites: {valid}")

    pytest_args: list[str] = []
    if context.verbose:
        pytest_args.append("-v")
    if context.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(context.pytest_args)

    print(f"[validation] Running validation suite: {suite_name}")
    result = pytest.main(pytest_args)
    return int(result)



if __name__ == "__main__":
    pass