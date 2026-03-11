# repeated runner logic

from engine_build.runner.regime_runner import Runner
from engine_build.core.engineP4 import Engine
from engine_build.regimes.compiled import CompiledRegime


def run_single(seed: int, regime_config : CompiledRegime, ticks: int):
    runner = Runner(
        regime_config=regime_config,
        n_runs=1,
        batch_id=seed,
    )
    return runner.run_single(runner.run_seeds[0], ticks)


def advance_engine(engine : "Engine", ticks: int):
    for _ in range(ticks):
        engine.step()
    return engine