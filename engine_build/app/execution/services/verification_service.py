"""Run verification test suites from normalized execution requests.

This module translates verification-mode request fields into pytest arguments
and executes the requested verification suite.
"""

from __future__ import annotations

import pytest

from engine_build.app.service_models.service_request_container import ExecutionRequest
from engine_build.app.service_models.suite_registry import VERIFICATION_SUITES


def verification_service_call(context: ExecutionRequest) -> int:
    """Execute a verification suite through pytest.

    Args:
        context: Execution request containing the verification suite selection
            and optional pytest control flags.

    Returns:
        Integer pytest exit code for the executed verification suite.

    Raises:
        ValueError: If verification mode is requested without a suite, or if
            the requested suite name is not registered.

    Notes:
        The service appends suite targets first and then forwards any extra
        ``pytest_args`` from the request unchanged.
    """
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
