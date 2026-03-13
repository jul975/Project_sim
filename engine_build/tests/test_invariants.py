import pytest

from engine_build.tests.helpers import advance_engine


@pytest.mark.dev
@pytest.mark.invariant
def test_spatial_invariants(make_engine, stable_regime, seed_ref, ticks_mid):
    eng = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_mid)

    for agent in eng.agents.values():
        x, y = agent.position
        assert 0 <= x < eng.world.world_width
        assert 0 <= y < eng.world.world_height


@pytest.mark.dev
@pytest.mark.invariant
def test_resource_bounds(make_engine, stable_regime, seed_ref, ticks_mid):
    eng = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_mid)

    assert (eng.world.resources >= 0).all()
    assert (eng.world.resources <= eng.world.fertility).all()


@pytest.mark.dev
@pytest.mark.invariant
def test_identity_monotonicity(make_engine, stable_regime, seed_ref, ticks_mid):
    eng = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_mid)

    ids = sorted(eng.agents.keys())
    if ids:
        assert max(ids) < eng.next_agent_id