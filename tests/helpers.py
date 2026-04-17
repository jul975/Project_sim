# repeated runner logic

from numpy.random.bit_generator import SeedSequence

from FestinaLente.app.execution.workflows.compile_workflow import (
    AnalysisOptions,
    BatchPlan,
    EngineTemplate,
    ProcessingPlan,
)
from FestinaLente.runner.batch_runner import BatchRunner
from FestinaLente.core.engine import Engine
from FestinaLente.regimes.compiled import CompiledRegime
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.compiler import compile_regime
from FestinaLente.analytics.processing.process_batch import analyze_batch
from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from dataclasses import fields
import numpy as np
from FestinaLente.runner.single_runner import SingleRunner
from FestinaLente.runner.utils.factories import EngineBuildMap
from FestinaLente.runner.utils.results import BatchRunResults
from FestinaLente.runner.utils.seeds import generate_run_sequences


def run_single(seed: int, regime_config : CompiledRegime, ticks: int) :
    """ runs a single simulation for a given seed and ticks. """
    run_sequence: dict[int, SeedSequence] = generate_run_sequences(seed, n_runs=1)
    engine_template = EngineTemplate(
        regime_config=regime_config,
        perf_flag=False,
        world_frame_flag=False,
        change_condition=False
    )
    runner_map = EngineBuildMap(
        run_seed=run_sequence[1],
        engine_template=engine_template
    )
    single_runner = SingleRunner(runner_map)

    
    return single_runner.run(ticks=ticks)


def advance_engine(engine : "Engine", ticks: int):
    """ advances engine by ticks. """
    for _ in range(ticks):
        engine.step()
    return engine






def assert_aggregate_fingerprint_finite(agg) -> None:
    for f in fields(agg):
        value = getattr(agg, f.name)
        assert np.isfinite(value), f"Invalid aggregate field: {f.name}={value}"


def run_regime_analysis(regime_name: str):
    """ runs a regime analysis for a given regime. """
    regime_spec = get_regime_spec(regime_name)
    regime_config = compile_regime(regime_spec)

    engine_template = EngineTemplate(
        regime_config=regime_config,
        perf_flag=True,
        world_frame_flag=True,
        change_condition=False,
    )
    runner_plan = BatchPlan(
        engine_template=engine_template,
        batch_id=DEFAULT_MASTER_SEED,
        n_runs=VALIDATION_DEFAULTS["runs"],
        ticks=VALIDATION_DEFAULTS["ticks"],
    )
    runner = BatchRunner(runner_plan)

    analysis_context = ProcessingPlan(
        n_runs=VALIDATION_DEFAULTS["runs"],
        total_tics=VALIDATION_DEFAULTS["ticks"],
        regime_label=regime_name,
        compiled_regime=regime_config,
        options=AnalysisOptions(
            include_world_frames=True,
            include_perf=True,
        ),
    )


    batch_results: BatchRunResults = runner.run_batch(ticks=runner_plan.ticks)
    return analyze_batch(processing_plan=analysis_context, batch_results=batch_results)


if __name__ == "__main__":
    pass
