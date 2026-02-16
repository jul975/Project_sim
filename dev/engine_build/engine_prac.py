"""
Problem 2 — Multi-Agent Random Walk (Order Sensitivity)

Objective
---------
Simulate N agents moving on a 1D line.

Global system state:

    S(t) = { position_i(t) } for i in {1,...,N}

Each timestep:

    position_i(t+1) = position_i(t) + δ_i(t)

where:

    δ_i(t) ∈ {-1, +1}

Direction is chosen randomly.


Required Constraints
--------------------
1. Use ONE master RNG at the engine level.
2. No global random usage.
3. No per-agent RNG instances.
4. Deterministic agent iteration order.
5. run(seed, steps) must be reproducible.


Required Experiments
--------------------

Experiment 1 — Determinism

    Engine(seed=42, N=5).run(100)
    Engine(seed=42, N=5).run(100)

Expected:
    Identical final positions.


Experiment 2 — Order Sensitivity

Change agent iteration order
(e.g., reverse iteration or shuffle once).

Run again with the same seed.

Expected:
    Entire trajectory diverges.


Experiment 3 — Artificial Synchrony

Give each agent its own RNG:

    agent.rng = np.random.default_rng(seed)

Expected:
    All agents move identically (perfect synchrony).

This demonstrates that identical per-agent seeding
destroys independence.


What This Problem Teaches
-------------------------

1. RNG call order is part of the world state.
2. Changing iteration order changes RNG consumption order.
3. Per-agent seeding with identical seeds creates correlated behavior.
4. Deterministic simulation requires:
       - Same seed
       - Same call order
       - Same number of RNG calls


Questions You Must Be Able To Answer
------------------------------------

1. What is S(t)?
2. What is r(t)?
3. How many RNG calls happen per tick?
4. What changes call order?
5. Why does shuffling cause divergence?


Goal
----
Understand that (S(t), r(t)) is a coupled deterministic system.
"""