from __future__ import annotations

from engine_build.app.execution_model.execution_request import ExecutionRequest
from engine_build.app.execution_model.default import DEFAULT_MASTER_SEED, EXPLORATION_DEFAULTS
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.runner.batch_runner import BatchRunner
from engine_build.visualisation.dynamic_new import animate_run


def run_exploration(context: ExecutionRequest) -> int:
    if context.regime is None:
        raise ValueError("Exploration mode requires a regime.")

    regime_spec = get_regime_spec(context.regime)
    regime_config = compile_regime(regime_spec)

    seed = context.seed if context.seed is not None else DEFAULT_MASTER_SEED
    ticks = context.ticks if context.ticks is not None else EXPLORATION_DEFAULTS["ticks"]

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=1,
        batch_id=seed,
        include_world_frames=True,
        include_perf=False,
    )

    batch_results = runner.run_batch(ticks=ticks)
    run_result = batch_results.runs[0]
    animate_run(run_result, fps=10)
    return 0


if __name__ == "__main__":
    pass