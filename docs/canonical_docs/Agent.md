# Agent

## Status

This document describes the current `Agent` implementation in [engine_build/core/domains/agent.py](engine_build/core/domains/agent.py) as of April 8, 2026.

The agent model is deliberately compact, supporting:

- deterministic execution via isolated RNG streams
- snapshot persistence and restoration
- reproducible batch runs
- the Stage III freeze baseline

## Responsibilities

An agent owns local organism state and agent-local randomness.

Current responsibilities:

- hold position, energy, age, alive state, and offspring count
- derive and own movement / reproduction / energy RNGs
- perform movement
- accept harvested energy
- perform reproduction checks
- age itself

The agent does not own:

- regime compilation
- world resource logic
- batch orchestration
- structural population mutation

Birth and death commits are owned by `Engine`.

## Stored State

Each live agent currently stores:

- `id`
- `engine`
- `position`
- `energy_level`
- `alive`
- `age`
- `offspring_count`
- `move_rng`
- `repro_rng`
- `energy_rng`

Notes:

- `position` is a 2D `(x, y)` tuple
- `offspring_count` participates in deterministic child identity
- RNG streams are intentionally separate by concern

## Initialization

Agent construction follows a deterministic three-step process:

```
identity_words → RNG derivation → state initialization
```

### Identity Model

**No per-agent SeedSequence object is stored.** Instead, each agent is identified by a deterministic tuple:

### Founder Identity

A founder with `id = founder_id` receives:

```python
identity_words = (master_ss.entropy, founder_id)
```

where `master_ss.entropy` is extracted once from the run's `SeedSequence` at engine startup.

### Child Identity

A newborn with parent `parent_id` and parent's `offspring_count = k` receives:

```python
child_entropy = parent.repro_rng.bit_generator.random_raw()

identity_words = (master_ss.entropy, child_entropy, parent_id, k)
```

The child entropy comes from the parent's reproduction RNG, ensuring sibling differentiation.

### RNG Derivation

From identity_words, three independent RNG streams are derived:

```python
move_rng   = Generator(PCG64(identity_words + (MOVEMENT,)))        # domain_tag = 1
repro_rng  = Generator(PCG64(identity_words + (REPRODUCTION,)))    # domain_tag = 2
energy_rng = Generator(PCG64(identity_words + (ENERGY,)))          # domain_tag = 3
```

Domain tags are constants defined in [engine_build/core/domains/agent.py](engine_build/core/domains/agent.py). This architecture is explained in detail in [docs/canonical_docs/RNG_ARCHITECTURE.md](RNG_ARCHITECTURE.md).

This is one of the core determinism mechanisms in the project: identity uniquely determines RNG streams.

### State Initialization

At creation:

- **Founders**: sample initial position from `move_rng` uniformly on the world grid
- **Newborns**: inherit parent's position directly (no position draw)
- `alive = True`
- `age = 0`
- `offspring_count = 0`
- `energy_level` sampled from `[energy_min, energy_max)` using `energy_rng.integers(low, high)`

Notes:
- Energy sampling uses NumPy's `integers(low, high)`, so the upper bound is **exclusive**
- Founders are all created at engine construction time
- Children are created only during commit phase when they receive valid IDs

## Runtime Behavior

### Movement

`move_agent()` applies:

1. subtract `movement_cost`
2. sample one cardinal move
3. update position
4. wrap on the torus
5. if energy is now `<= 0`, set `alive = False` and report failure

Current move set:

```text
(-1, 0), (1, 0), (0, -1), (0, 1)
```

### Harvest

Harvest distribution is computed by `World.harvest()`.

The agent-side method:

```text
agent.harvest_resources(harvest)
```

simply adds the harvested value to `energy_level`.

### Reproduction

Reproduction is split across two methods:

- `can_reproduce()` checks:

```text
energy_level >= reproduction_threshold
```

- `does_reproduce()` draws:

```text
repro_rng.random() < engine.reproduction_probability
```

On success:

- `reproduction_cost` is subtracted immediately from the parent
- the parent is later queued by the biology phase for commit-time birth creation

Child entropy is produced by:

```text
parent.repro_rng.bit_generator.random_raw()
```

### Aging

`age_agent()` applies:

- `age += 1`
- if `age >= max_age`, set `alive = False`

Important current behavior:

- post-harvest survivors always age during the biology phase
- successful reproducers still age in the same tick
- agents queued for `post_reproduction_death` also still pass through `age_agent()` in the current implementation

## Birth and Death Semantics

The agent class only marks or enables transitions. `Engine` performs structural mutation.

### Death paths

The current runtime distinguishes:

- age death
- metabolic death after movement cost
- post-harvest starvation
- post-reproduction death

Important timing detail:

- age-based death is flagged by `age_agent()`
- removal happens on the next tick, when movement phase sees `alive == False`

### Birth path

When a queued parent is committed:

- the engine creates a newborn at `next_agent_id`
- the child starts at the parent position
- the parent's `offspring_count` increments
- `next_agent_id` increments

Births are capacity-limited after queued deaths are counted.

## Snapshot and Canonical State

The agent is part of both canonical hashing and the snapshot layer.

### Canonical hashing

State serialization includes:

- `id`
- `position`
- `energy_level`
- `age`
- `alive`
- `offspring_count`
- `move_rng` state
- `repro_rng` state
- `energy_rng` state

Agents are serialized in ID order for hashing.

### Snapshot restore

`AgentSnapshot` stores:

- `id`
- `agent_spawn_count`
- `position`
- `energy_level`
- `alive`
- `age`
- movement RNG state
- reproduction RNG state
- energy RNG state

`Agent.from_snapshot()` restores the live agent directly from that data.

## Current Invariants

The current implementation asserts:

- `id >= 0`
- the engine reference is present
- position is within world bounds
- `age >= 0`
- `energy_level >= 0` unless the agent is dead
- all three RNGs are valid NumPy generators

Broader engine-level invariants are checked in the verification suite.

## Freeze-Relevant Limits

- there are no explicit agent-agent interaction rules yet beyond shared-cell harvest and competition through the global population cap
- `max_energy` is not used as a runtime clamp on `energy_level`
- local harvest order depends on stable encounter order, not an explicit per-cell sort
- agents do not yet carry traits or inheritance state
