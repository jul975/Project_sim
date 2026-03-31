# repeated runner logic

from engine_build.runner.batch_runner import BatchRunner
from engine_build.core.engine import Engine
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.analytics.pipelines.analyze_batch import analyze_batch
from engine_build.app.execution_model.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from dataclasses import fields
import numpy as np


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

    batch_results = runner.run_batch(ticks=VALIDATION_DEFAULTS["ticks"])
    return analyze_batch(batch_results, regime_label=regime_name)


if __name__ == "__main__":
    pass