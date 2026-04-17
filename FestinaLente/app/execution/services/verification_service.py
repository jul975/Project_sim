"""Run verification test suites from normalized execution requests.

This module translates verification-mode request fields into pytest arguments
and executes the requested verification suite.
"""

from __future__ import annotations

import pytest

from FestinaLente.app.service_models.service_request_container import ServiceRequest
from FestinaLente.app.service_models.suite_registry import VERIFICATION_SUITES


def verification_service_call(verification_request: ServiceRequest) -> int:
    """Execute a verification suite through pytest.

    Args:
        verification_request: Service request containing the verification suite selection
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
    if verification_request.service_request_meta.suite is None:
        raise ValueError("Verification mode requires a suite.")

    targets = VERIFICATION_SUITES.get(str(verification_request.service_request_meta.suite))
    if targets is None:
        valid = ", ".join(sorted(VERIFICATION_SUITES))
        raise ValueError(f"Unknown verification suite: {verification_request.service_request_meta.suite!r}. Valid suites: {valid}")

    pytest_args: list[str] = []
    if verification_request.processing_request.verbose:
        pytest_args.append("-v")
    if verification_request.processing_request.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(verification_request.processing_request.pytest_args)

    print(f"[verification] Running verification suite: {verification_request.service_request_meta.suite}")
    result = pytest.main(pytest_args)
    return int(result)


if __name__ == "__main__":
    pass
