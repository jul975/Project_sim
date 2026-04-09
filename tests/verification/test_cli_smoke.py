from __future__ import annotations

import subprocess
import sys

from engine_build.app.cli.parser import build_parser
from engine_build.app.cli.request_builder import (
    build_experiment_request,
    build_verification_request,
    build_validation_request,
)
from engine_build.app.cli.menu import run_menu
from engine_build.app.execution_model.execution_request import (
    ExecutionRequest
    )
from engine_build.app.execution_model.modes import ExecutionMode

from engine_build.app.execution_model.suite_registry import (
    REGIME_OPTIONS,
    VERIFICATION_SUITES,
    VALIDATION_SUITES,
)


def _get_subparser(parser, name: str):
    subparsers_action = next(
        action for action in parser._actions if action.dest == "command"
    )
    return subparsers_action.choices[name]


def _get_suite_choices(subparser) -> tuple[str, ...]:
    suite_action = next(action for action in subparser._actions if action.dest == "suite")
    return tuple(suite_action.choices)


def test_cli_smoke_experiment_request_build():
    parser = build_parser()
    args = parser.parse_args(["experiment", "--regime", "stable"])

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

    assert isinstance(request, ExecutionRequest)
    assert request.regime == "stable"
    assert request.runs is None
    assert request.ticks is None
    assert request.seed is None
    assert request.features.plotting is False
    assert request.features.plot_dev is False
    assert request.features.profiling is False
    assert request.features.capture_world_frames is False
    assert request.tail_fraction == 0.25

def test_cli_smoke_experiment_tail_fraction_parser_plumbing():
    parser = build_parser()
    args = parser.parse_args(
        ["experiment", "--regime", "stable", "--tail-fraction", "0.5"]
    )

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

    assert isinstance(request, ExecutionRequest)
    assert request.mode is ExecutionMode.EXPERIMENT
    assert request.regime == "stable"
    assert request.runs is None
    assert request.ticks is None
    assert request.seed is None
    assert request.features.plotting is False
    assert request.features.plot_dev is False
    assert request.features.profiling is False
    assert request.features.capture_world_frames is False
    assert request.tail_fraction == 0.5


def test_cli_smoke_experiment_tail_fraction_menu_plumbing(monkeypatch):
    answers = iter(
        [
            "1",
            "1",
            "",
            "",
            "",
            "n",
            "n",
            "n",
            "n",
            "0.5",
            "y",
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    context = run_menu()

    assert isinstance(context, ExecutionRequest)
    assert context.mode is ExecutionMode.EXPERIMENT
    assert context.regime == "stable"
    assert context.runs is None
    assert context.ticks is None
    assert context.seed is None
    assert context.features.plotting is False
    assert context.features.plot_dev is False
    assert context.features.profiling is False
    assert context.features.capture_world_frames is False
    assert context.tail_fraction == 0.5


def test_cli_smoke_verify_request_build():
    parser = build_parser()
    args = parser.parse_args(["verify", "--suite", "determinism"])

    request = build_verification_request(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=args.pytest_args,
    )

    assert isinstance(request, ExecutionRequest)
    assert request.suite == "determinism"
    assert request.verbose is False
    assert request.fail_fast is False
    assert request.pytest_args == ()


def test_cli_smoke_validate_request_build():
    parser = build_parser()
    args = parser.parse_args(["validate", "--suite", "contracts"])

    request = build_validation_request(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=args.pytest_args,
    )

    assert isinstance(request, ExecutionRequest)
    assert request.suite == "contracts"
    assert request.verbose is False
    assert request.fail_fast is False
    assert request.pytest_args == ()


def test_cli_smoke_experiment_regime_choices_match_spec():
    parser = build_parser()
    experiment_parser = _get_subparser(parser, "experiment")
    regime_action = next(action for action in experiment_parser._actions if action.dest == "regime")

    assert tuple(regime_action.choices) == REGIME_OPTIONS


def test_cli_smoke_verify_suite_choices_match_spec():
    parser = build_parser()
    verify_parser = _get_subparser(parser, "verify")

    assert _get_suite_choices(verify_parser) == tuple(VERIFICATION_SUITES.keys())


def test_cli_smoke_validate_suite_choices_match_spec():
    parser = build_parser()
    validate_parser = _get_subparser(parser, "validate")

    assert _get_suite_choices(validate_parser) == tuple(VALIDATION_SUITES.keys())


def test_cli_smoke_help_runs():
    result = subprocess.run(
        [sys.executable, "-m", "engine_build.main", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "experiment" in result.stdout
    assert "verify" in result.stdout
    assert "validate" in result.stdout


def test_cli_smoke_verify_determinism_runs():
    result = subprocess.run(
        [sys.executable, "-m", "engine_build.main", "verify", "--suite", "determinism"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "[verification] Running verification suite: determinism" in result.stdout
