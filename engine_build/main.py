
import sys

from engine_build.cli.menu import run_menu
from engine_build.cli.parser import build_parser
from engine_build.cli.dispatch import dispatch

from engine_build.cli.parser import build_parser
from engine_build.cli.menu import run_menu
from engine_build.cli.menu import _build_experiment_request, _build_validation_request, _build_fertility_request




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



def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] == "menu":
        request = run_menu()
        if request is None:
            return 0
        return dispatch(request)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "experiment":
        return dispatch(_build_experiment_request(args))
    if args.command == "validate":
        return dispatch(_build_validation_request(args))
    if args.command == "fertility":
        return dispatch(_build_fertility_request(args))

    parser.error(f"Unknown command: {args.command}")
    return 2