from __future__ import annotations

import argparse

from engine_build.cli.spec import (
    REGIME_OPTIONS,
    validation_suite_choices,
    verification_suite_choices,
)
from engine_build.cli.requests import (
    ExperimentRequest,
    ValidationRequest,
    VerificationRequest
)

# NOTE:
# fertility/dev plotting remains intentionally off the public parser surface.
# Keep the request builder for compatibility with legacy imports from main.py.


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
    experiment.add_argument(
        "--world-frame-flag",
        action="store_true",
        help="Enable world frame capture.",
    )
    experiment.add_argument(
        "--tail-fraction",
        type=float,
        default=0.25,
        help="Fraction of tail to use for analysis.",
    )

    # -------------------------
    # verify
    # -------------------------
    verify = subparsers.add_parser(
        "verify",
        help="Run verification pytest suites.",
    )
    verify.add_argument(
        "--suite",
        required=True,
        choices=verification_suite_choices(),
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
        help="Run validation pytest suites.",
    )
    validate.add_argument(
        "--suite",
        required=True,
        choices=validation_suite_choices(),
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
        world_frame_flag=args.world_frame_flag,
        tail_fraction=args.tail_fraction,
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


# Compatibility stub for main.py import.
# Not wired into the public parser surface anymore.
def build_fertility_request(args: argparse.Namespace) -> FertilityRequest:
    return FertilityRequest(seed=getattr(args, "seed", None))