# RNG Architecture

## Purpose and Design

This document describes the live seeding and RNG-partition model as of April 8, 2026.

The engine uses a **flat identity-words architecture** rather than a hierarchical per-agent `SeedSequence.spawn()` tree. Each agent derives its three independent RNG streams from:
- deterministic identity tuples (run entropy + genealogy)
- fixed domain tags (movement=1, reproduction=2, energy=3)

This design eliminates the memory overhead of lineage trees while maintaining full determinism and isolation.

## Batch and Run Seeding

### Batch Level

```
batch_seed: int
    ↓
SeedSequence(batch_seed)
    ↓
spawn(n_runs) → [run_ss_0, run_ss_1, ..., run_ss_n]
```

Each run receives an independent `SeedSequence`. This logic is in [engine_build/runner/seeds.py](engine_build/runner/seeds.py).

### Run Level: Master SeedSequence

```
master_ss = run_ss
    ↓
master_ss.entropy: int64 (used for all agents)
    ↓
master_ss.spawn(1)[0] → world_seed
    ↓
default_rng(world_seed) → world.rng_world
```

The `master_ss.entropy` value is **extracted once** and used as a constant across all agent identity derivations in that run.

## Agent RNG Topology

Inside one engine, agents derive RNGs using **identity words + domain tags**:

```text
For each agent:
  identity_words: tuple
    ↓
  PCG64(identity_words + domain_tag) → bit_generator
    ↓
  Generator(bit_generator)  [the live RNG stream]
```

### Founder Identity

A founder agent with `id=founder_id` receives:

```python
identity_words = (master_ss.entropy, founder_id)

move_rng   = Generator(PCG64(identity_words + (MOVEMENT,)))      # domain_tag = 1
repro_rng  = Generator(PCG64(identity_words + (REPRODUCTION,)))  # domain_tag = 2
energy_rng = Generator(PCG64(identity_words + (ENERGY,)))        # domain_tag = 3
```

### Child Identity

A newborn child of parent `parent_id` with parent `offspring_count=k` receives:

```python
child_entropy = parent.repro_rng.bit_generator.random_raw()

identity_words = (master_ss.entropy, child_entropy, parent_id, k)

move_rng   = Generator(PCG64(identity_words + (MOVEMENT,)))
repro_rng  = Generator(PCG64(identity_words + (REPRODUCTION,)))
energy_rng = Generator(PCG64(identity_words + (ENERGY,)))
```

The domain tags are constants defined in [engine_build/core/domains/agent.py](engine_build/core/domains/agent.py):
- `MOVEMENT = 1`
- `REPRODUCTION = 2`
- `ENERGY = 3`

## Stream Isolation and Responsibilities

Each agent maintains **three independent streams** identified by domain tags. This isolation prevents one concern from perturbing another:

### `move_rng` (domain_tag = 1)

- **Founder use**: Sample initial position uniformly from `[0, world_width) × [0, world_height)`
- **Every agent use**: Sample movement direction during movement phase (cardinal move selection)
- **Isolation**: Movement randomness does not affect reproduction probability rolls or energy sampling

### `repro_rng` (domain_tag = 2)

- **Founder use**: Initialized but may not be used until agent reproduces
- **Every agent use**: Bernoulli reproduction roll (does this agent attempt reproduction this tick?)
- **Child creation use**: Generate `child_entropy = repro_rng.bit_generator.random_raw()` for offspring's unique seed
- **Isolation**: Reproduction draws do not consume movement entropy or affect initial-energy draws

### `energy_rng` (domain_tag = 3)

- **Founder use**: Sample initial energy from `[energy_low, energy_high)`
- **Every agent use**: Not used during runtime (initial assignment only)
- **Isolation**: Energy initialization does not affect movement or reproduction draws

### `world.rng_world` (global)

- **Use**: Build fertility landscape via smoothed random noise
- **Timing**: Initialization only (not reused during simulation)
- **Isolation**: World generation does not affect agent-local streams

## Why Isolation Holds

The division follows a strict rule: **one responsibility per stream**.

This prevents subtle bugs:

```
✓ CORRECT:
  move_rng for movement
  repro_rng for reproduction
  energy_rng for energy
  world_rng for world generation

✗ WRONG:
  One shared RNG for [movement + reproduction]
  → reproduction draws consume movement budget
  → movement behavior changes if reproduction policy changes
```

The checked-in regression suite for this is [tests/verification/test_rng_isolation.py](tests/verification/test_rng_isolation.py).

## Snapshot Persistence

