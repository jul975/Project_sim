from __future__ import annotations

from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.service_models.default import DEFAULT_MASTER_SEED, EXPLORATION_DEFAULTS
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.spec import RegimeSpec
from engine_build.runner.batch_runner import BatchRunner
from engine_build.runner.results import BatchRunResults, RunArtifacts
from engine_build.visualisation.dynamic_new import animate_run


# NOTE: Service should own the workflow

# get request
# validate request
# build workflow context (compile regime, build runner, results handlers, presenters, etc.)
# run workflow
    # create single source of truth for all entry points (CLI, menu, API, etc.) to get workflow context from.
    # pass to runner
# process results runner (summarise, classify, print, plot, etc.)
# return exit code


def exploration_service_call(exploration_request: ServiceRequest) -> int:
    if exploration_request.service_request_meta.regime is None:
        raise ValueError("Exploration mode requires a regime.")

    regime_spec: RegimeSpec = get_regime_spec(exploration_request.service_request_meta.regime)
    regime_config: CompiledRegime = compile_regime(regime_spec)

    seed: int = exploration_request.runner_request.seed if exploration_request.runner_request.seed is not None else DEFAULT_MASTER_SEED
    ticks: int = exploration_request.runner_request.ticks if exploration_request.runner_request.ticks is not None else EXPLORATION_DEFAULTS["ticks"]

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=1,
        batch_id=seed,
        include_world_frames=True,
        include_perf=False,
    )

    batch_results: BatchRunResults = runner.run_batch(ticks=ticks)
    run_result: RunArtifacts = batch_results.runs[0]
    animate_run(run_result, fps=10)
    return 0


if __name__ == "__main__":
    pass