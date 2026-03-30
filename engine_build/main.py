from __future__ import annotations

import sys

from engine_build.app.cli.dispatch import dispatch
from engine_build.app.cli.menu import run_menu
from engine_build.app.cli.parser import (
    build_parser,
    build_experiment_context,
    build_verification_context,
    build_validation_context,
    build_exploration_context,
)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] == "menu":
        context = run_menu()
        if context is None:
            return 0
        return dispatch(context)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "experiment":
        context = build_experiment_context(args)
    elif args.command == "verify":
        context = build_verification_context(args)
    elif args.command == "validate":
        context = build_validation_context(args)
    elif args.command == "dynamic":
        context = build_exploration_context(args)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    return dispatch(context)


if __name__ == "__main__":
    raise SystemExit(main())