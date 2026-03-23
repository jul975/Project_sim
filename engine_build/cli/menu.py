from __future__ import annotations

from typing import Sequence

from engine_build.cli.requests import (
    ExperimentRequest,
    VerificationRequest,
    ValidationRequest,
)
from engine_build.cli.spec import (
    REGIME_OPTIONS,
    verification_suite_choices,
    validation_suite_choices,
)

MenuRequest = ExperimentRequest | VerificationRequest | ValidationRequest | None


def run_menu() -> MenuRequest:
    while True:
        print("\n" + "=" * 50)
        print(" Ecosystem Emergent Behavior Simulator ")
        print("=" * 50)
        print("1. Run experiment")
        print("2. Run verification suite")
        print("3. Run validation suite")
        print("4. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            return _build_experiment_request()
        if choice == "2":
            return _build_verification_request()
        if choice == "3":
            return _build_validation_request()
        if choice == "4":
            return None

        print("Invalid choice.")


def _build_experiment_request() -> ExperimentRequest:
    print("\n--- Experiment Setup ---")
    regime = _choose_from_list("Select regime", REGIME_OPTIONS)
    runs = _optional_int("Runs", allow_zero=False)
    ticks = _optional_int("Ticks", allow_zero=False)
    seed = _optional_int("Seed")
    plot = _yes_no("Plot batch results?", default=False)
    plot_dev = _yes_no("Plot dev figures?", default=False)
    perf_flag = _yes_no("Enable perf profiling?", default=False)
    world_frame_flag = _yes_no("Enable world-frame capture?", default=False)
    tail_fraction = _optional_float("Tail fraction", default=0.25, min_value=0.0, max_value=1.0)

    print("\nExperiment summary:")
    print(f"  regime           : {regime}")
    print(f"  runs             : {runs}")
    print(f"  ticks            : {ticks}")
    print(f"  seed             : {seed}")
    print(f"  plot             : {plot}")
    print(f"  plot_dev         : {plot_dev}")
    print(f"  perf_flag        : {perf_flag}")
    print(f"  world_frame_flag : {world_frame_flag}")
    print(f"  tail_fraction    : {tail_fraction}")

    if not _yes_no("Launch experiment?", default=True):
        return _build_experiment_request()

    return ExperimentRequest(
        regime=regime,
        runs=runs,
        ticks=ticks,
        seed=seed,
        plot=plot,
        plot_dev=plot_dev,
        perf_flag=perf_flag,
        world_frame_flag=world_frame_flag,
        tail_fraction=tail_fraction,
    )


def _build_verification_request() -> VerificationRequest:
    print("\n--- Verification Setup ---")
    suite = _choose_from_list("Select verification suite", verification_suite_choices())
    verbose = _yes_no("Verbose output?", default=False)
    fail_fast = _yes_no("Fail fast?", default=False)

    print("\nVerification summary:")
    print(f"  suite     : {suite}")
    print(f"  verbose   : {verbose}")
    print(f"  fail_fast : {fail_fast}")

    if not _yes_no("Run verification?", default=True):
        return _build_verification_request()

    return VerificationRequest(
        suite=suite,
        verbose=verbose,
        fail_fast=fail_fast,
    )


def _build_validation_request() -> ValidationRequest:
    print("\n--- Validation Setup ---")
    suite = _choose_from_list("Select validation suite", validation_suite_choices())
    verbose = _yes_no("Verbose output?", default=False)
    fail_fast = _yes_no("Fail fast?", default=False)

    print("\nValidation summary:")
    print(f"  suite     : {suite}")
    print(f"  verbose   : {verbose}")
    print(f"  fail_fast : {fail_fast}")

    if not _yes_no("Run validation?", default=True):
        return _build_validation_request()

    return ValidationRequest(
        suite=suite,
        verbose=verbose,
        fail_fast=fail_fast,
    )


def _choose_from_list(title: str, options: Sequence[str]) -> str:
    while True:
        print(f"\n{title}:")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")

        raw = input("Enter choice number: ").strip()

        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]

        print("Invalid selection.")


def _optional_int(label: str, allow_zero: bool = True) -> int | None:
    while True:
        raw = input(f"{label} [blank = default]: ").strip()

        if raw == "":
            return None

        try:
            value = int(raw)
        except ValueError:
            print("Please enter an integer or leave blank.")
            continue

        if not allow_zero and value <= 0:
            print("Please enter a positive integer.")
            continue

        return value


def _optional_float(
    label: str,
    *,
    default: float,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    while True:
        raw = input(f"{label} [blank = {default}]: ").strip()

        if raw == "":
            return default

        try:
            value = float(raw)
        except ValueError:
            print("Please enter a float or leave blank.")
            continue

        if min_value is not None and value < min_value:
            print(f"Please enter a value >= {min_value}.")
            continue

        if max_value is not None and value > max_value:
            print(f"Please enter a value <= {max_value}.")
            continue

        return value


def _yes_no(prompt: str, default: bool) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"

    while True:
        raw = input(f"{prompt} {suffix}: ").strip().lower()

        if raw == "":
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False

        print("Please enter y or n.")