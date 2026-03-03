
"""
NOTE: older notes base is still oke

TEST PROTOCOL — Ecosystem Engine

Domains:
1. Determinism
2. Structural Invariants
3. Dynamics Sanity
4. RNG Isolation
5. Identity Stability

Each domain tests a different property of the engine.

-------------------------------------------------------
python -m engine_build.test.test_engine --mode dev

-- mode dev => Development mode → fast, core safety checks
-- mode validate => Validation mode → full system verification
-- mode full => Possibly deep mode → long-horizon + baseline

-- hash ref seed = 42 26304bd3336bd69810062c9ae8311d67a3b7fe6f872ff4fe3b2ea8501a35ba0d
"""
from engine_build.runner.regime_runner import BatchRunner
from engine_build.regimes.registry import get_regime_config
from dataclasses import dataclass
import argparse
import numpy as np

from engine_build.core.engineP4 import Engine

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""


@dataclass(frozen=True)
class TestConfig:
    regime: str = "stable"
    ticks_short: int = 200
    ticks_mid: int = 1000
    ticks_long: int = 5000
    seed_ref: int = 42
    seed_a: int = 1
    seed_b: int = 2

TEST = TestConfig()



# TEST RUNNER
def run_test(test_func):
    try:
        test_func()
        return TestResult(test_func.__name__, True)
    except AssertionError as e:
        return TestResult(test_func.__name__, False, str(e))
    except Exception as e:
        return TestResult(test_func.__name__, False, f"Unexpected error: {e}")



# =========================================================
# 1. DETERMINISM SUITE
# =========================================================

def test_same_seed_determinism():
    regime_config = get_regime_config(TEST.regime)
    runner1 = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    runner2 = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng1, _ = runner1.run_single(runner1.run_seeds[0], TEST.ticks_mid)
    eng2, _ = runner2.run_single(runner2.run_seeds[0], TEST.ticks_mid)
    

    assert eng1 == eng2 , f"Same seed => different worlds. \n |eng1.get_state_hash() = {eng1.get_state_hash()}\n | eng2.get_state_hash() = {eng2.get_state_hash()}"


def test_snapshot_equivalence():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    # run for a short amount of time to create some variability.
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_short)


    

    snapshot = eng.get_snapshot()
    clone = Engine.from_snapshot(snapshot)
    # run for a long time to create some variability.
    for _ in range(TEST.ticks_mid):
        eng.step()
        clone.step()

    assert eng.get_state_hash() == clone.get_state_hash(), f"Snapshot hash equivalence failed. \n |eng.get_state_hash() = {eng.get_state_hash()}\n | clone.get_state_hash() = {clone.get_state_hash()}"


def test_seed_sensitivity():
    regime_config = get_regime_config(TEST.regime)
    runner1 = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_a)
    runner2 = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_b)
    eng1, _ = runner1.run_single(runner1.run_seeds[0], TEST.ticks_mid)
    eng2, _ = runner2.run_single(runner2.run_seeds[0], TEST.ticks_mid)

    assert eng1 != eng2 , f"Seed sensitivity failed. \n |eng1.get_state_hash() = {eng1.get_state_hash()}\n | eng2.get_state_hash() = {eng2.get_state_hash()}"


# =========================================================
# 2. STRUCTURAL INVARIANT SUITE
# =========================================================

def test_spatial_invariants():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)

    for agent in eng.agents.values():
        assert 0 <= agent.position < eng.world_size , f"Agent position out of bounds. | agent.position = {agent.position} | eng.world_size = {eng.world_size}"


def test_resource_bounds():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)

    assert (eng.world.resources >= 0).all() , f"Negative resources found. | eng.world.resources = {eng.world.resources}"
    assert (eng.world.resources <= eng.world.fertility).all() , f"Resources exceed fertility. | eng.world.resources = {eng.world.resources} | eng.world.fertility = {eng.world.fertility}"


def test_identity_monotonicity():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)
    
    ids = sorted(eng.agents.keys())
    # if there are agents, the highest id should be less than the next_agent_id
    if ids:
        assert max(ids) < eng.next_agent_id, f"Identity monotonicity failed. | max(ids) = {max(ids)} | eng.next_agent_id = {eng.next_agent_id}"

    
# =========================================================
# 3. DYNAMICS SANITY SUITE
# =========================================================

def test_population_variability():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    _, metrics = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)

    assert len(set(metrics.population)) > 1 , f"Population variability failed. | len(set(metrics.population)) = {len(set(metrics.population))} | metrics.population = {metrics.population}"
    assert max(metrics.population) <= regime_config.population_config.max_agent_count , f"Population exceeds max_agent_count. | max(metrics.population) = {max(metrics.population)} | regime_config.population_config.max_agent_count = {regime_config.population_config.max_agent_count}"


def test_energy_boundedness():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)

    for agent in eng.agents.values():
        assert agent.energy_level >= 0 , f"Negative energy found. | agent.energy_level = {agent.energy_level}"


# =========================================================
# 4. RNG STREAM ISOLATION SUITE
# =========================================================

