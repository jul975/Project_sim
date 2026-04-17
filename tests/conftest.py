import numpy as np
import pytest

from FestinaLente.app.execution.workflows.compile_workflow import EngineTemplate
from FestinaLente.core.engine import Engine
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.compiler import compile_regime


@pytest.fixture
def stable_regime():
    return compile_regime(get_regime_spec("stable"))


@pytest.fixture
def extinction_regime():
    return compile_regime(get_regime_spec("extinction"))


@pytest.fixture
def saturated_regime():
    return compile_regime(get_regime_spec("saturated"))


@pytest.fixture
def seed_ref():
    return 42


@pytest.fixture
def seed_a():
    return 1


@pytest.fixture
def seed_b():
    return 2


@pytest.fixture
def ticks_short():
    return 200


@pytest.fixture
def ticks_mid():
    return 1000


@pytest.fixture
def ticks_long():
    return 5000


@pytest.fixture
def make_engine():
    def _make_engine(seed: int, regime_config, **kwargs):
        perf_flag = kwargs.pop("perf_flag", False)
        collect_worldview = kwargs.pop("collect_worldview", False)
        world_frame_flag = kwargs.pop("world_frame_flag", collect_worldview)
        change_condition = kwargs.pop("change_condition", False)
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"Unexpected engine fixture kwargs: {unexpected}")

        engine_template = EngineTemplate(
            regime_config=regime_config,
            perf_flag=perf_flag,
            world_frame_flag=world_frame_flag,
            change_condition=change_condition,
        )
        return Engine(
            engine_template,
            np.random.SeedSequence(seed),
            perf_flag=perf_flag,
            collect_worldview=world_frame_flag,
        )
    return _make_engine
