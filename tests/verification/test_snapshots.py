"""
Group 1 — snapshot shape / validity
    test_snapshot_agent_count_matches_engine
    test_snapshot_world_shape_consistent    
    test_snapshot_config_roundtrips

Group 2 — basic roundtrip
    test_snapshot_roundtrip_at_tick_zero
    test_snapshot_roundtrip_midstream

Group 3 — restored world equality
    test_restored_world_matches_original

Group 4 — restored agent equality
    test_restored_agents_match_original

Group 5 — restored RNG equality
    test_restored_rng_states_match_original

Group 6 — continuation
    test_restored_engine_matches_original_after_one_step
    test_restored_engine_matches_original_after_many_steps

That is what I would call the “deep snapshot suite.”





"""

import pytest

from engine_build.core.engineP4 import Engine
from tests.helpers import advance_engine


@pytest.mark.dev
@pytest.mark.validate
@pytest.mark.snapshot
def test_snapshot_agent_count_matches_engine(make_engine, stable_regime, seed_ref) -> None:
    eng : Engine = make_engine(seed_ref, stable_regime)
    snapshot = eng.get_snapshot()


    assert len(snapshot.agents) == len(eng.agents)
    assert snapshot.next_agent_id == eng.next_agent_id
    assert snapshot.max_agent_count == eng.max_agent_count
    assert snapshot.max_age == eng.max_age
    assert snapshot.reproduction_probability == eng.reproduction_probability


@pytest.mark.dev
@pytest.mark.validate
@pytest.mark.snapshot
def test_snapshot_world_shape_consistent(make_engine, stable_regime, seed_ref) -> None:
    """ test that snapshot world shape is consistent with engine world. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    snapshot = eng.get_snapshot()


    assert snapshot.world.world_width == eng.world.world_width
    assert snapshot.world.world_height == eng.world.world_height
    assert snapshot.world.resources.shape == eng.world.resources.shape
    assert snapshot.world.fertility.shape == eng.world.fertility.shape
    assert snapshot.world.max_harvest == eng.world.max_harvest
    assert snapshot.world.resource_regen_rate == eng.world.resource_regen_rate


@pytest.mark.dev
@pytest.mark.validate
@pytest.mark.snapshot

def test_restored_engine_config_matches_original(make_engine, stable_regime, seed_ref) -> None:
    """ test that restored engine config matches original. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    snapshot = eng.get_snapshot()

    eng2 : Engine = Engine.from_snapshot( snapshot)

    
    assert eng2.config == eng.config
    assert eng2.energy_params == eng.energy_params
    assert eng2.resource_params == eng.resource_params
    assert eng2.landscape_params == eng.landscape_params

    assert eng2.world_params == eng.world_params




@pytest.mark.snapshot
@pytest.mark.dev
def test_snapshot_roundtrip_at_tick_zero(make_engine, stable_regime, seed_ref):
    """ test that snapshot roundtrip at tick zero matches original. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    snapshot = eng.get_snapshot()
    clone = Engine.from_snapshot(snapshot)

    assert clone.get_state_hash() == eng.get_state_hash()




@pytest.mark.snapshot
@pytest.mark.validate
def test_restored_world_matches_original(make_engine, stable_regime, seed_ref, ticks_short) -> None:
    """ test that restored world matches original after some steps. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_short)

    clone = Engine.from_snapshot(eng.get_snapshot())

    assert clone.world.tick == eng.world.tick
    assert clone.world.change_condition == eng.world.change_condition
    assert clone.world.world_width == eng.world.world_width
    assert clone.world.world_height == eng.world.world_height
    assert (clone.world.resources == eng.world.resources).all()
    assert (clone.world.fertility == eng.world.fertility).all()
    assert clone.world.max_harvest == eng.world.max_harvest
    assert clone.world.resource_regen_rate == eng.world.resource_regen_rate


@pytest.mark.snapshot
@pytest.mark.validate
def test_snapshot_roundtrip_midstream(make_engine, stable_regime, seed_ref, ticks_short):
    eng : Engine = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_short)

    snapshot = eng.get_snapshot()
    clone = Engine.from_snapshot(snapshot)

    assert clone.get_state_hash() == eng.get_state_hash()







@pytest.mark.snapshot
@pytest.mark.validate
def test_restored_agents_match_original(make_engine, stable_regime, seed_ref, ticks_short) -> None:
    """ test that restored agents match original after some steps. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    
    advance_engine(eng, ticks_short)

    clone = Engine.from_snapshot(eng.get_snapshot())

    assert clone.agents.keys() == eng.agents.keys()

    for agent_id in eng.agents:
        a = eng.agents[agent_id]
        b = clone.agents[agent_id]

        assert b.id == a.id
        assert b.position == a.position
        assert b.age == a.age
        assert b.energy_level == a.energy_level
        assert b.alive == a.alive
        assert b.offspring_count == a.offspring_count
        # relevant? below? have to check
        assert b.move_rng.bit_generator.state == a.move_rng.bit_generator.state
        assert b.repro_rng.bit_generator.state == a.repro_rng.bit_generator.state
        assert b.energy_rng.bit_generator.state == a.energy_rng.bit_generator.state




@pytest.mark.snapshot
@pytest.mark.validate
def test_restored_engine_matches_original_after_one_step(make_engine, stable_regime, seed_ref, ticks_short) -> None:
    """ test that restored engine matches original after one step. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    

    advance_engine(eng, ticks_short)

    clone = Engine.from_snapshot(eng.get_snapshot())

    eng.step()
    clone.step()

    assert clone.get_state_hash() == eng.get_state_hash()



@pytest.mark.snapshot
@pytest.mark.validate
def test_restored_engine_matches_original_after_many_steps(
    make_engine, stable_regime, seed_ref, ticks_short, ticks_mid
) -> None:
    """ test that restored engine matches original after many steps. """
    eng : Engine = make_engine(seed_ref, stable_regime)
    
    advance_engine(eng, ticks_short)

    clone = Engine.from_snapshot(eng.get_snapshot())

    advance_engine(eng, ticks_mid)
    advance_engine(clone, ticks_mid)

    assert clone.get_state_hash() == eng.get_state_hash()



@pytest.mark.snapshot
@pytest.mark.validate
def test_restored_rng_states_match_original(make_engine, stable_regime, seed_ref, ticks_short):
    eng : Engine = make_engine(seed_ref, stable_regime)
    advance_engine(eng, ticks_short)

    clone : Engine = Engine.from_snapshot(eng.get_snapshot())

    assert clone.world.rng_world.bit_generator.state == eng.world.rng_world.bit_generator.state

    for agent_id in eng.agents:
        a = eng.agents[agent_id]
        b = clone.agents[agent_id]

        assert b.move_rng.bit_generator.state == a.move_rng.bit_generator.state
        assert b.repro_rng.bit_generator.state == a.repro_rng.bit_generator.state
        assert b.energy_rng.bit_generator.state == a.energy_rng.bit_generator.state