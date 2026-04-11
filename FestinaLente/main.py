from __future__ import annotations

import sys

from FestinaLente.app.cli.dispatch import dispatch
from FestinaLente.app.cli.menu import run_menu
from FestinaLente.app.cli.parser import build_parser
from FestinaLente.app.cli.request_builder import (
    build_experiment_request,
    build_verification_request,
    build_validation_request,
    build_exploration_request,
)




def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] == "menu":
        request = run_menu()
        if request is None:
            return 0
        return dispatch(request)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "experiment":
        request = build_experiment_request(
            regime=args.regime,
            seed=args.seed,
            runs=args.runs,
            ticks=args.ticks,
            tail_fraction=args.tail_fraction,
            plot=args.plot,
            plot_dev=args.plot_dev,
            profiling=args.profiling,
            capture_world_frames=args.capture_world_frames,
            animate=args.animate,
        )
    elif args.command == "verify":
        request = build_verification_request(
            suite=args.suite,
            verbose=args.verbose,
            fail_fast=args.fail_fast,
            pytest_args=args.pytest_args,
        )
    elif args.command == "validate":
        request = build_validation_request(
            suite=args.suite,
            verbose=args.verbose,
            fail_fast=args.fail_fast,
            pytest_args=args.pytest_args,
        )
    elif args.command == "dynamic":
        request = build_exploration_request(
            regime=args.regime,
            seed=args.seed,
            ticks=args.ticks,
        )
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    return dispatch(request)


if __name__ == "__main__":
    raise SystemExit(main())