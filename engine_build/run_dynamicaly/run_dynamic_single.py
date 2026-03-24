


from engine_build.visualisation.dynamic_new import animate_run
from engine_build.runner.regime_runner import RunArtifacts, Runner, BatchRunResults
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.compiled import CompiledRegime
from engine_build.execution.default import DEFAULT_MASTER_SEED
from engine_build.cli.requests import DynamicRunRequest





def run_dynamic_mode(request : DynamicRunRequest) -> int:
    regime_spec = get_regime_spec(request.regime)
    regime_config: CompiledRegime = compile_regime(regime_spec)

    seed = request.seed if request.seed is not None else DEFAULT_MASTER_SEED

    runner = Runner(
        regime_config=regime_config,
        n_runs=1,
        batch_id=seed,
        include_world_frames=True,
    )

    batch_results: BatchRunResults = runner.run_regime_batch(ticks=request.ticks if request.ticks is not None else 1000)
    run_results: RunArtifacts = batch_results.runs[0]
    animate_run(run_results, fps=10)



