"""Interactive menu helpers for building execution requests.

This module gathers console input, prints confirmation summaries, and returns
normalized ``ExecutionRequest`` objects through the shared request-builder
layer.
"""

from __future__ import annotations


from engine_build.app.cli.request_builder import build_experiment_request, build_verification_request, build_validation_request, build_exploration_request
from engine_build.app.service_models.suite_registry import REGIME_OPTIONS, VERIFICATION_SUITES, VALIDATION_SUITES

from engine_build.app.service_models.service_request_container import ExecutionRequest

from typing import Sequence





###########

def _choose_from_list(prompt: str, options: Sequence[str]) -> str:
    """Prompt the user to choose one value from a numbered list.

    Args:
        prompt: Label shown above the numbered options.
        options: Ordered option strings available for selection.

    Returns:
        The selected option string.
    """
    print(f"\n{prompt}:")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    while True:
        choice = input("Enter choice number: ")
        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        index = int(choice) - 1
        if 0 <= index < len(options):
            return options[index]
        print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
    
def _optional_int(prompt: str, allow_zero: bool = True) -> int | None:
    """Read an optional integer from console input.

    Args:
        prompt: Prompt label displayed to the user.
        allow_zero: Whether ``0`` is accepted as a valid value.

    Returns:
        Parsed integer value, or ``None`` when the input is left blank.
    """
    while True:
        value = input(f"{prompt} (leave blank for default): ")
        if value == "":
            return None
        if value.isdigit():
            int_value = int(value)
            if allow_zero or int_value > 0:
                return int_value
        print("Invalid input. Please enter a positive integer or leave blank.")

def _optional_float(prompt: str, default: float, min_value: float = float("-inf"), max_value: float = float("inf")) -> float:
    """Read an optional bounded float from console input.

    Args:
        prompt: Prompt label displayed to the user.
        default: Value returned when the input is left blank.
        min_value: Inclusive lower bound for valid input.
        max_value: Inclusive upper bound for valid input.

    Returns:
        Parsed float value or the provided default.
    """
    while True:
        value = input(f"{prompt} (default {default}): ")
        if value == "":
            return default
        try:
            float_value = float(value)
            if min_value <= float_value <= max_value:
                return float_value
            print(f"Value must be between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a number or leave blank.")

def _yes_no(prompt: str, default: bool = False) -> bool:
    """Read a yes/no response from console input.

    Args:
        prompt: Prompt label displayed to the user.
        default: Value returned when the user presses enter with no input.

    Returns:
        ``True`` for yes-style responses and ``False`` for no-style responses.
    """
    default_str = "Y/n" if default else "y/N"
    while True:
        value = input(f"{prompt} ({default_str}): ").strip().lower()
        if value == "":
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Invalid input. Please enter 'y' or 'n'.")


##################


def _collect_experiment_inputs() -> dict[str, object]:
    """Collect menu inputs required to build an experiment request."""
    print("\n--- Experiment Setup ---")
    return {
        "regime": _choose_from_list("Select regime", REGIME_OPTIONS),
        "runs": _optional_int("Runs", allow_zero=False),
        "ticks": _optional_int("Ticks", allow_zero=False),
        "seed": _optional_int("Seed"),
        "plot": _yes_no("Plot batch results?", default=False),
        "plot_dev": _yes_no("Plot dev figures?", default=False),
        "profiling": _yes_no("Enable perf profiling?", default=False),
        "capture_world_frames": _yes_no("Enable world-frame capture?", default=False),
        "tail_fraction": _optional_float(
            "Tail fraction",
            default=0.25,
            min_value=0.0,
            max_value=1.0,
        ),
    }

def _collect_exploration_inputs() -> dict[str, object]:
    """Collect menu inputs required to build an exploration request."""
    print("\n--- Exploration Setup ---")
    return {
        "regime": _choose_from_list("Select regime", REGIME_OPTIONS),
        "seed": _optional_int("Seed"),
        "ticks": _optional_int("Ticks", allow_zero=False),
    }

def _collect_verification_inputs() -> dict[str, object]:
    """Collect menu inputs required to build a verification request."""
    print("\n--- Verification Setup ---")
    return {
        "suite": _choose_from_list("Select verification suite", tuple(VERIFICATION_SUITES.keys())),
        "verbose": _yes_no("Verbose output?", default=False),
        "fail_fast": _yes_no("Fail fast?", default=False),
        "pytest_args": tuple(input("Extra pytest args (space-separated, leave blank for none): ").split()),
    }

def _collect_validation_inputs() -> dict[str, object]:
    """Collect menu inputs required to build a validation request."""
    print("\n--- Validation Setup ---")
    return {
        "suite": _choose_from_list("Select validation suite", tuple(VALIDATION_SUITES.keys())),
        "verbose": _yes_no("Verbose output?", default=False),
        "fail_fast": _yes_no("Fail fast?", default=False),
        "pytest_args": tuple(input("Extra pytest args (space-separated, leave blank for none): ").split()),
    }

############

