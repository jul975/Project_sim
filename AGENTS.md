# AGENTS.md — Working with FestinaLente

## Project Foundation

This is a **deterministic ecosystem simulator** — a research-grade tool for reproducible multi-agent simulations on a 2D toroidal world.

The codebase is organized for **clarity, testability, and deterministic reproducibility**, not convenience or performance tricks.

**Above all: Preserve determinism.** This is non-negotiable. When in doubt, choose the approach that keeps results reproducible.

## Core Architectural Principles

### Separation of Concerns

- **Engine layer** (`core/engine.py`, `core/transitions.py`): orchestration and phase stepping only
- **Model layer** (`core/domains/`, `regimes/`): ecology logic, regime compilation, agent behavior
- **Analytics layer** (`analytics/`, `runner/`): metrics collection, summaries, classification
- **Tests** (`tests/verification/`, `tests/validation/`): verification and validation as distinct workflows

**Rule**: Do not move ecology logic into orchestration, or analytics into simulation logic. No exceptions.

### RNG Architecture (Critical)

**No per-agent SeedSequence lineage trees.** Agents derive RNGs from flat identity words:

```python
# Founder
identity_words = (master_ss.entropy, founder_id)

# Child
identity_words = (master_ss.entropy, child_entropy, parent_id, parent.offspring_count)

# Each agent gets three domains
move_rng   = Generator(PCG64(identity_words + (1,)))  # movement direction
repro_rng  = Generator(PCG64(identity_words + (2,)))  # reproduction Bernoulli  
energy_rng = Generator(PCG64(identity_words + (3,)))  # initial energy
```

**Domain tags are fixed constants** (`MOVEMENT=1`, `REPRODUCTION=2`, `ENERGY=3` in `core/domains/agent.py`). Do not share streams between domains.

See [docs/canonical_docs/RNG_ARCHITECTURE.md](docs/canonical_docs/RNG_ARCHITECTURE.md) for full detail.

### The TransitionContext Pattern

Phases do not mutate engine state directly. Instead:

1. **Phase** evaluates conditions → appends to intermediate buckets (TransitionContext)
2. **Commit** atomically applies all changes: deaths → births → regrowth

Benefits: isolated phase logic, trackable cause-of-death, deterministic commit order.

