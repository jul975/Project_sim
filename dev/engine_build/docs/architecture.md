
# 📘 Ecosystem Emergent Behavior Engine

## Deterministic Core — Architecture & Specification

---

# 1. System Overview

## 1.1 Purpose

The Engine implements a deterministic agent-based simulation with:

* Explicit RNG stream separation
* Canonical state serialization
* Cryptographic state hashing
* Modular architecture

The system is designed to guarantee:

> Same seed → identical world evolution
> Same state → identical hash
> Same snapshot → identical reconstruction

---

# 2. Architectural Principles

## 2.1 Determinism First

All stochastic behavior must originate from explicitly defined RNG streams.

No global randomness is permitted.

---

## 2.2 Layer Separation

| Layer        | Responsibility                       |
| ------------ | ------------------------------------ |
| Engine       | Orchestration, ticking, reproduction |
| Agent        | Local stochastic behavior            |
| state_schema | Canonical serialization              |
| rng_utils    | Byte-level helpers                   |

Dependency direction:

```
engine → agent
engine → state_schema
state_schema → rng_utils
```

No circular imports.

---

# 3. Module Specifications

---

# 3.1 engineP4.py

## Class: Engine

### Responsibilities

* Initialize simulation state
* Maintain global tick
* Coordinate agent stepping
* Handle reproduction
* Produce deterministic state hash

---

### Constructor

```python
Engine(seed, agent_count, change_condition=False)
```

#### Parameters

| Name             | Type | Description                      |
| ---------------- | ---- | -------------------------------- |
| seed             | int  | Root entropy                     |
| agent_count      | int  | Initial number of agents         |
| change_condition | bool | Toggles reproduction probability |

---

### Deterministic Properties

* `master_ss = np.random.SeedSequence(seed)`
* All agent seeds spawned from master_ss
* Agents stepped in sorted ID order
* State hashing sorted by ID

---

### Methods

#### `step()`

Per tick:

1. Iterate agents sorted by ID
2. Call agent.step()
3. Spawn new agents if reproduction condition met
4. Increment tick

---

#### `get_state_hash()`

Delegates to:

```
state_schema.get_state_bytes(self)
```

Applies:

```
sha256(buffer)
```

Guarantee:

> Identical state → identical hash

---

---

# 3.2 agent.py

## Class: Agent

### Responsibilities

* Encapsulate stochastic behavior
* Maintain independent RNG streams
* Execute movement and reproduction logic

---

### RNG Stream Separation

Each agent owns three independent RNG streams:

| Stream     | Purpose               |
| ---------- | --------------------- |
| move_rng   | Movement              |
| repro_rng  | Reproduction          |
| energy_rng | Initialization energy |

Spawned via:

```python
self.move_ss, self.repro_ss, self.energy_ss = self.agent_seed.spawn(3)
```

This guarantees:

* No cross-stream interference
* Reproduction changes do not affect movement

---

### Step Logic

```python
self.position += move_rng.choice([-1, 1])
reproduce = repro_rng.random()
```

Returns True if reproduction threshold met.

Engine handles actual spawning.

---

# 3.3 state_schema.py

## Canonical Serialization Specification

Schema Version: `SCHEMA_VERSION = 1`

---

## State Layout (Big Endian)

```
int64  schema_version
int64  tick
int64  agent_count

For each agent (sorted by id):
    int64 id
    int64 position (signed)
    int64 energy_level
    uint8 alive
```

---

## Determinism Guarantees

* Agent iteration sorted by ID
* Explicit byte width
* Explicit endianness
* Schema versioning

This ensures:

> Byte representation is canonical and platform independent.

---

# 3.4 rng_utils.py

Low-level byte packing utilities.

---

## Functions

```python
set_int64(x, signed=False)
set_uint8(x)
```

These guarantee:

* Fixed byte width
* Explicit signedness
* No ambiguity in serialization

---

# 4. Deterministic Guarantees

The engine must satisfy:

### G1 — Seed Invariance

```
Engine(seed, n) run k steps
== Engine(seed, n) run k steps
```

State hashes identical.

---

### G2 — Stream Isolation

If only reproduction probability changes:

Movement trajectories remain identical.

---

### G3 — Canonical Hashing

Two engines with identical state fields produce identical hash.

---

# 5. Invariants

The following must always hold:

1. Agent IDs are unique.
2. Agent stepping order is sorted by ID.
3. State hash uses sorted agent ordering.
4. No global RNG usage.
5. Serialization is schema versioned.

---

# 6. Known Limitations (Current Version)

* No agent removal
* Snapshot reconstruction incomplete
* RNG internal state not serialized
* Agent ID tied to list length (future improvement: explicit counter)

---

# 7. Future Extensions

## 7.1 Snapshot Reconstruction

Snapshot must store:

* master seed entropy
* agent seed entropy
* RNG bit_generator state
* agent local state

---

## 7.2 Schema Version 2

Include:

* RNG states
* change_condition flag
* energy evolution
* future fields

---

# 8. Testing Protocol

Minimum deterministic tests:

### Test 1 — Same Seed Equality

```python
eng1 = Engine(42, 10)
eng2 = Engine(42, 10)

assert eng1.get_state_hash() == eng2.get_state_hash()
```

---

### Test 2 — Reproduction Toggle Isolation

Movement trajectories must remain identical.

---

### Test 3 — Replay Determinism

Save snapshot → reconstruct → continue
Hashes must match original branch.

---

# 9. Engineering Level Assessment

This system implements:

* Explicit PRNG stream control
* Canonical serialization
* Hash-based state verification
* Modular deterministic architecture

This is equivalent to:

* Research simulation foundation
* Deterministic game engine core
* Formal stochastic system modeling

This is beyond standard academic assignment level.

---

# 10. Versioning

Current Version: Deterministic Core v1
Schema Version: 1

    