Snapshots preserve all RNG state necessary for perfect continuation. Stored RNG state includes:

- `master_ss` metadata: `entropy`, `spawn_key`, `pool_size`
- `world.rng_world.bit_generator.state` (PCG64 state dict)
- **For each live agent**: `move_rng`, `repro_rng`, `energy_rng` bit-generator states

Restoration via [engine_build/core/utils/rng_utils.py::reconstruct_rng](engine_build/core/utils/rng_utils.py) rebuilds:

```python
# Schematic restore
move_rng = Generator(PCG64(bit_generator_state=saved_move_state))
repro_rng = Generator(PCG64(bit_generator_state=saved_repro_state))
energy_rng = Generator(PCG64(bit_generator_state=saved_energy_state))
```

Because RNG states are stored directly, **no per-agent seed lineage object is needed**. This is a key simplification from earlier designs.

## Determinism Contract

Under fixed:
- batch seed
- compiled regime
- code version
- Python + NumPy runtime

The outcomes are:

$$
\text{same batch seed} \xrightarrow{\text{spawn(n)}} \text{same run seeds} \xrightarrow{\text{identity words}} \text{same agent RNG streams}
$$

$$
\xrightarrow{\text{stable phase order + deterministic commits}} \text{identical state trajectory}
$$

Snapshots have an additional guarantee:

$$
\text{snapshot} \xrightarrow{\text{restore RNG states}} \text{continuation-equivalent behavior}
$$

## Design Rationale: Why Flat Identity Words?

### Old design (lineage tree method):

Each agent stored a `SeedSequence` object:
```python
agent.seed_seq = master_ss.spawn(n_siblings)[agent_index]
agent.move_rng = Generator(PCG64(agent.seed_seq.spawn(1)[0]))
```

**Problems:**
- Memory overhead: one SeedSequence object per agent
- Spawn state coupling: each `spawn()` mutates internal counters
- Snapshot complexity: had to preserve lineage topology

### New design (flat identity words):

Each agent computes deterministic identity from tuple + domain tag:
```python
identity = (run_entropy, child_entropy, parent_id, offspring_count)
move_rng = Generator(PCG64(identity + (1,)))
```

**Advantages:**
- Zero object overhead: tuples + PCG64() are lightweight
- No spawn mutations: identity is fully determined, independent of other agents
- Snapshot simplicity: store RNG states, reconstruct on restore
- Genealogy is explicit: parent_id + offspring_count make lineage transparent

## Implementation Considerations

### Why `master_ss.entropy` Works for All Agents

Each run's `master_ss = spawn(n_runs)[run_index]` provides:
- `entropy`: a unique int64 derived from the batch seed
- `spawn_key`, `pool_size`: helper metadata for NumPy's SeedSequence algorithm

The current design:
1. Extract `master_ss.entropy` once at engine start
2. Use this constant for all agent identity derivations in that run
3. Spawn only once (for world_seed), avoiding spawn-counter state mutations

This is valid because:
- `entropy` is already high-entropy (derived from batch seed)
- Identity differentiation comes from `founder_id` or `child_entropy`, not from spawn iteration
- No agent RNG derivation depends on spawn order

### Snapshot Restoration Caveat

When restoring a snapshot:
- RNG bit-generator states are perfectly preserved
- NumPy's internal `SeedSequence.spawn()`  child counter cannot be preserved

This is acceptable because:
- The runtime does **not** call `master_ss.spawn()` after `world_seed` is created
- All subsequent agent RNGs are derived from identity words, not spawn calls
- Spawn counter state is irrelevant to execution correctness

### Determinism Boundaries

Determinism is guaranteed across:
- Same batch seed + regime + code + Python/NumPy runtime

Determinism is **NOT** guaranteed across:
- Different Python versions
- Different NumPy versions (PCG64 algorithm changes)
- Different CPU architectures (floating-point rounding in smoothing kernel)

## Practical Principles

**Add a new random component?** Create a new domain tag and stream. Example:

```python
# DO THIS:
NEW_CONCERN_TAG = 4
new_rng = Generator(PCG64(identity_words + (NEW_CONCERN_TAG,)))

# NOT THIS:
reuse_result = move_rng.random()  # ❌ steals from movement budget
reuse_result = repro_rng.random()  # ❌ steals from reproduction budget
```

**Preserve determinism?** Keep streams isolated. If two systems need randomness, give them separate RNG trees rooted from their concern's domain tag.

**Snapshot a simulation?** All RNG state is captured automatically. Restore will continue precisely where it left off.
