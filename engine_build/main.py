


from __future__ import annotations

import argparse
import sys

from engine_build.cli.requests import (
    ExperimentRequest,
    ValidationRequest,
    FertilityRequest,
)
from engine_build.experiments.run_experiment import run_experiment_mode
from engine_build.validation.run_validation import run_validation_mode
from engine_build.experiments.fertility_dist_plot import run_and_plot_population_dynamics


def add_common_experiment_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--regime",
        choices=["fragile", "abundant", "stable", "test_stable"],
        default="stable",
        help="Select ecological regime type",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional master seed override",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        help="Number of runs to execute",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Number of ticks per run",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ecosystem emergent behavior simulator CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Run an experiment batch",
    )
    add_common_experiment_args(experiment_parser)
    experiment_parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot batch population dynamics",
    )
    experiment_parser.add_argument(
        "--plot-dev",
        action="store_true",
        help="Plot verbose development figures",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Run validation workflows",
    )
    validate_parser.add_argument(
        "--suite",
        choices=["all", "determinism", "regime", "invariants"],
        default="all",
        help="Validation suite to run",
    )
    validate_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose validation output",
    )
    validate_parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at the first validation failure",
    )

    fertility_parser = subparsers.add_parser(
        "fertility",
        help="Run fertility/population dynamics demo",
    )
    fertility_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed override",
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
    )


def build_validation_request(args: argparse.Namespace) -> ValidationRequest:
    return ValidationRequest(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
    )


def build_fertility_request(args: argparse.Namespace) -> FertilityRequest:
    return FertilityRequest(
        seed=args.seed,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "experiment":
        request = build_experiment_request(args)
        return run_experiment_mode(request)

    if args.command == "validate":
        request = build_validation_request(args)
        return run_validation_mode(request)

    if args.command == "fertility":
        request = build_fertility_request(args)
        run_and_plot_population_dynamics()
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())