def test_movement_rng_isolated_from_reproduction():
    regime_config = get_regime_config(TEST.regime)
    
    seed = TEST.seed_ref
    eng1 = Engine(np.random.SeedSequence(seed), regime_config)
    eng2 = Engine(np.random.SeedSequence(seed), regime_config, change_condition=True)



    # advance and check position of both
    for step in range(TEST.ticks_mid):
        eng1.step()
        eng2.step()
        
        base_ids = range(regime_config.population_config.initial_agent_count)
        
        for i in base_ids:
            if i in eng1.agents and i in eng2.agents:
                assert eng1.agents[i].position == eng2.agents[i].position, (
                    f"Divergence at step {step} for agent {i}"
                )

    # Compare the SAME identities (the original cohort only)
    common_ids = [i for i in base_ids if i in eng1.agents and i in eng2.agents]


    pos1 = [eng1.agents[i].position for i in common_ids]
    pos2 = [eng2.agents[i].position for i in common_ids]

    assert pos1 == pos2, (
        "Movement RNG polluted by reproduction policy toggle."
        f"\n| pos1={pos1}"
        f"\n| pos2={pos2}"
    )

# =========================================================
# 5. REFERENCE BASELINE
# =========================================================

def test_reference_hash():
    regime_config = get_regime_config(TEST.regime)
    runner = BatchRunner(regime_config, n_runs=1, ticks=TEST.ticks_mid, batch_id=TEST.seed_ref)
    eng, _ = runner.run_single(runner.run_seeds[0], TEST.ticks_mid)

    expected_hash = "26304bd3336bd69810062c9ae8311d67a3b7fe6f872ff4fe3b2ea8501a35ba0d"
    assert eng.get_state_hash() == expected_hash , f"Reference hash failed. | eng.get_state_hash() = {eng.get_state_hash()} | expected_hash = {expected_hash}"




# =========================================================


def run_determinism_suite():
    tests = [
        test_same_seed_determinism,
        test_snapshot_equivalence,
        test_seed_sensitivity,
    ]

    results = [run_test(t) for t in tests]

    all_passed = all(r.passed for r in results)

    print("\n=== Determinism Suite ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status} | {r.name}")
        if not r.passed:
            print(f"    -> {r.message}")

    print(f"\nSuite Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed, results

def run_structural_invariant_suite():
    tests = [
        test_spatial_invariants,
        test_resource_bounds,
        test_identity_monotonicity,
    ]

    results = [run_test(t) for t in tests]

    all_passed = all(r.passed for r in results)

    print("\n=== Structural Invariant Suite ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status} | {r.name}")
        if not r.passed:
            print(f"    -> {r.message}")

    print(f"\nSuite Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed, results

def run_dynamics_sanity_suite():
    tests = [
        test_population_variability,
        test_energy_boundedness,
    ]

    results = [run_test(t) for t in tests]

    all_passed = all(r.passed for r in results)

    print("\n=== Dynamics Sanity Suite ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status} | {r.name}")
        if not r.passed:
            print(f"    -> {r.message}")

    print(f"\nSuite Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed, results

def run_rng_isolation_suite():
    tests = [
        test_movement_rng_isolated_from_reproduction,
    ]

    results = [run_test(t) for t in tests]

    all_passed = all(r.passed for r in results)

    print("\n=== RNG Isolation Suite ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status} | {r.name}")
        if not r.passed:
            print(f"    -> {r.message}")

    print(f"\nSuite Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed, results

def run_reference_baseline_suite():
    tests = [
        test_reference_hash,
    ]

    results = [run_test(t) for t in tests]

    all_passed = all(r.passed for r in results)

    print("\n=== Reference Baseline Suite ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status} | {r.name}")
        if not r.passed:
            print(f"    -> {r.message}")

    print(f"\nSuite Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed, results

def run_dev_mode():
    print("\n=== DEVELOPMENT MODE ===")
    core_ok = True

    det_ok, _ = run_determinism_suite()
    inv_ok, _ = run_structural_invariant_suite()

    core_ok = det_ok and inv_ok

    print("\nDEV MODE RESULT:", "PASS" if core_ok else "FAIL")
    

def run_validation_mode():
    print("\n=== VALIDATION MODE ===")

    det_ok, _ = run_determinism_suite()
    inv_ok, _ = run_structural_invariant_suite()
    dyn_ok, _ = run_dynamics_sanity_suite()
    rng_ok, _ = run_rng_isolation_suite()


    all_ok = det_ok and inv_ok and dyn_ok and rng_ok

    print("\nVALIDATION RESULT:", "PASS" if all_ok else "FAIL")

def run_full_mode():
    print("\n=== FULL SYSTEM VALIDATION ===")

    det_ok, _ = run_determinism_suite()
    inv_ok, _ = run_structural_invariant_suite()
    dyn_ok, _ = run_dynamics_sanity_suite()
    rng_ok, _ = run_rng_isolation_suite()
    ref_ok, _ = run_reference_baseline_suite()

    all_ok = det_ok and inv_ok and dyn_ok and rng_ok and ref_ok

    print("\nFULL VALIDATION RESULT:", "PASS" if all_ok else "FAIL")

def main():
    
    parser = argparse.ArgumentParser(description="Ecosystem Engine Determinism Test")

    parser.add_argument(
        "--mode",
        choices=["dev", "validate", "full"],
        default="dev",
        help="Select test mode"
    )

    args = parser.parse_args()

    if args.mode == "dev":
        run_dev_mode()
    elif args.mode == "validate":
        run_validation_mode()
    elif args.mode == "full":
        run_full_mode()


if __name__ == "__main__":
    main()
    