import pytest

from engine_build.regimes.compiled import CompiledRegime

from engine_build.core.engineP4 import Engine


@pytest.mark.rng
@pytest.mark.validate
@pytest.mark.slow
def test_movement_rng_isolated_from_reproduction(
    make_engine,
    stable_regime : CompiledRegime,
    seed_ref  : int,
    ticks_mid : int,
):
    """ test that movement rng is isolated from reproduction rng. """
    eng1: Engine = make_engine(seed_ref, stable_regime)
    eng2: Engine = make_engine(seed_ref, stable_regime, change_condition=True)

    base_ids = range(stable_regime.population_params.initial_agent_count)

    for step in range(ticks_mid):
        eng1.step()
        eng2.step()

        for agent_id in base_ids:
            if agent_id in eng1.agents and agent_id in eng2.agents:
                assert eng1.agents[agent_id].position == eng2.agents[agent_id].position, (
                    f"Movement RNG polluted by reproduction policy toggle "
                    f"at step {step} for agent {agent_id}. "
                    f"| pos1={eng1.agents[agent_id].position} "
                    f"| pos2={eng2.agents[agent_id].position}"
                )

    common_ids = [
        agent_id for agent_id in base_ids
        if agent_id in eng1.agents and agent_id in eng2.agents
    ]

    pos1 = [eng1.agents[agent_id].position for agent_id in common_ids]
    pos2 = [eng2.agents[agent_id].position for agent_id in common_ids]

    assert pos1 == pos2, (
        "Movement RNG polluted by reproduction policy toggle in final cohort comparison. "
        f"| common_ids={common_ids} "
        f"| pos1={pos1} "
        f"| pos2={pos2}"
    )