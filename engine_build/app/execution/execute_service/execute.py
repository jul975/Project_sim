
from engine_build.app.execution_model.context import ExecutionContext
from engine_build.app.execution_model.default import EXPERIMENT_DEFAULTS
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.runner.batch_runner import BatchRunner, BatchRunResults
from engine_build.analytics.pipelines.analyze_batch import analyze_batch, AnalysisConfig, BatchAnalysis

from engine_build.app.execution.presenters.console import print_experiment_spec


def build_batch_analysis(context: ExecutionContext) -> BatchAnalysis:
    """ build batch, run batch and return analysis from context. """
# def sep function for building and retuning batch analysis
    regime_spec = get_regime_spec(context.regime)
    regime_config = compile_regime(regime_spec)

    ticks = context.ticks if context.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = context.runs if context.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    print_experiment_spec(regime_spec)

    runner : BatchRunner = BatchRunner(
        regime_config=regime_config,
        n_runs=runs,
        batch_id=context.seed,
        include_world_frames=context.features.capture_world_frames,
        include_perf=context.features.profiling,
    )

    batch_results : BatchRunResults = runner.run_batch(ticks=ticks)
    
    return analyze_batch(
        batch_results,
        AnalysisConfig(
            include_perf=context.features.profiling,
            include_world_frames=context.features.capture_world_frames,
            regime_label=context.regime,
        ),
    )