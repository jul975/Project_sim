
from __future__ import annotations

from engine_build.app.execution_model.suite_registry import (
    REGIME_OPTIONS,
    VERIFICATION_SUITES,
    VALIDATION_SUITES,
)
import argparse


# NOTE: Parser should only build ExecutionRequest objects, not dispatch directly.





def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engine_build",
        description="Ecosystem Emergent Behavior Simulator",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # experiment
    experiment = subparsers.add_parser("experiment", help="Run batch experiment")
    experiment.add_argument("--regime", choices=REGIME_OPTIONS, required=True)
    experiment.add_argument("--runs", type=int)
    experiment.add_argument("--ticks", type=int)
    experiment.add_argument("--seed", type=int)
    experiment.add_argument("--plot", action="store_true")
    experiment.add_argument("--plot-dev", action="store_true", dest="plot_dev")
    experiment.add_argument("--perf-flag", action="store_true", dest="perf_flag")
    experiment.add_argument(
        "--world-frame-flag",
        action="store_true",
        dest="world_frame_flag",
    )
    experiment.add_argument("--tail-fraction", type=float, default=0.25),
    experiment.add_argument("--animate", action="store_true")

    # verify
    verify = subparsers.add_parser("verify", help="Run verification suite")
    verify.add_argument("--suite", choices=tuple(VERIFICATION_SUITES.keys()), default="all")
    verify.add_argument("--verbose", action="store_true")
    verify.add_argument("--fail-fast", action="store_true", dest="fail_fast")
    verify.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        dest="pytest_args",
        help="Extra pytest argument; may be repeated",
    )

    # validate
    validate = subparsers.add_parser("validate", help="Run validation suite")
    validate.add_argument("--suite", choices=tuple(VALIDATION_SUITES.keys()), default="all")
    validate.add_argument("--verbose", action="store_true")
    validate.add_argument("--fail-fast", action="store_true", dest="fail_fast")
    validate.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        dest="pytest_args",
        help="Extra pytest argument; may be repeated",
    )

    # dynamic / exploration
    dynamic = subparsers.add_parser("dynamic", help="Run exploration / animated simulation")
    dynamic.add_argument("--regime", choices=REGIME_OPTIONS, required=True)
    dynamic.add_argument("--seed", type=int)
    dynamic.add_argument("--ticks", type=int)

    return parser



if __name__ == "__main__":
    pass