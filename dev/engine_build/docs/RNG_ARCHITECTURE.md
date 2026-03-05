# RNG Architecture

## Purpose
This document defines how randomness is generated, partitioned, and restored in the ecosystem engine.

Primary goals:
- deterministic replay from `(seed, config, code_version)`
- stream isolation between subsystems
- stable lineage for agent descendants
- snapshot-safe RNG restoration

## RNG Topology
The engine uses NumPy `SeedSequence` lineage and `default_rng` (PCG64).

```text
master_ss (Engine)
+-- world_ss = master_ss.spawn(1)[0]
|   +-- rng_world (World)
|
+-- agent_ss[i] = master_ss.spawn(initial_agent_count)[i]
    +-- move_ss, repro_ss, energy_ss = agent_ss[i].spawn(3)
        +-- move_rng   (movement decisions)
        +-- repro_rng  (reproduction draw)
        +-- energy_rng (initial energy only)
```

## Stream Ownership
- `world.rng_world`: world initialization (`fertility`) and world-level stochasticity.
- `agent.move_rng`: movement step (`choice([-1, 1])`).
- `agent.repro_rng`: reproduction Bernoulli draw (`random() < p`).
- `agent.energy_rng`: initial energy sampling at agent creation.

Each concern has its own stream to prevent cross-contamination.

## Initialization Flow
1. Engine receives `master_ss`.
2. Engine spawns one world seed and `N` agent seeds.
3. World is initialized from `world_ss`.
4. Each agent splits its seed into 3 substreams (`move`, `repro`, `energy`).

## Reproduction Lineage
Child seeds are deterministic descendants of the parent seed identity:

```text
child_spawn_key = parent_spawn_key + (parent.agent_spawn_count,)
child_seed = SeedSequence(entropy=parent_entropy, spawn_key=child_spawn_key, pool_size=parent_pool_size)
parent.agent_spawn_count += 1
```

Implication:
- sibling ordering is stable
- replayed runs generate the same descendant seed tree

## Snapshot and Restore
Snapshots store RNG state at two levels:
- seed metadata (`entropy`, `spawn_key`, `pool_size`, `agent_spawn_count`)
- full bit-generator states for `rng_world`, `move_rng`, `repro_rng`, `energy_rng`

Restore reconstructs:
- generators from stored bit-generator states
- seed lineage using stored seed metadata

This allows mid-run clone/restart with deterministic continuation.

## Determinism and Isolation Contract
Contract enforced by architecture and tests:
- same seed + same config => identical state hash trajectory
- different seeds => divergent trajectory
- reproduction policy changes do not alter movement trajectories of shared surviving IDs

Reference implementation checks this in `test_movement_rng_isolated_from_reproduction`.

## Operational Rules
- never reuse one RNG stream for multiple behavioral domains
- keep agent iteration order stable (`sorted(agent_ids)`)
- include all RNG states in canonical state serialization
- treat RNG API changes (NumPy/bit-generator) as determinism-impacting

## Current Limitation
NumPy does not expose `SeedSequence.n_children_spawned` for exact restoration. The engine emulates child progression via `agent_spawn_count` in spawn-key extension. This preserves engine-level lineage determinism, but is not a byte-identical reconstruction of NumPy internal `SeedSequence` counters.