See [ARCHITECTURE.md](docs/canonical_docs/ARCHITECTURE.md#transition-layer-phase-separation) for diagram.

### Tick Order (Immutable)

```
movement → interaction → biology → commit → tick += 1
```

**Do not reorder.** Do not conditionally skip phases. This order is tested and documented.

Movement phase includes:
- Age entry-check (agents ≥ max_age queued for death)
- Direction sampling + movement
- Metabolic death if energy ≤ 0

See [MATHEMATICAL_MODEL.md](docs/canonical_docs/MATHEMATICAL_MODEL.md) sections 5-8 for formal definitions.

## Determinism Rules

These are hard requirements. Violations will break reproducibility.

### RNG Isolation (Non-negotiable)

- Each agent has **three independent RNG streams** by domain tag
- World has **one global RNG** for fertility generation only
- **Do not reuse streams** across concerns (no shared RNG for movement + reproduction)
- **Do not shuffle or re-sort agents per tick** — rely on Python dict insertion order
- **Do not introduce new randomness without a new stream** with explicit domain tag

Regression: [tests/verification/test_rng_isolation.py](tests/verification/test_rng_isolation.py)

### State Mutation Determinism

- `next_agent_id` only increments; no ID reuse
- Deaths commit **before** births (order matters)
- Births are sliced by capacity **before** materialization
- Resource regrowth is deterministic: `resources + regen_rate`, capped at fertility
- Harvest distribution has deterministic remainder: first `r` agents get +1

Regression: [tests/verification/test_determinism.py](tests/verification/test_determinism.py)

### Snapshots and Continuity

- Snapshot must capture **all RNG bit-generator states**
- Snapshot must capture **all flags** (perf_flag, world_frame_flag)
- Restore must be **byte-identical continuation** — same trajectory from resume point
- Do not drop or modify RNG states during restore

Regression: [tests/verification/test_snapshots.py](tests/verification/test_snapshots.py)

### Canonical Hashing

- Hash includes: tick, agent count, all RNG states, **all flags**, resource/fertility arrays
- Different hashes under same seed = determinism broken
- Hash comparison is the primary determinism regression gate

See: [FestinaLente/core/snapshot/state_schema.py](FestinaLente/core/snapshot/state_schema.py) (SCHEMA_VERSION = 2)

### If You Touch These, Run Tests

| Topic | Minimum Tests |
|-------|---|
| Engine / stepping / RNG / snapshots | `pytest tests/verification/test_determinism.py tests/verification/test_rng_isolation.py tests/verification/test_snapshots.py` |
| Phase order / aging / death / aging | `pytest tests/verification/test_invariants.py` |
| Regime params / thresholds | `pytest tests/validation/test_regime_contracts.py` |
| Agent identity / birth / reproduction | `pytest tests/verification/test_determinism.py` |
| Spatial / occupancy / harvest | `pytest tests/verification/test_invariants.py` |

**If any fail, fix the root cause. Do not weaken assertions unless the task explicitly requires changing the contract.**

## Repository Map

**Start here for any non-trivial change:**

1. [README.md](README.md) — entry point, command reference, design philosophy
2. [docs/canonical_docs/ARCHITECTURE.md](docs/canonical_docs/ARCHITECTURE.md) — system structure, TransitionContext, phase flow
3. [docs/canonical_docs/RNG_ARCHITECTURE.md](docs/canonical_docs/RNG_ARCHITECTURE.md) — identity model, stream isolation
4. [docs/canonical_docs/DETERMINISM.md](docs/canonical_docs/DETERMINISM.md) — reproducibility contracts, spatial index ordering
5. Related canonical docs for specific subsystem details

**Then inspect:**

- [FestinaLente/main.py](FestinaLente/main.py) — CLI entry point
- [FestinaLente/core/engine.py](FestinaLente/core/engine.py) — step orchestration
- [FestinaLente/core/domains/agent.py](FestinaLente/core/domains/agent.py) — agent identity and RNG setup
- [FestinaLente/core/transitions/transitions.py](FestinaLente/core/transitions/transitions.py) — 4-phase cycle
- [FestinaLente/regimes/compiler.py](FestinaLente/regimes/compiler.py) — ecology math authority
- [FestinaLente/runner/batch_runner.py](FestinaLente/runner/batch_runner.py) — orchestration only
- [FestinaLente/analytics/pipelines/analyze_batch.py](FestinaLente/analytics/pipelines/analyze_batch.py) — post-run analytics

**Before editing behavior:**

- Check [tests/verification/](tests/verification/) and [tests/validation/](tests/validation/) to understand contracts
- Review existing related tests in the same module

**Code organization:**

```
FestinaLente/
├── core/
│   ├── engine.py              [Step orchestration]
│   ├── domains/               [Agent, World]
│   ├── transitions/           [4-phase stepping + TransitionContext]
│   ├── snapshot/              [State serialization + hashing]
│   └── utils/                 [RNG utilities]
├── regimes/                   [Configuration layer]
├── runner/                    [Batch orchestration]
├── analytics/                 [Post-run analysis]
├── app/                       [CLI, dispatch, execution]
└── validation/                [Validation helpers]

tests/
├── verification/              [Determinism, invariants, snapshots, RNG]
└── validation/                [Regime contracts, separation]

docs/
├── canonical_docs/            [Architecture refs: MATHEMATICAL_MODEL, RNG_ARCHITECTURE, DETERMINISM, etc.]
└── Project_Status/            [Status snapshots, roadmap]
```

## Setup and Common Commands

**Environment:**

```bash
# Create and activate
python -m venv .venv
source .venv/bin/activate              # Linux/macOS
# or
.venv\Scripts\activate                 # Windows

# Install
python -m pip install -r requirements.txt
```

**Experiments:**

```bash
# Baseline
python -m FestinaLente.main experiment --regime stable

# Custom parameters
python -m FestinaLente.main experiment --regime stable --runs 5 --ticks 200 --seed 42

# With options
python -m FestinaLente.main experiment --regime abundant --runs 10 --ticks 1000 --tail-fraction 0.1 --perf-flag

# Interactive menu
python -m FestinaLente.main menu
```

**Testing:**

```bash
# Verification (determinism, invariants, snapshots, RNG isolation)
python -m FestinaLente.main verify --suite all
# or
pytest tests/verification

# Validation (regime contracts, separation)
python -m FestinaLente.main validate --suite all
# or
pytest tests/validation

# Specific suites
pytest tests/verification/test_determinism.py
pytest tests/verification/test_rng_isolation.py
pytest tests/verification/test_snapshots.py
pytest tests/verification/test_invariants.py
```

**Development:**

```bash
# Run one experiment and profile
python -m FestinaLente.main experiment --regime stable --runs 1 --ticks 100 --perf-flag

# Run with world-frame capture for debug plots
python -m FestinaLente.main experiment --regime stable --runs 2 --ticks 200 --world-frame-flag --plot-dev
```

## Test and Validation Policy

For any non-trivial code change:

1. **Run the smallest relevant test subset first**
2. **Then run the broader affected suite**
3. **Do not claim success without noting what was actually run**

**When touching specific areas:**

| Area | Tests to Run |
|------|------|
| Engine / stepping / RNG / snapshots | `pytest tests/verification/test_determinism.py tests/verification/test_rng_isolation.py tests/verification/test_snapshots.py` |
| Phase order / timing / aging / death | `pytest tests/verification/test_invariants.py` |
| Regime params / thresholds / rules | `pytest tests/validation/test_regime_contracts.py` |
| Agent identity / birth / reproduction | `pytest tests/verification/test_determinism.py` |
| Spatial / occupancy / harvest mechanics | `pytest tests/verification/test_invariants.py` |
| CLI / outputs / modes | Run full integration: `python -m FestinaLente.main experiment --regime stable --runs 2 --ticks 100` |

**Failure response (mandatory):**

- If tests fail, fix the root cause (not the test)
- Do not weaken assertions unless the task explicitly requires changing the contract
- Escalate to reviewer if root cause is unclear

## Change Policy

- **Minimal diffs first**: Preserve existing architecture unless the task explicitly calls for refactor
- **Avoid opportunistic rewrites**: Do not rename symbols, files, or modules without clear reason
- **Dead code only**: Remove only when confident it is unused and not part of an in-progress migration
- **Keep entry points simple**: Favor readability and traceability over clever abstractions
- **High-signal comments**: Explain *why*, not *what*

## Documentation Policy

Update documentation when changing:

- **Public CLI behavior** (new flags, command structure)
- **Regime definitions or meanings** (parameter changes, regime semantics)
- **Output formats** (metrics, summaries, schemas)
- **Metrics/fingerprint semantics** (what is measured and how)
- **Invariants** (state constraints, death paths)
- **Architectural boundaries** (phase order, module responsibilities)

**If behavior changes but docs are not updated, mention that gap explicitly in your summary.**

## Output / CLI Policy

- **Do not silently change output schemas, labels, or summary semantics** - if metrics change, update docs and explain in summary
- **Do not change default flags or command behavior casually** - preserve backward compatibility
- **If console summaries or exported outputs change, keep them readable and stable**
- **Prefer additive changes over breaking changes** unless explicitly requested

Example: If you add a new metric, update EXPERIMENTS.md to document it. If you change an existing metric's meaning, flag it as a breaking change.

## Code Style Guidance

- **Follow the project's existing naming and module structure** - be consistent with current code
- **Keep functions focused and explicit** - single responsibility
- **Avoid mixing data collection, formatting, and simulation logic in one function** - separate concerns
- **Prefer straightforward control flow over abstraction-heavy patterns** - clarity > cleverness
- **Keep comments high-signal and explain why when needed** - avoid stating the obvious

## When Uncertain

When the correct implementation path is ambiguous:

1. preserve determinism
2. preserve current architecture boundaries
3. preserve testability
4. choose the smaller change

State assumptions clearly in the final summary.
