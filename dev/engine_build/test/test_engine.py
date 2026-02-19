from engine_build.engineP4 import Engine, MAX_AGENT_COUNT
import numpy as np

"""
Testing plan: 

need to test for 3 critical invariants: 
    - Seed → Lineage → State → Hash


def test_same_seed()
def test_different_seed()
def test_snapshot()
def test_forward_clone()
def test_reference_trajectory()
def test_long_horizon()



"""
# testing ranges
T_mid = 250
T_tail = 250
Total = 500
N_agents = 10


def test_same_seed_determinism_suite(seed : np.int64) -> str:
    """ verify determinism for diff engines with the same seed """
    eng1 = Engine(seed, N_agents)
    eng2 = Engine(seed, N_agents)

    eng1.run(T_mid)
    eng2.run(T_mid)

    status = "PASSED" if eng1 == eng2 else "FAILED"

    print("================================================================")
    print("Testing Same Seed => Identical World...")
    print(f"for seed = {seed} || T = {T_mid}")
    print(f"test_same_seed_determinism: {status}")
    print("================================================================")

    return status


# canonical determinism suite (PRIMARY)
def test_canonical_determinism_suite(seed : np.int64, full_trajectory : bool = False) -> str:
    """ Verify trajectory equivalence for mid run interruption, cloning and continuation. """

    eng1 = Engine(seed, N_agents)
    eng1.run(T_mid)

    snapshot = eng1.get_snapshot()

    clone = Engine.from_snapshot(snapshot)
    clone.run(T_tail)

    eng1.run(T_tail)


    if not full_trajectory:
        status = "PASSED" if eng1 == clone else "FAILED"
    else:
        eng2 = Engine(seed, N_agents)
        eng2.run(T_mid + T_tail)
        status = "PASSED" if eng1 == clone and eng1 == eng2 else "FAILED"

    print("================================================================")
    print("Testing Canonical Determinism...")
    print(f"full_trajectory: {full_trajectory}")
    print(f"for seed = {seed}")
    print(f"|| T_mid = {T_mid} || T_tail = {T_tail} || T_total = {Total}")
    print("\n")
    print(f"test_canonical_determinism: {status}")
    print("================================================================")

    return status


# Snapshot Idempotence 
def test_snapshot_idempotence_suite(seed : np.int64) -> str:
    """ Verify that snapshotting an engine does not change its state. And snapshot is restorable. """
    
    """ CAVE => This isolates reconstruction correctness from forward evolution."""
    
    
    eng = Engine(seed, N_agents)
    eng.run(T_mid)

    snapshot_1 = eng.get_snapshot()
    clone = Engine.from_snapshot(snapshot_1)


    clone_status = "PASSED" if eng == clone else "FAILED"

    print("================================================================")
    print("Testing Snapshot Idempotence...")
    print(f"for seed = {seed}")
    print(f"|| T = {T_mid}")
    print("\n")
    
    print(f"test_clone_from_snapshot: {clone_status}")
    print("================================================================")

    

    return clone_status


# Multi-Clone Consistency
def test_multi_clone_consistency_suite(seed : np.int64) -> str:
    """ Verify that multiple clones of the same snapshot are equivalent. """

    """ CAVE => CATCHES SUBTLE REFERENCE BUGS"""
    eng = Engine(seed, N_agents)
    eng.run(T_mid)

    snapshot = eng.get_snapshot()

    clone_1 = Engine.from_snapshot(snapshot)
    clone_2 = Engine.from_snapshot(snapshot)

    status = "PASSED" if clone_1 == clone_2 else "FAILED"

    print("================================================================")
    print("Testing Multi-Clone Consistency...")
    print(f"for seed = {seed}")
    print(f"T at snapshot: {T_mid}")
    print(f"|| T = {Total}")
    print("\n")
    print(f"test_multi_clone_consistency: {status}")
    print("================================================================")

    return status

# seed sensitivity
def test_seed_sensitivity_suite(seed_1 : np.int64, seed_2 : np.int64) -> str:
    """ Verify that different seeds produce different worlds. """
    eng1 = Engine(seed_1, N_agents)
    eng2 = Engine(seed_2, N_agents)

    eng1.run(Total)
    eng2.run(Total)

    status = "PASSED" if eng1 != eng2 else "FAILED"

    print("================================================================")
    print("Testing Seed Sensitivity...")
    print(f"for seed_1 = {seed_1} and seed_2 = {seed_2}")
    print(f"|| T = {Total}")
    print("\n")
    print(f"test_seed_sensitivity: {status}")
    print("================================================================")

    return status

## NOTE: next 2 tests to implement 

### 1) RNG Stream Independence Test 

''' Verify stream separation.
NOTE: 
        - MEDIUM PRIORITY => check change_condition logic first! 

Example:

        Engine(seed, change_condition=False)
        Engine(seed, change_condition=True)


        Compare movement-only fields.
        
        
'''

### 2) Identity stability test. 
"""
    Purpose:

            Verify ID monotonicity under creation/deletion (future).

            Later when you add death.
"""




if __name__ == "__main__":
    test_canonical_determinism_suite(42, full_trajectory=True)
    