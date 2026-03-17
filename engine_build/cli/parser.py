from __future__ import annotations

import argparse

from engine_build.cli.options import (
    REGIME_OPTIONS,
    VALIDATION_SUITES,
    VERIFICATION_SUITES,
)
from engine_build.cli.requests import (
    ExperimentRequest,
    ValidationRequest,
    VerificationRequest,
    FertilityRequest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engine_build.main",
        description="Ecosystem Emergent Behavior Simulator",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -------------------------
    # experiment
    # -------------------------
    experiment = subparsers.add_parser(
        "experiment",
        help="Run the experimental simulation pipeline.",
    )
    experiment.add_argument(
        "--regime",
        required=True,
        choices=REGIME_OPTIONS,
        help="Named regime to run.",
    )
    experiment.add_argument(
        "--runs",
        type=int,
        default=None,
        help="Number of runs. Leave unset to use experiment defaults.",
    )
    experiment.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Number of ticks. Leave unset to use experiment defaults.",
    )
    experiment.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base seed for deterministic execution.",
    )
    experiment.add_argument(
        "--plot",
        action="store_true",
        help="Plot batch results.",
    )
    experiment.add_argument(
        "--plot-dev",
        action="store_true",
        help="Plot development/debug figures.",
    )
    experiment.add_argument(
        "--perf-flag",
        action="store_true",
        help="Enable performance/profiling mode.",
    )

    # -------------------------
    # verify
    # -------------------------
    verify = subparsers.add_parser(
        "verify",
        help="Run verification pytest suites (determinism, invariants, rng, snapshots, regime).",
    )
    verify.add_argument(
        "--suite",
        required=True,
        choices=VERIFICATION_SUITES,
        help="Verification suite to run.",
    )
    verify.add_argument(
        "--verbose",
        action="store_true",
        help="Run pytest with verbose output.",
    )
    verify.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure.",
    )
    verify.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        dest="pytest_args",
        help="Extra raw pytest argument. Repeatable.",
    )

    # -------------------------
    # validate
    # -------------------------
    validate = subparsers.add_parser(
        "validate",
        help="Run validation pytest suites (regime/business validation).",
    )
    validate.add_argument(
        "--suite",
        required=True,
        choices=VALIDATION_SUITES,
        help="Validation suite to run.",
    )
    validate.add_argument(
        "--verbose",
        action="store_true",
        help="Run pytest with verbose output.",
    )
    validate.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure.",
    )
    validate.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        dest="pytest_args",
        help="Extra raw pytest argument. Repeatable.",
    )

    # -------------------------
    # fertility
    # -------------------------
    fertility = subparsers.add_parser(
        "fertility",
        help="Run the fertility/dev plotting workflow.",
    )
    fertility.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed for the fertility/dev flow.",
    )

    return parser


def build_experiment_request(args: argparse.Namespace) -> ExperimentRequest:
    return ExperimentRequest(
        regime=args.regime,
        seed=args.seed,
        runs=args.runs,
        ticks=args.ticks,
        plot=args.plot,
        plot_dev=args.plot_dev,
        perf_flag=args.perf_flag,
    )


def build_verification_request(args: argparse.Namespace) -> VerificationRequest:
    return VerificationRequest(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=tuple(args.pytest_args),
    )


def build_validation_request(args: argparse.Namespace) -> ValidationRequest:
    return ValidationRequest(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=tuple(args.pytest_args),
    )


def build_fertility_request(args: argparse.Namespace) -> FertilityRequest:
    return FertilityRequest(
        seed=args.seed,
    )