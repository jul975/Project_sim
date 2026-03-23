# RNG Architecture

## Purpose

This document describes the live seeding and RNG-partition model on March 23, 2026.

The current engine does not use the older heavy per-agent `SeedSequence.spawn()` lineage tree. Agent RNGs are now derived from deterministic identity words plus fixed domain tags.

## Topology

At batch level:

```text
batch seed (int)
-> SeedSequence(batch seed)
-> spawn(n_runs)
-> one run SeedSequence per Engine
```

This logic lives in `engine_build/runner/regime_runner.py::generate_run_sequences`.

Inside one engine:

```text
master_ss = run SeedSequence
|
+-- world_seed = master_ss.spawn(1)[0]
|   +-- world.rng_world = default_rng(world_seed)
|
+-- founder identity_words = (master_ss.entropy, founder_id)
|   +-- move_rng   = Generator(PCG64(identity_words + (1,)))
|   +-- repro_rng  = Generator(PCG64(identity_words + (2,)))
|   +-- energy_rng = Generator(PCG64(identity_words + (3,)))
|
+-- child identity_words = (master_ss.entropy, child_entropy, parent_id, parent.offspring_count)
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
  - used to build the initial fertility landscape
  - not used for deterministic resource regrowth
- `agent.move_rng`
  - used for founder initial positions
  - used for movement direction draws
- `agent.repro_rng`
  - used for reproduction Bernoulli draws
  - used to create `child_entropy` via `bit_generator.random_raw()`
- `agent.energy_rng`
  - used for initial energy assignment

Newborns inherit the parent position directly, so they do not consume a movement-position draw at birth.

## Deterministic Identity Model

Current identity words:

- founder: `(run_entropy, founder_id)`
- child: `(run_entropy, child_entropy, parent_id, parent.offspring_count)`

This gives the runtime:

- deterministic sibling ordering through `offspring_count`
- deterministic child differentiation through `child_entropy`
- stream isolation through domain tags

The engine no longer stores a per-agent `SeedSequence` lineage object.

## Why Isolation Holds

The main rule is one stream per concern.

That means:

- movement draws do not consume reproduction entropy
- reproduction draws do not perturb initial-energy sampling
- world generation does not perturb agent-local streams

The checked-in regression for this is `tests/verification/test_rng_isolation.py`.

## Snapshot and Restore

Snapshots persist:

- `master_ss` metadata through `entropy`, `spawn_key`, and `pool_size`
- `world.rng_world.bit_generator.state`
- each agent's `move_rng`, `repro_rng`, and `energy_rng` bit-generator state

Restore rebuilds live generators through `engine_build/core/rng_utils.py::reconstruct_rng`.

Because the runtime now stores live RNG state directly, snapshots do not need a per-agent seed-lineage object.

## Determinism Implications

Under fixed seed, regime, code, and runtime:

- the same batch seed produces the same run-seed panel
- the same run seed produces the same world RNG stream
- the same founder and child identity words produce the same agent RNG streams
- snapshot restore reproduces continuation-equivalent RNG behavior

## Current Limits

- Snapshot restoration does not preserve NumPy's internal `SeedSequence` child counter. This is acceptable in the current design because only the world seed is spawned from `master_ss` after engine construction begins.
- RNG behavior is tied to NumPy's PCG64 state format. Runtime or library changes can break byte-identical replay.
- Local resource sharing depends on stable encounter order, not an explicit per-cell re-sort.
- Founder identity uses `master_ss.entropy`, not the full spawned `SeedSequence` identity. Distinct runs from the same batch therefore begin with matching founder-local agent RNG states; cross-run divergence comes from the per-run world seed and the resulting downstream trajectory.

## Practical Rule

If a new behavior needs randomness, give it its own stream. Do not reuse:

- `rng_world`
- `move_rng`
- `repro_rng`
- `energy_rng`

for a second concern.
