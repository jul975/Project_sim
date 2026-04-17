from __future__ import annotations

import subprocess
import sys

from FestinaLente.app.cli.parser import build_parser
from FestinaLente.app.cli.request_builder import (
    build_experiment_request,
    build_verification_request,
    build_validation_request,
)
from FestinaLente.app.cli.menu import run_menu
from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, EXPERIMENT_DEFAULTS
from FestinaLente.app.service_models.service_request_container import (
    ServiceRequest
)
from FestinaLente.app.service_models.modes import ExecutionMode

from FestinaLente.app.service_models.suite_registry import (
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


def _assert_default_experiment_request(request: ServiceRequest, *, tail_fraction: float) -> None:
    assert request.service_request_meta.mode is ExecutionMode.EXPERIMENT
    assert request.service_request_meta.regime == "stable"
    assert request.runner_request.runs == EXPERIMENT_DEFAULTS["runs"]
    assert request.runner_request.ticks == EXPERIMENT_DEFAULTS["ticks"]
    assert request.runner_request.seed == DEFAULT_MASTER_SEED
    assert request.service_request_meta.execution_features.plotting is False
    assert request.service_request_meta.execution_features.plot_dev is False
    assert request.service_request_meta.execution_features.perf_profiling is False
    assert request.service_request_meta.execution_features.capture_world_frames is False
    assert request.processing_request.tail_fraction == tail_fraction


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

    assert isinstance(request, ServiceRequest)
    _assert_default_experiment_request(request, tail_fraction=0.25)

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

    assert isinstance(request, ServiceRequest)
    _assert_default_experiment_request(request, tail_fraction=0.5)


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

    assert isinstance(context, ServiceRequest)
    _assert_default_experiment_request(context, tail_fraction=0.5)


def test_cli_smoke_verify_request_build():
    parser = build_parser()
    args = parser.parse_args(["verify", "--suite", "determinism"])

    request = build_verification_request(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=args.pytest_args,
    )

    assert isinstance(request, ServiceRequest)
    assert request.service_request_meta.mode is ExecutionMode.VERIFICATION
    assert request.service_request_meta.suite == "determinism"
    assert request.processing_request.verbose is False
    assert request.processing_request.fail_fast is False
    assert request.processing_request.pytest_args == ()


def test_cli_smoke_validate_request_build():
    parser = build_parser()
    args = parser.parse_args(["validate", "--suite", "contracts"])

    request = build_validation_request(
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=args.pytest_args,
    )

    assert isinstance(request, ServiceRequest)
    assert request.service_request_meta.mode is ExecutionMode.VALIDATION
    assert request.service_request_meta.suite == "contracts"
    assert request.processing_request.verbose is False
    assert request.processing_request.fail_fast is False
    assert request.processing_request.pytest_args == ()


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
        [sys.executable, "-m", "FestinaLente.main", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "experiment" in result.stdout
    assert "verify" in result.stdout
    assert "validate" in result.stdout


def test_cli_smoke_verify_determinism_runs():
    result = subprocess.run(
        [sys.executable, "-m", "FestinaLente.main", "verify", "--suite", "determinism"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "[verification] Running verification suite: determinism" in result.stdout



if __name__ == "__main__":
    pass
