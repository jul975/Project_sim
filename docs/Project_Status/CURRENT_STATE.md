# Current Project State (March 18, 2026)

## Overview

The Ecosystem Emergent Behavior Simulator is in active **pre-Stage III stabilization**.

The major architectural transition to a 2D world model is complete, the post-refactor runtime crisis has been resolved, and the determinism-preserving simulation core is in much better shape than it was earlier in March. The project is no longer blocked by the earlier catastrophic abundant-run slowdown, but it is still in an active cleanup and alignment phase before a clean Stage III freeze.

The main work still in motion is now:

- validation contract alignment,
- CLI surface cleanup,
- spatial metric reintroduction,
- and Stage III interaction design.

**Last updated:** March 18, 2026

**Current stage:** Pre-Stage III / pre-`v0.3`

**Project posture:** Working experimental engine with strong determinism guarantees, active refactoring, and remaining interface/validation cleanup

## Headline Status

- **2D topology is live**
  - the engine, world, snapshots, and state serialization all operate on 2D `(x, y)` positions
- **The runtime crisis is resolved**
  - the earlier abundant birth-path slowdown is no longer blocking development
- **Determinism remains a hard constraint**
  - snapshot continuation, RNG isolation, and canonical state behavior remain central quality gates
- **Verification is strong; validation is not fully settled**
  - on March 18, 2026, the full pytest run was `19 passed, 1 failed`
  - the remaining failure is `tests/validation/test_regime_contracts.py::test_extinction_regime_validation`
- **The CLI module is in transition, not frozen**
  - the request/parser/dispatch architecture is taking shape
  - the experiment path is usable
  - the validation and fertility lanes still need contract cleanup

## Stable Foundations

### 2D simulation core

The system now runs on a 2D toroidal world:

- fertility and resource fields are 2D NumPy arrays
- agent positions are `(x, y)` tuples
- movement and wrapping semantics are 2D
- occupancy is tracked by cell position during the transition phases

This is the key enabling step for Stage III spatial interaction work.

### Deterministic execution model

The simulation still centers determinism as a first-class design rule:

- reproducible trajectories from fixed seeds
- isolated RNG ownership across world, movement, reproduction, and energy
- canonical state serialization and hashing
- snapshot/restore continuation support
- explicit invariants around IDs, bounds, age, energy, and population caps

### Updated agent identity and initialization model

The current agent design is materially different from the older seed-lineage-heavy version.

Important current characteristics:

- newborn identity is derived from compact deterministic identity words
- agents no longer store the older `SeedSequence` lineage scaffolding on-object
- each agent still owns three separate RNG streams:
  - movement
  - reproduction
  - energy
- initialization is cleaner than the earlier generic birth path, even though more cleanup is still possible

This is one of the main reasons the post-refactor runtime profile is far healthier than it was during the earlier abundant-run slowdown.

### Phase-structured engine

The engine loop is now clearly shaped around:

1. movement
2. interaction
3. biology
4. commit

That phase structure is important because it improves:

- reasoning clarity,
- profiling,
- future interaction work,
- and validation targeting.

### Batch execution and analytics

The batch/analytics layer is in active use and remains one of the stronger parts of the codebase:

- multi-run orchestration through `Runner`
- deterministic run-seed generation from a batch seed
- per-tick metrics collection
- tail-window fingerprint analysis
- regime summarization and classification
- experiment reporting with phase timing output

## Performance State

### The earlier performance blocker is no longer the main problem

The severe long-horizon abundant slowdown that previously made development impractical has been addressed.

The documented benchmark in `docs/Project_Status/PERFORMANCE_REPORT.md` captures the core shift:

- legacy abundant `5000`-tick benchmark: `1682.87s`
- documented post-refactor comparable benchmark: `19.47s`

The exact runtime will still vary by machine and run shape, but the important project-state conclusion is:

> the birth-path runtime pathology is no longer blocking iterative work.

### Current performance frontier

Performance work is no longer emergency triage. It is now targeted refinement.

Current technical reading:

- commit births remain the dominant runtime hotspot in high-growth regimes
- movement has become the next visible hot path
- movement does not currently look pathological; it scales roughly linearly with agent count
- the most expensive sub-cost inside movement is directional RNG sampling, not a broad structural algorithm failure

So the performance situation is now:

- **resolved as a crisis**
- **not finished as an optimization story**

## Regime Set (Current Registry)

The current named regimes in `engine_build/regimes/registry.py` are:

| Regime | Role |
| --- | --- |
| `stable` | default bounded baseline |
| `fragile` | high-cost reproduction stress case |
| `extinction` | low-regeneration collapse pressure |
| `collapse` | lower-threshold collapse testing |
| `saturated` | high-occupancy / near-cap growth case |
| `abundant` | permissive growth regime |

