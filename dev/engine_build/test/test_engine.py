from engine_build.engineP4 import Engine, MAX_AGENT_COUNT
import numpy as np


def snapshot(engine):
    """Lightweight deterministic state representation."""
    return [(a.id, a.position) for a in engine.state]

# test 1 same seed => identical world
def test_same_seed_determinism():
    eng1 = Engine(42, 10)
    eng2 = Engine(42, 10)

    eng1.run(50)
    eng2.run(50)

    assert snapshot(eng1) == snapshot(eng2)
    assert eng1.agent_count == eng2.agent_count



# test 2 agent count limit => no runaway growth
def test_agent_limit():
    eng = Engine(42, 10)
    eng.run(200)

    assert len(eng.state) <= MAX_AGENT_COUNT


# test 3 multiple seeds =>  different worlds
#                           Detects crashes or state corruption.
def test_multiple_seeds():
    for seed in range(5):
        eng = Engine(seed, 5)
        eng.run(30)

        assert len(eng.state) > 0


    

# test 4 position integrity => no floats => Detects RNG bugs.
def test_position_integrity():
    eng = Engine(123, 10)
    eng.run(20)

    for agent in eng.state:
        assert isinstance(agent.position, (int, np.integer))



