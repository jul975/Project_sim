import pytest

from tests.helpers import advance_engine
from engine_build.core.engineP4 import Engine

from engine_build.regimes.compiled import CompiledRegime


@pytest.mark.dev
@pytest.mark.validate
def test_same_seed_determinism(make_engine : Engine, stable_regime_config : CompiledRegime, seed_ref : int, ticks_mid : int):
    eng1 = make_engine(seed_ref, stable_regime_config)
    eng2 = make_engine(seed_ref, stable_regime_config)

    for step in range(ticks_mid):
        eng1.step()
        eng2.step()
        assert eng1.get_state_hash() == eng2.get_state_hash(), f"Divergence at tick {step}"


@pytest.mark.dev
@pytest.mark.validate
def test_snapshot_equivalence(make_engine, stable_regime_config, seed_ref, ticks_short, ticks_mid):
    eng = make_engine(seed_ref, stable_regime_config)
    advance_engine(eng, ticks_short)

    snapshot = eng.get_snapshot()
    clone = eng.__class__.from_snapshot(snapshot)

    for step in range(ticks_mid):
        eng.step()
        clone.step()
        assert eng.get_state_hash() == clone.get_state_hash(), f"Snapshot divergence at tick {step}"


@pytest.mark.validate
def test_seed_sensitivity(make_engine, stable_regime_config, seed_a, seed_b, ticks_mid):
    eng1 = make_engine(seed_a, stable_regime_config)
    eng2 = make_engine(seed_b, stable_regime_config)

    advance_engine(eng1, ticks_mid)
    advance_engine(eng2, ticks_mid)

    assert eng1.get_state_hash() != eng2.get_state_hash()