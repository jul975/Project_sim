from __future__ import annotations


from engine_build.app.cli.request_builder import build_experiment_request, build_verification_request, build_validation_request, build_exploration_request
from engine_build.app.execution_model.suite_registry import REGIME_OPTIONS, VERIFICATION_SUITES, VALIDATION_SUITES

from engine_build.app.execution_model.execution_request import ExecutionRequest

from typing import Sequence





###########

def _choose_from_list(prompt: str, options: Sequence[str]) -> str:
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
    print("\n--- Exploration Setup ---")
    return {
        "regime": _choose_from_list("Select regime", REGIME_OPTIONS),
        "seed": _optional_int("Seed"),
        "ticks": _optional_int("Ticks", allow_zero=False),
    }

def _collect_verification_inputs() -> dict[str, object]:
    print("\n--- Verification Setup ---")
    return {
        "suite": _choose_from_list("Select verification suite", tuple(VERIFICATION_SUITES.keys())),
        "verbose": _yes_no("Verbose output?", default=False),
        "fail_fast": _yes_no("Fail fast?", default=False),
        "pytest_args": tuple(input("Extra pytest args (space-separated, leave blank for none): ").split()),
    }

def _collect_validation_inputs() -> dict[str, object]:
    print("\n--- Validation Setup ---")
    return {
        "suite": _choose_from_list("Select validation suite", tuple(VALIDATION_SUITES.keys())),
        "verbose": _yes_no("Verbose output?", default=False),
        "fail_fast": _yes_no("Fail fast?", default=False),
        "pytest_args": tuple(input("Extra pytest args (space-separated, leave blank for none): ").split()),
    }

############

def _print_experiment_summary(inputs: dict[str, object]) -> None:
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
    print("\nExploration summary:")
    print("  mode                 : EXPLORATION")
    print(f"  regime               : {inputs['regime']}")
    print(f"  ticks                : {inputs['ticks']}")
    print(f"  seed                 : {inputs['seed']}")


def _print_verification_summary(inputs: dict[str, object]) -> None:
    print("\nVerification summary:")
    print("  mode                 : VERIFICATION")
    print(f"  suite                : {inputs['suite']}")
    print(f"  verbose              : {inputs['verbose']}")
    print(f"  fail_fast            : {inputs['fail_fast']}")
    print(f"  pytest_args          : {inputs['pytest_args']}")


def _print_validation_summary(inputs: dict[str, object]) -> None:
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
    while True:
        answers = collect_fn()
        summary_fn(answers)
        if _yes_no(confirm_prompt, default=True):
            return build_fn(**answers)



#############

def _build_experiment_request_from_menu() -> ExecutionRequest:
    return _confirm_and_build(
        collect_fn=_collect_experiment_inputs,
        summary_fn=_print_experiment_summary,
        build_fn=build_experiment_request,
        confirm_prompt="Launch experiment?",
    )
        
def _build_exploration_request_from_menu() -> ExecutionRequest:
    return _confirm_and_build(
        collect_fn=_collect_exploration_inputs,
        summary_fn=_print_exploration_summary,
        build_fn=build_exploration_request,
        confirm_prompt="Launch exploration?",
    )

def _build_verification_request_from_menu() -> ExecutionRequest:
    return _confirm_and_build(
        collect_fn=_collect_verification_inputs,
        summary_fn=_print_verification_summary,
        build_fn=build_verification_request,
        confirm_prompt="Launch verification?",
    )


def _build_validation_request_from_menu() -> ExecutionRequest:
    return _confirm_and_build(
        collect_fn=_collect_validation_inputs,
        summary_fn=_print_validation_summary,
        build_fn=build_validation_request,
        confirm_prompt="Launch validation?",
    )


def _build_validation_request_from_menu() -> ExecutionRequest:
    return _confirm_and_build(
        collect_fn=_collect_validation_inputs,
        summary_fn=_print_validation_summary,
        build_fn=build_validation_request,
        confirm_prompt="Launch validation?",
    )

        
def run_menu() -> ExecutionRequest | None:
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