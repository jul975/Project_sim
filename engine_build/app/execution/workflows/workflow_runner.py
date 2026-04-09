
from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.service_models.default import EXPERIMENT_DEFAULTS
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.spec import RegimeSpec
from engine_build.runner.batch_runner import BatchRunner, BatchRunResults
from engine_build.app.execution.presenters.console import print_experiment_spec

from engine_build.analytics.contracts.analysis_context import AnalysisContext, AnalysisOptions


def build_and_run_batch(batch_request: ServiceRequest) -> tuple[BatchRunResults, AnalysisContext]:
    """ build batch, run batch and return batch results from context. """

# def sep function for building and retuning batch 
    regime_spec : RegimeSpec = get_regime_spec(batch_request.regime)
    regime_config : CompiledRegime = compile_regime(regime_spec=regime_spec)

    ticks = batch_request.ticks if batch_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = batch_request.runs if batch_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    # NOTE: temp need to move 
    print_experiment_spec(regime_spec)

    runner : BatchRunner = BatchRunner(
        regime_config=regime_config,
        n_runs=runs,
        batch_id=batch_request.seed,
        include_world_frames=batch_request.features.capture_world_frames,
        include_perf=batch_request.features.profiling,
    )

    batch_results : BatchRunResults = runner.run_batch(ticks=ticks)

    analysis_context = AnalysisContext(
        n_runs=runs,
        total_tics=ticks,
        tail_fraction=batch_request.tail_fraction,
        regime_label=batch_request.regime,
        compiled_regime=regime_config,
        options=AnalysisOptions(
            include_perf=batch_request.features.profiling,
            include_world_frames=batch_request.features.capture_world_frames,
        ),
    )
    
    return batch_results, analysis_context


if __name__ == "__main__":
    pass