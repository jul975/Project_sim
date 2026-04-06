
from engine_build.app.execution_model.execution_context import ExecutionContext
from engine_build.app.execution_model.default import EXPERIMENT_DEFAULTS
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.runner.batch_runner import BatchRunner, BatchRunResults
from engine_build.app.execution.presenters.console import print_experiment_spec

from engine_build.analytics.contracts.analysis_context import AnalysisContext, AnalysisOptions


def build_and_run_batch(context: ExecutionContext) -> tuple[BatchRunResults, AnalysisContext]:
    """ build batch, run batch and return batch results from context. """

# def sep function for building and retuning batch 
    regime_spec = get_regime_spec(context.regime)
    regime_config = compile_regime(regime_spec)

    ticks = context.ticks if context.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = context.runs if context.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    # NOTE: temp need to move 
    print_experiment_spec(regime_spec)

    runner : BatchRunner = BatchRunner(
        regime_config=regime_config,
        n_runs=runs,
        batch_id=context.seed,
        include_world_frames=context.features.capture_world_frames,
        include_perf=context.features.profiling,
    )

    batch_results : BatchRunResults = runner.run_batch(ticks=ticks)

    analysis_context = AnalysisContext(
        n_runs=runs,
        total_tics=ticks,
        tail_fraction=context.tail_fraction,
        regime_label=context.regime,
        compiled_regime=regime_config,
        options=AnalysisOptions(
            include_perf=context.features.profiling,
            include_world_frames=context.features.capture_world_frames,
        ),
    )
    
    return batch_results, analysis_context


if __name__ == "__main__":
    pass