def _print_experiment_summary(inputs: dict[str, object]) -> None:
    """Print a confirmation summary for experiment inputs."""
    print("\nExperiment summary:")
    print("  mode                 : EXPERIMENT")
    print(f"  regime               : {inputs['regime']}")
    print(f"  runs                 : {inputs['runs']}")
    print(f"  ticks                : {inputs['ticks']}")
    print(f"  seed                 : {inputs['seed']}")
    print(f"  plot                 : {inputs['plot']}")
    print(f"  plot_dev             : {inputs['plot_dev']}")
    print(f"  profile              : {inputs['profiling']}")
    print(f"  capture_world_frames : {inputs['capture_world_frames']}")
    print(f"  tail_fraction        : {inputs['tail_fraction']}")

def _print_exploration_summary(inputs: dict[str, object]) -> None:
    """Print a confirmation summary for exploration inputs."""
    print("\nExploration summary:")
    print("  mode                 : EXPLORATION")
    print(f"  regime               : {inputs['regime']}")
    print(f"  ticks                : {inputs['ticks']}")
    print(f"  seed                 : {inputs['seed']}")


def _print_verification_summary(inputs: dict[str, object]) -> None:
    """Print a confirmation summary for verification inputs."""
    print("\nVerification summary:")
    print("  mode                 : VERIFICATION")
    print(f"  suite                : {inputs['suite']}")
    print(f"  verbose              : {inputs['verbose']}")
    print(f"  fail_fast            : {inputs['fail_fast']}")
    print(f"  pytest_args          : {inputs['pytest_args']}")


def _print_validation_summary(inputs: dict[str, object]) -> None:
    """Print a confirmation summary for validation inputs."""
    print("\nValidation summary:")
    print("  mode                 : VALIDATION")
    print(f"  suite                : {inputs['suite']}")
    print(f"  verbose              : {inputs['verbose']}")
    print(f"  fail_fast            : {inputs['fail_fast']}")
    print(f"  pytest_args          : {inputs['pytest_args']}")

##############

def _confirm_and_build(
    *,
    collect_fn,
    summary_fn,
    build_fn,
    confirm_prompt: str,
) -> ExecutionRequest:
    """Collect inputs, show a summary, and build a confirmed request.

    Args:
        collect_fn: Callable that gathers raw answers from the user.
        summary_fn: Callable that prints the collected answers.
        build_fn: Request-builder callable used after confirmation.
        confirm_prompt: Confirmation prompt shown before building the request.

    Returns:
        Confirmed execution request built from the collected answers.
    """
    while True:
        answers = collect_fn()
        summary_fn(answers)
        if _yes_no(confirm_prompt, default=True):
            return build_fn(**answers)



#############

def _build_experiment_request_from_menu() -> ExecutionRequest:
    """Build an experiment request through the interactive menu flow."""
    return _confirm_and_build(
        collect_fn=_collect_experiment_inputs,
        summary_fn=_print_experiment_summary,
        build_fn=build_experiment_request,
        confirm_prompt="Launch experiment?",
    )
        
def _build_exploration_request_from_menu() -> ExecutionRequest:
    """Build an exploration request through the interactive menu flow."""
    return _confirm_and_build(
        collect_fn=_collect_exploration_inputs,
        summary_fn=_print_exploration_summary,
        build_fn=build_exploration_request,
        confirm_prompt="Launch exploration?",
    )

def _build_verification_request_from_menu() -> ExecutionRequest:
    """Build a verification request through the interactive menu flow."""
    return _confirm_and_build(
        collect_fn=_collect_verification_inputs,
        summary_fn=_print_verification_summary,
        build_fn=build_verification_request,
        confirm_prompt="Launch verification?",
    )


def _build_validation_request_from_menu() -> ExecutionRequest:
    """Build a validation request through the interactive menu flow."""
    return _confirm_and_build(
        collect_fn=_collect_validation_inputs,
        summary_fn=_print_validation_summary,
        build_fn=build_validation_request,
        confirm_prompt="Launch validation?",
    )


def _build_validation_request_from_menu() -> ExecutionRequest:
    """Build a validation request through the interactive menu flow."""
    return _confirm_and_build(
        collect_fn=_collect_validation_inputs,
        summary_fn=_print_validation_summary,
        build_fn=build_validation_request,
        confirm_prompt="Launch validation?",
    )

        
def run_menu() -> ExecutionRequest | None:
    """Run the interactive menu and return the selected execution request.

    Returns:
        Built execution request for the selected mode, or ``None`` when the
        user chooses to exit.
    """
    print("Welcome to the Engine Build CLI!")
    print("Please select an execution mode:")
    mode = _choose_from_list("Execution mode", ["Experiment", "Exploration", "Verification", "Validation", "Exit"])

    if mode == "Experiment":
        request = _build_experiment_request_from_menu()
        return request
    elif mode == "Exploration":
        request = _build_exploration_request_from_menu()
        return request
    elif mode == "Verification":
        request = _build_verification_request_from_menu()
        return request
    elif mode == "Validation":
        request = _build_validation_request_from_menu()
        return request
    elif mode == "Exit":
        print("Exiting. Goodbye!")
        return None
    else:
        print("Invalid mode selected.")
        return None

if __name__ == "__main__":
    run_menu()
