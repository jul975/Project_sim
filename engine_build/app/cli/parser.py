from engine_build.app.execution.context import ExecutionContext
from engine_build.app.execution.features import ExecutionFeatures
from engine_build.app.execution.modes import ExecutionMode

def build_experiment_context(args) -> ExecutionContext:
    return ExecutionContext(
        mode=ExecutionMode.EXPERIMENT,
        regime=args.regime,
        seed=args.seed,
        runs=args.runs,
        ticks=args.ticks,
        tail_fraction=args.tail_fraction,
        features=ExecutionFeatures(
            plot=args.plot,
            plot_dev=args.plot_dev,
            profile=args.perf_flag,
            capture_world_frames=args.world_frame_flag,
        ),
    )


def build_verification_context(args) -> ExecutionContext:
    return ExecutionContext(
        mode=ExecutionMode.VERIFICATION,
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=tuple(args.pytest_args),
    )


def build_validation_context(args) -> ExecutionContext:
    return ExecutionContext(
        mode=ExecutionMode.VALIDATION,
        suite=args.suite,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        pytest_args=tuple(args.pytest_args),
    )


def build_exploration_context(args) -> ExecutionContext:
    return ExecutionContext(
        mode=ExecutionMode.EXPLORATION,
        regime=args.regime,
        seed=args.seed,
        ticks=args.ticks,
        features=ExecutionFeatures(animate=True),
    )