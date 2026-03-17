from __future__ import annotations

from pathlib import Path

import pytest

from engine_build.cli.requests import VerificationRequest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VERIFICATION_SUITE_TARGETS: dict[str, list[str]] = {
    "all": [str(PROJECT_ROOT / "tests" / "verification")],
    "determinism": [str(PROJECT_ROOT / "tests" / "verification" /"test_determinism.py")],
    "invariants": [str(PROJECT_ROOT / "tests" / "verification" / "test_invariants.py")],
    "rng": [str(PROJECT_ROOT / "tests" / "verification" / "test_rng_isolation.py")],
    "snapshots": [str(PROJECT_ROOT / "tests" / "verification" / "test_snapshots.py")]
}


def run_verification_mode(request: VerificationRequest) -> int:
    targets = VERIFICATION_SUITE_TARGETS.get(request.suite)
    if targets is None:
        valid = ", ".join(sorted(VERIFICATION_SUITE_TARGETS))
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