# Stage III Roadmap

## Status

**Stage line:** `0.3.x`  
**Current repo posture:** active Stage III freeze baseline  
**Current package metadata:** `0.3.0a0`

---

## Purpose

Stage III stabilizes the simulator as a **spatially explicit ecological interaction framework**.

The purpose of this stage is **not** to maximize feature count. It is to make spatial locality, interaction ownership, ecological interpretation, and experiment surfaces explicit enough that the simulator can be treated as a coherent and reproducible research instrument.

In practical terms, Stage III should convert the project from:

> a deterministic ecological engine

into:

> a deterministic, spatially explicit ecological framework with clear interaction semantics, measurable spatial behavior, and a documented freeze line.

---

## Current Baseline

The current codebase already contains most of the Stage III architectural foundation:

- deterministic 2D toroidal world model
- explicit phase-structured tick pipeline
  - movement
  - interaction
  - biology
  - commit
- ratio-native regime specification and compilation
- snapshot / restore support
- canonical state hashing
- validation and verification lanes
- batch experimentation and post-hoc regime analysis
- first-class `OccupancyIndex` integration

This means Stage III should now be treated as a **freeze-hardening stage**, not as a greenfield architecture stage.

---

## Stage III Core Principle

**Do not increase ecological complexity faster than explanatory structure.**

Every Stage III change should strengthen at least one of the following:

- spatial interaction clarity
- local competition semantics
- reproducibility and validation
- observability and diagnostics
- regime interpretability
- future extensibility without architectural blur

If a change does not clearly support one of those goals, it probably belongs after Stage III.

---

## Stage III Scope

### In scope

- explicit spatial interaction ownership
- stronger local competition / contention semantics
- spatial diagnostics and pattern measurement
- clearer boundary between world state and spatial lookup
- validation and release-surface hardening
- documentation alignment with actual implemented behavior

### Out of scope

These should **not** be absorbed into Stage III unless they are required to complete the freeze line:

- broad trait systems
- inheritance and selection dynamics beyond the current line
- major scheduler / event-queue redesign
- evolutionary or ML layers
- large new biological mechanic families
- generalized world-simulation abstraction inflation

---

## Architectural Frame

Stage III depends on keeping the following boundaries clear.

### Canonical state

Owns what the simulation **actually is**.

- `World`
  - dimensions
  - topology / wraparound
  - fertility field
  - resource field
  - environmental update rules
- `Agent`
  - identity
  - position
  - energy/internal state
  - alive state
  - age
  - RNG lineage / local RNG state
- `Engine`
  - run identity
  - config
  - tick progression
  - global coordination / commit ownership

### Derived execution structures

Own what the engine needs to compute the next tick efficiently.

- `OccupancyIndex`
  - sparse cell → agents lookup
  - occupied-cell iteration
  - local counts
  - deterministic local ordering policy

### Tick-local workspace

Owns one-step temporary execution state.

- `TransitionContext`
  - occupancy reference
  - post-harvest survivors
  - pending deaths by cause
  - reproducers awaiting commit

### Derived observation structures

Own what is exported, visualized, or analyzed.

- `WorldView`
- world-frame captures
- simulation metrics
- fingerprints / summaries / regime reports

### Critical rule

`OccupancyIndex` is **not** the world.

It is a **derived execution lookup structure**, not canonical spatial state. The canonical environmental substrate remains the responsibility of `World`.

---

## Stage III Workstreams

## 1. Spatial execution boundary hardening

### Goal

Finish the spatial boundary so that `World`, `OccupancyIndex`, and `TransitionContext` have non-overlapping responsibilities.

### Required outcomes

- `OccupancyIndex` is treated as the first-class engine-side spatial lookup object
- remaining legacy naming is removed or clarified
- deterministic local ordering policy is explicit
- same-cell interaction semantics are documented
- the design stops drifting toward a giant `SpatialIndex` / `worldContext` hybrid

### Concrete tasks

- rename legacy field names such as `occupied_positions` if they no longer describe the actual abstraction
- decide and document whether local occupants are ordered canonically by `agent.id`
- enforce that ordering in one place only
- keep `World` responsible for environmental state and environmental transforms
- keep `OccupancyIndex` responsible for spatial lookup only

### Exit condition

The spatial layer is small, explicit, deterministic, and conceptually frozen.

---

## 2. Explicit local competition semantics

### Goal

Move from incidental shared-cell interaction to clearly modeled local competition.

### Why this matters

Stage III is supposed to make space matter ecologically, not just geometrically.

The simulator should move from:

> agents happen to share a cell

to:

> shared local space has explicit ecological consequences

### Candidate mechanisms

Implement only a small number of these, not all of them:

- crowding / density pressure
- collision or interference cost
- local resource contention semantics stronger than simple availability splitting
- local starvation / competition classification
- simple density-dependent penalties

### Constraints

- keep determinism intact
- keep update order explicit
- avoid introducing opaque or hidden coupling

### Exit condition

At least one nontrivial local competition mechanism is implemented, documented, and measurable.

---

## 3. Spatial diagnostics and observability

### Goal

Make spatial behavior analyzable, not just visible.

### Required outcomes

Stage III should have a minimal stable spatial diagnostics surface.

### Recommended diagnostics

Choose a small, durable set:

- occupancy entropy
- local density variance / clustering proxy
- resource heterogeneity over time
- density–resource correlation
- patch depletion / recovery persistence

