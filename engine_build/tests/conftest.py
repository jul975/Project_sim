import numpy as np
import pytest

from engine_build.core.engineP4 import Engine
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime


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
        return Engine(np.random.SeedSequence(seed), regime_config, **kwargs)
    return _make_engine