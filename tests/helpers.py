# repeated runner logic

from FestinaLente.runner.batch_runner import BatchRunner
from FestinaLente.core.engine import Engine
from FestinaLente.regimes.compiled import CompiledRegime
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.compiler import compile_regime
from FestinaLente.analytics.derive.process_batch import analyze_batch
from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from dataclasses import fields
import numpy as np
from FestinaLente.analytics.contracts.analysis_context import AnalysisContext


def run_single(seed: int, regime_config : CompiledRegime, ticks: int) :
    """ runs a single simulation for a given seed and ticks. """
    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=1,
        batch_id=seed,
    )
    return runner.run_single(runner.run_seeds[0], ticks)


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

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=VALIDATION_DEFAULTS["runs"],
        batch_id=DEFAULT_MASTER_SEED,
    )
    analysis_context = AnalysisContext(
        include_world_frames=True,
        include_perf=True,
        regime_label=regime_name,
    )


    batch_results = runner.run_batch(ticks=VALIDATION_DEFAULTS["ticks"])
    return analyze_batch(batch_results, analysis_context)


if __name__ == "__main__":
    pass