### Notes

These do not need to be final research metrics. They do need to be reproducible, interpretable, and cheap enough to maintain.

### Exit condition

Claims about spatial behavior can be supported by logged metrics rather than only inspection of plots or animations.

---

## 4. Validation and semantics hardening

### Goal

Align declared Stage III behavior with actual tested behavior.

### Required outcomes

- verification and validation remain green on the declared freeze line
- regime contracts only promise what the current code actually supports
- helper / analysis-context mismatches are repaired or explicitly scoped out
- public-facing docs reflect implemented behavior, not target behavior

### Concrete tasks

- repair any remaining validation-helper / analysis-context integration gaps
- decide which named regimes are hard guarantees versus exploratory presets
- ensure CLI and analysis docs match the active code paths
- re-check snapshot, world-view, and analysis-edge cases against the current freeze line

### Exit condition

The Stage III line has a small, honest, tested set of guarantees.

---

## 5. Stage III documentation freeze

### Goal

Produce documentation that describes the current Stage III system clearly and without legacy ambiguity.

### Required outcomes

At minimum, the repo should clearly explain:

- current world / occupancy / transition boundary
- tick phase order and ownership
- implemented local interaction mechanics
- available metrics and diagnostics
- declared Stage III non-goals
- what remains post-freeze work rather than release blockers

### Exit condition

A new contributor can understand the Stage III model without reconstructing intent from scattered historical notes.

---

## 6. Release-surface stabilization

### Goal

Treat `v0.3` as a documented freeze line rather than a moving target.

### Required outcomes

- package metadata, docs, and release language align
- the Stage III baseline is described consistently across status docs, roadmap docs, and release notes
- bounded rough edges are tracked explicitly as post-freeze follow-up items

### Exit condition

The project can point to a coherent Stage III freeze baseline without caveats swallowing the stage label.

---

## What Is Already Considered Complete Enough

The following are foundational pieces that should **not** be re-opened as if they were missing:

- ratio-native regime specification and compilation
- explicit engine phase pipeline
- deterministic 2D baseline
- runner / analytics / validation package split
- occupancy abstraction introduced as a first-class object
- snapshot / restore and state hashing infrastructure

These can still be refined, but they are no longer the central missing architecture.

---

## Non-Goals for Stage III

Stage III should **not** become the dumping ground for every interesting future system.

Do not treat the following as Stage III requirements:

- generalized `SpatialIndex` that also owns world state
- trait inheritance and evolutionary selection layers
- agent polymorphism / inheritance-heavy redesign
- global event scheduler redesign
- machine learning or inverse-modeling integration
- major new trophic layers unless they directly validate the current stage goal

If these are pursued, they should be framed as post-Stage III work unless they are narrowly required to complete a declared Stage III acceptance gate.

---

## Recommended Near-Term Priority Order

If Stage III work needs to be sequenced tightly, use this order:

1. finish `OccupancyIndex` integration and naming cleanup
2. freeze `World` vs `OccupancyIndex` vs `TransitionContext` responsibilities
3. implement one explicit local competition mechanic
4. add a minimal spatial diagnostics surface
5. harden validation and public regime semantics
6. finalize Stage III documentation and freeze language

This order preserves clarity while still moving the ecology forward.

---

## Stage III Deliverables

### Required deliverables

- stable deterministic 2D baseline
- documented world / occupancy / transition boundary
- first-class `OccupancyIndex` semantics
- one clear local competition / contention extension
- spatial diagnostics surface
- green verification and declared-validation lanes
- aligned Stage III documentation

### Nice-to-have deliverables

- neighborhood query support beyond same-cell occupancy
- stronger world-frame / observation ergonomics
- expanded regime manifests and comparison surfaces
- improved profiling visibility for spatial hot paths

---

## Stage III Acceptance Criteria

Stage III can be considered stable when all of the following are true:

1. **Determinism remains intact**
   - same-seed reproducibility holds
   - snapshot continuation remains equivalent
   - RNG isolation remains enforced
   - spatial ordering does not introduce hidden nondeterminism

2. **Spatial semantics are explicit**
   - `World`, `OccupancyIndex`, and `TransitionContext` have clear, documented responsibilities

3. **At least one nontrivial local competition mechanism exists**
   - local density or contention matters behaviorally

4. **Spatial patterns are measurable**
   - diagnostics support interpretation beyond visual inspection

5. **Validation matches the declared public surface**
   - the repo promises only what it actually tests and supports

6. **Documentation matches the code**
   - no major Stage III behavior is documented only as future intention

---

## Relationship to Later Stages

Stage III prepares, but does not yet implement, later-stage ambitions such as:

- trait heterogeneity and inheritance
- richer ecological rule families
- more advanced scheduler abstractions
- inverse modeling and learned dynamics
- broader computational-world research instrumentation

The success condition for Stage III is therefore **not** maximal sophistication.
It is a stable, well-bounded, reproducible spatial ecology baseline.

---

## Short Version

**Stage III is the stabilization of the simulator as a spatially explicit ecological interaction framework.**

The deterministic 2D baseline, phase-structured engine, ratio-compiled regimes, and occupancy layer already exist. The remaining work is to harden the world / occupancy / transition boundary, make local competition semantics explicit, promote spatial diagnostics from visual intuition to measured output, and align validation plus documentation with the actual behavior of the current `0.3.x` line.
