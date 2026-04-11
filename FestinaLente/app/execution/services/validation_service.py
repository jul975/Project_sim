"""Run validation test suites from normalized execution requests.

This module resolves validation suite names, builds pytest arguments, and
executes the requested validation suite.
"""

from __future__ import annotations

import pytest

from FestinaLente.app.service_models.service_request_container import ServiceRequest
from FestinaLente.app.service_models.suite_registry import (
    VALIDATION_SUITES,
    resolve_validation_suite_name,
)


def validation_service_call(validation_request: ServiceRequest) -> int:
    """Execute a validation suite through pytest.

    Args:
        validation_request: Service request containing the validation suite selection
            and optional pytest control flags.

    Returns:
        Integer pytest exit code for the executed validation suite.

    Raises:
        ValueError: If validation mode is requested without a suite, or if the
            resolved suite name is not registered.

    Notes:
        Validation suite aliases are normalized before lookup so the service
        can accept the app-layer suite vocabulary consistently.
    """
    if validation_request.suite is None:
        raise ValueError("Validation mode requires a suite.")

    suite_name = resolve_validation_suite_name(str(validation_request.suite))
    targets = VALIDATION_SUITES.get(suite_name)

    if targets is None:
        valid = ", ".join(sorted(VALIDATION_SUITES))
        raise ValueError(f"Unknown validation suite: {validation_request.suite!r}. Valid suites: {valid}")

    pytest_args: list[str] = []
    if validation_request.verbose:
        pytest_args.append("-v")
    if validation_request.fail_fast:
        pytest_args.append("-x")

    pytest_args.extend(targets)
    pytest_args.extend(validation_request.pytest_args)

    print(f"[validation] Running validation suite: {suite_name}")
    result = pytest.main(pytest_args)
    return int(result)



if __name__ == "__main__":
    pass
