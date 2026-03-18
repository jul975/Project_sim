# RNG Architecture

## Purpose

This document describes how randomness is seeded, partitioned, and restored in the current engine.

The current implementation is not the older per-agent `SeedSequence.spawn()` tree model. Agent RNGs are now derived from deterministic identity words plus fixed domain tags.

## Topology

At batch level, the runner derives per-run seeds from a batch seed:

```text
batch seed (int)
-> SeedSequence(batch seed)
-> spawn(n_runs)
-> one run SeedSequence per Engine
```

Inside a single engine:

```text
master_ss = run SeedSequence
|
+-- world_seed = master_ss.spawn(1)[0]
|   +-- world.rng_world = default_rng(world_seed)
|
+-- founder identity words = (master_ss.entropy, founder_id)
|   +-- move_rng   = Generator(PCG64(identity_words + (1,)))
|   +-- repro_rng  = Generator(PCG64(identity_words + (2,)))
|   +-- energy_rng = Generator(PCG64(identity_words + (3,)))
|
+-- child identity words = (master_ss.entropy, child_entropy, parent_id, parent.offspring_count)
    +-- move_rng   = Generator(PCG64(identity_words + (1,)))
    +-- repro_rng  = Generator(PCG64(identity_words + (2,)))
    +-- energy_rng = Generator(PCG64(identity_words + (3,)))
```

Domain tags are defined in `engine_build/core/agent.py`:

- `MOVEMENT = 1`
- `REPRODUCTION = 2`
- `ENERGY = 3`

## Stream Responsibilities

- `world.rng_world`
  - used for fertility-field generation in `World._generate_fertility_fields()`
  - world regrowth is currently deterministic and does not draw randomness
- `agent.move_rng`
  - used for founder initial positions
  - used for subsequent movement direction draws
- `agent.repro_rng`
  - used for reproduction Bernoulli draws
  - used to generate `child_entropy` through `bit_generator.random_raw()`
- `agent.energy_rng`
  - used for initial energy assignment at creation

Newborns inherit the parent's position, so they do not consume a movement draw during initialization.

## Deterministic Agent Identity

Founders and newborns are keyed differently:

- founder identity: `(run_entropy, founder_id)`
- child identity: `(run_entropy, child_entropy, parent_id, parent.offspring_count)`

This gives the engine:

- deterministic sibling ordering through `offspring_count`
- deterministic child differentiation through `child_entropy`
- stream isolation through domain tags

The engine no longer stores a `SeedSequence` lineage object on each agent.

## Why Isolation Holds

The key isolation rule is one stream per behavioral domain.

That means:

- movement draws do not consume reproduction entropy
- reproduction draws do not perturb initial-energy sampling
- world generation does not perturb agent-local streams

The checked-in isolation regression is `tests/verification/test_rng_isolation.py`, which verifies that changing reproduction probability does not change movement trajectories for shared surviving founders.

## Snapshot and Restore

Snapshots persist the RNG data needed for continuation:

- `master_ss` metadata: `entropy`, `spawn_key`, `pool_size`
- `world.rng_world.bit_generator.state`
- each agent's `move_rng`, `repro_rng`, and `energy_rng` bit-generator state

Restore reconstructs generators directly from saved bit-generator state in `engine_build/core/rng_utils.py`.

Because agent RNGs are identity-word based, snapshots do not need per-agent seed-lineage metadata beyond the live generator states.

## Determinism Implications

Under fixed seed, regime, code, and runtime:

- the same batch seed produces the same run-seed panel
- the same run seed produces the same world RNG stream
- the same founder and child identities produce the same agent RNG streams
- snapshot restore produces continuation-equivalent RNG behavior

## Current Limits

- Snapshot restoration does not preserve NumPy's internal `SeedSequence` child counter. This is acceptable for the current engine because the post-initialization runtime no longer depends on repeated `master_ss.spawn()` calls after the world seed is created.
- RNG behavior is coupled to NumPy's PCG64 state format. Library or version changes can break byte-identical replay.
- Local resource-sharing order depends on stable runtime traversal order, not on an explicit per-cell sort.
- Agent identity currently uses `master_ss.entropy`, not the full run `SeedSequence` identity. Distinct spawned run seeds from the same batch therefore share founder-local agent RNG states; cross-run variation currently comes from the world seed and downstream interactions.

## Practical Rule

If a new behavior needs randomness, give it its own stream. Do not reuse `move_rng`, `repro_rng`, `energy_rng`, or `rng_world` for a second concern.
