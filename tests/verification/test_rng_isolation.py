import numpy as np
import pytest

from FestinaLente.core.spatial.neighborhood import MoveCandidate

from FestinaLente.core.engine import Engine
from FestinaLente.regimes.compiled import CompiledRegime

# 1 REAL RNG ISOLATION TEST

@pytest.mark.rng
@pytest.mark.verify
def test_move_rng_isolated_from_repro_rng_given_fixed_move_distribution(
    make_engine,
    stable_regime,
    seed_ref,
):
    """ test that movement RNG is isolated from reproduction RNG when movement distribution is fixed. """
    eng_a : Engine = make_engine(seed_ref, stable_regime)
    eng_b : Engine = make_engine(seed_ref, stable_regime)

    agent_a = eng_a.agents[0]
    agent_b = eng_b.agents[0]

    # Keep movement inputs fixed across both agents.
    candidates = [
        MoveCandidate(delta=(0, -1), position=(1, 1), resource_level=10, occupancy_count=0),
        MoveCandidate(delta=(0,  1), position=(2, 2), resource_level=10, occupancy_count=0),
        MoveCandidate(delta=(-1, 0), position=(3, 3), resource_level=10, occupancy_count=0),
        MoveCandidate(delta=(1,  0), position=(4, 4), resource_level=10, occupancy_count=0),
    ]
    probabilities = np.array([0.1, 0.2, 0.3, 0.4], dtype=float)

    # Prevent death from movement cost during repeated draws.
    agent_a.energy_level = 10_000
    agent_b.energy_level = 10_000

    for step in range(100):
        # Deliberately consume reproduction RNG on only one side.
        _ = agent_b.repro_rng.random()

        moved_a = agent_a.move_agent(candidates, probabilities)
        moved_b = agent_b.move_agent(candidates, probabilities)

        assert moved_a == moved_b
        assert agent_a.position == agent_b.position, (
            f"move_rng was affected by repro_rng consumption at step {step}: "
            f"{agent_a.position=} {agent_b.position=}"
        )



# 2 POPULATION-COUPLING INTEGRATION TEST


@pytest.mark.rng
@pytest.mark.verify
@pytest.mark.slow
def test_reproduction_toggle_can_change_base_cohort_paths_under_spatial_crowding(
    make_engine,
    stable_regime : CompiledRegime,
    seed_ref,
    ticks_short,
):
    
    eng1: Engine = make_engine(seed_ref, stable_regime)
    eng2: Engine = make_engine(seed_ref, stable_regime, change_condition=True)

    base_ids = range(stable_regime.population_params.initial_agent_count)

    divergence_found = False

    for _ in range(ticks_short):
        eng1.step()
        eng2.step()

        for agent_id in base_ids:
            if agent_id in eng1.agents and agent_id in eng2.agents:
                if eng1.agents[agent_id].position != eng2.agents[agent_id].position:
                    divergence_found = True
                    break

        if divergence_found:
            break

    assert divergence_found, (
        "Expected reproduction policy toggle to eventually change base-cohort movement "
        "under occupancy-weighted movement, but no divergence was observed."
    )


# NOTE: NEXT TEST TO IMPLEMENT
# def test_base_cohort_paths_remain_equal_when_crowding_weight_is_zero():
# => need to inject weights upstream first


if __name__ == "__main__":
    pytest.main([__file__, "-k", "test_move_rng_isolated_from_repro_rng_given_fixed_move_distribution"])