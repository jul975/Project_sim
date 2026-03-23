


'''
FRONT ENDS
├─ CLI args
└─ terminal menu

both produce
      ↓
typed request objects
      ↓
dispatcher
      ↓
EXECUTION LANES
├─ simulation lane
│   regime -> compile -> runner -> engine -> analytics -> report
└─ test lane
    pytest suite -> pass/fail -> report


That is the key simplification:

    Menu and CLI are just input methods
    Runner is only for simulation execution
    Pytest suite execution is a separate lane
    Both lanes are reached through the same dispatcher



'''
from __future__ import annotations

import sys

from engine_build.cli.dispatch import dispatch
from engine_build.cli.menu import run_menu
from engine_build.cli.parser import (
    build_parser,
    build_experiment_request,
    build_verification_request,
    build_validation_request,
)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    # Keep the interactive menu explicit.
    # CLI remains the canonical anchor path.
    if argv and argv[0] == "menu":
        request = run_menu()
        if request is None:
            return 0
        return dispatch(request)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "experiment":
        request = build_experiment_request(args)
    elif args.command == "verify":
        request = build_verification_request(args)
    elif args.command == "validate":
        request = build_validation_request(args)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    return dispatch(request)


if __name__ == "__main__":
    raise SystemExit(main())