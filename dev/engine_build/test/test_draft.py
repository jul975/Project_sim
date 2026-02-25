"""
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

import numpy as np
from engine_build.engineP4 import Engine
from engine_build.config import SimulationConfig
from dataclasses import dataclass
import argparse

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""

BASE_CONFIG = SimulationConfig()
SEED = 42
T_SHORT = 100
T_MEDIUM = 500
T_LONG = 2000
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
    eng1 = Engine(SEED, BASE_CONFIG)
    eng2 = Engine(SEED, BASE_CONFIG)

    eng1.run(T_MEDIUM)
    eng2.run(T_MEDIUM)

    assert eng1 == eng2 , f"Same seed => different worlds. \n |eng1.get_state_hash() = {eng1.get_state_hash()}\n | eng2.get_state_hash() = {eng2.get_state_hash()}"


def test_snapshot_equivalence():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_MEDIUM)

    snapshot = eng.get_snapshot()
    clone = Engine.from_snapshot(snapshot)

    assert eng == clone, f"Snapshot equivalence failed. \n |eng.get_state_hash() = {eng.get_state_hash()}\n | clone.get_state_hash() = {clone.get_state_hash()}"


def test_seed_sensitivity():
    eng1 = Engine(1, BASE_CONFIG)
    eng2 = Engine(2, BASE_CONFIG)

    eng1.run(T_MEDIUM)
    eng2.run(T_MEDIUM)

    assert eng1 != eng2 , f"Seed sensitivity failed. \n |eng1.get_state_hash() = {eng1.get_state_hash()}\n | eng2.get_state_hash() = {eng2.get_state_hash()}"



# =========================================================
# 2. STRUCTURAL INVARIANT SUITE
# =========================================================

def test_spatial_invariants():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_LONG)

    for agent in eng.agents.values():
        assert 0 <= agent.position < eng.world_size , f"Agent position out of bounds. | agent.position = {agent.position} | eng.world_size = {eng.world_size}"


def test_resource_bounds():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_LONG)

    assert (eng.world.resources >= 0).all() , f"Negative resources found. | eng.world.resources = {eng.world.resources}"
    assert (eng.world.resources <= eng.world.fertility).all() , f"Resources exceed fertility. | eng.world.resources = {eng.world.resources} | eng.world.fertility = {eng.world.fertility}"


def test_identity_monotonicity():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_LONG)
    
    ids = sorted(eng.agents.keys())
    # if there are agents, the highest id should be less than the next_agent_id
    if ids:
        assert max(ids) < eng.next_agent_id, f"Identity monotonicity failed. | max(ids) = {max(ids)} | eng.next_agent_id = {eng.next_agent_id}"

    



# =========================================================
# 3. DYNAMICS SANITY SUITE
# =========================================================

def test_population_variability():
    eng = Engine(SEED, BASE_CONFIG)
    metrics = eng.run_with_metrics(T_MEDIUM)

    assert len(set(metrics.population)) > 1 , f"Population variability failed. | len(set(metrics.population)) = {len(set(metrics.population))} | metrics.population = {metrics.population}"
    assert max(metrics.population) <= BASE_CONFIG.max_agent_count , f"Population exceeds max_agent_count. | max(metrics.population) = {max(metrics.population)} | BASE_CONFIG.max_agent_count = {BASE_CONFIG.max_agent_count}"


def test_energy_boundedness():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_MEDIUM)

    for agent in eng.agents.values():
        assert agent.energy_level >= 0 , f"Negative energy found. | agent.energy_level = {agent.energy_level}"


# =========================================================
# 4. RNG STREAM ISOLATION SUITE
# =========================================================

def test_movement_rng_isolated_from_reproduction():
    eng1 = Engine(SEED, BASE_CONFIG, change_condition=False)
    eng2 = Engine(SEED, BASE_CONFIG, change_condition=True)

    eng1.run(T_MEDIUM)
    eng2.run(T_MEDIUM)

    # Compare the SAME identities (the original cohort only)
    base_ids = range(BASE_CONFIG.initial_agent_count)
    common_ids = [i for i in base_ids if i in eng1.agents and i in eng2.agents]

    pos1 = [eng1.agents[i].position for i in common_ids]
    pos2 = [eng2.agents[i].position for i in common_ids]

    assert pos1 == pos2, (
        "Movement RNG not isolated from reproduction (base cohort differs). "
        f"| pos1={pos1} | pos2={pos2}"
    )

# =========================================================
# 5. REFERENCE BASELINE
# =========================================================

def test_reference_hash():
    eng = Engine(SEED, BASE_CONFIG)
    eng.run(T_MEDIUM)

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
    parser = argparse.ArgumentParser(description="Ecosystem Engine Test Runner")

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
    