Important note:

- `test_stable` is **not** part of the current registry
- docs or commands still referring to `test_stable` are stale against the live regime set

## Testing And Validation State

### Verification status

The determinism-oriented verification foundation is in good shape:

- determinism
- invariants
- RNG isolation
- snapshots
- regime separation checks

These are now conceptually separate from behavioral validation.

### Validation status

Validation is the main quality area still being aligned.

Current observed state:

- full pytest on March 18, 2026: `19 passed, 1 failed`
- failing test: `tests/validation/test_regime_contracts.py::test_extinction_regime_validation`
- current failure condition:
  - expected extinction-rate floor is too strict for current empirical output
  - observed extinction rate in the failing run was `0.5`, below the asserted `0.8`

Interpretation:

- the validation framework exists
- the validation tests are no longer completely legacy
- but at least one behavioral contract still needs recalibration against the current engine behavior

This is a much better state than "no validation," but it is not yet a frozen regime-validation surface.

## CLI Status

The CLI has improved structurally, but it should be described as **in transition**, not fully stable.

### What is now in place

- explicit request objects
- parser module
- dispatcher
- menu frontend
- split between:
  - `experiment`
  - `verify`
  - `validate`
  - `fertility`

### What is still misaligned

- the validation CLI request/parser contract and `run_validation.py` do not currently describe the same suite names
- the menu path still exposes only part of the newer frontend surface
- the fertility request exists, but the underlying fertility workflow still behaves like a temporary stub
- the CLI module is closer to the intended architecture than before, but not yet fully coherent end-to-end

So the correct current statement is:

> the CLI architecture is actively being normalized, but it is not yet a finished public interface.

## In Transition

### Validation contract cleanup

Behavioral validation is the biggest open alignment task.

What still needs work:

- update thresholds to current empirical behavior
- make validation expectations clearly distinct from verification checks
- stabilize suite naming across CLI requests, parser choices, and runner entry points

### Spatial metrics and fingerprints

The engine now has the 2D structure needed for Stage III, but the analytics layer has not fully caught up.

Still needed:

- occupancy distribution metrics
- clustering or local-density summaries
- neighborhood-sensitive spatial diagnostics

The topology is ready; the metrics layer is not fully there yet.

### CLI and entrypoint polish

The request-driven CLI design is close to the correct architecture, but the last wiring inconsistencies still need cleanup before it should be treated as stable.

### Fertility/dev plotting lane

The fertility/dev plotting path remains a secondary lane and still needs alignment with the current request/runner architecture before it should be treated as a first-class interface.

## Known Limitations

1. **Validation is not green yet**
   - one regime-contract test currently fails
   - this is a behavioral-threshold issue, not a core determinism failure

2. **CLI surface is not yet frozen**
   - request objects, parser, menu, and runners are closer to alignment, but not fully consistent

3. **Spatial analytics lag behind the 2D engine**
   - the topology and occupancy structure exist
   - the higher-level spatial metrics still need to be reintroduced

4. **Fertility demo path is still provisional**
   - it exists, but it is not yet as cleanly integrated as the main experiment path

5. **Performance work is still open**
   - the crisis is resolved
   - births remain the main optimization frontier in abundant-like runs

## Quality Gates

Simulation logic changes should continue to satisfy all of the following:

- pass determinism-oriented verification
- preserve snapshot continuation behavior
- maintain or intentionally update invariants
- document any intentional state-hash or regime-behavior changes
- update docs when public behavior or architecture changes

Recommended pre-freeze quality gates:

- verification suites green
- validation suites green
- experiment/verify/validate command surface coherent
- current regime set documented consistently across code and docs
- post-refactor performance baseline recorded

## Next Immediate Priorities

1. **Stabilize the validation surface**
   - recalibrate failing extinction contract
   - align suite naming and expectations

2. **Finish CLI normalization**
   - make parser, requests, menu, dispatcher, and runners speak the same contract
   - keep `main.py` as a thin frontend selector only

3. **Reintroduce 2D-aware spatial metrics**
   - occupancy
   - clustering
   - neighborhood pressure

4. **Document Stage III interaction rules before implementation**
   - collision/crowding policy
   - local competition semantics
   - new invariants

5. **Freeze a clean pre-Stage III baseline**
   - once validation, CLI, and docs are aligned

## Navigation

- **README / project overview:** [README.md](../../README.md)
- **Strategic roadmap:** [ROADMAP.md](ROADMAP.md)
- **Performance status:** [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
- **Architecture docs:** [docs/canonical_docs/ARCHITECTURE.md](../canonical_docs/ARCHITECTURE.md)
- **Experiment / validation concepts:** [docs/canonical_docs/EXPERIMENTS.md](../canonical_docs/EXPERIMENTS.md)
