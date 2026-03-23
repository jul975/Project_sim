# Current Project State (March 23, 2026)

## Overview

The Ecosystem Emergent Behavior Simulator is at a strong pre-Stage III freeze point.

Current baseline:

- package metadata: `0.3.0a0`
- documentation freeze checkpoint: `v0.2.5`
- stage posture: pre-Stage III / pre-`v0.3`
- repository posture: working deterministic 2D simulator with green tests, refreshed docs, and a small set of clearly documented pre-freeze rough edges

The major architectural transition to the 2D world model is complete. The runtime is no longer in performance-triage mode, the deterministic core is stable, and the remaining work is mostly about freeze hygiene and Stage III preparation rather than emergency refactoring.

The version labels need to be read carefully:

- `0.3.0a0` is the current package metadata
- `v0.2.5` is the documentation and release-note label for the pre-Stage III freeze baseline

## Headline Status

- **2D topology is live**
  - world state, snapshots, hashing, movement, and occupancy tracking all operate on 2D `(x, y)` positions
- **Determinism remains a hard constraint**
  - canonical state hashing, RNG isolation, snapshot continuation, and invariants are still first-class quality gates
- **The main CLI surface is live**
  - the public lanes are now `experiment`, `verify`, `validate`, and `menu`
  - the older fertility-lane documentation is stale and no longer describes the current CLI
- **Validation is green again**
  - full local pytest run in the project virtual environment on March 23, 2026: `31 passed`
- **The performance crisis is resolved**
  - the documented long-horizon abundant slowdown is no longer blocking normal development

## Verified Current Baseline

### Runtime and architecture

The current engine is stable enough to treat as a freeze candidate for the end of the Stage II baseline:

- deterministic 2D toroidal world
- phase-structured tick loop:
  - movement
  - interaction
  - biology
  - commit
- compact deterministic agent identity model
- snapshot and restore support
- canonical state serialization and hashing
- batch runner plus regime-level analytics and classification

### Command surface

The live user-facing entrypoints are:

- `python -m engine_build.main experiment ...`
- `python -m engine_build.main verify ...`
- `python -m engine_build.main validate ...`
- `python -m engine_build.main menu`

The CLI is intentionally small, but it is coherent enough to document and freeze as a pre-Stage III baseline.

### Regime registry

The live named regimes are:

- `stable`
- `fragile`
- `abundant`
- `saturated`
- `collapse`
- `extinction`

Any remaining docs or commands referring to older regime names are stale.

### Test and quality status

The current repository state is materially better than the March 18 snapshot:

- full pytest run: `31 passed`
- verification lane is green
- validation lane is green
- CLI smoke coverage exists

Interpretation:

- the project is no longer in a "tests mostly pass except one behavioral contract" state
- it is now in a "freezeable baseline with a few known design limitations" state

## Stable Foundations

### Deterministic engine core

The engine still centers deterministic replay and continuation:

- isolated RNG ownership across world, movement, reproduction, and energy
- canonical equivalence via state hash
- snapshot continuation behavior tested directly
- stable runtime traversal semantics
- monotonic ID allocation

### Refactored birth and identity path

The current agent and birth path are materially cleaner than the older seed-lineage-heavy model:

- children derive from compact identity words
- newborns start directly at the parent position
- agent initialization is split into identity, RNG, and state steps
- birth-path cost is much lower than it was during the worst abundant-run slowdown

### Experiment and analytics lane

The experiment path is now one of the stronger parts of the repository:

- `Runner` owns orchestration cleanly
- `SimulationMetrics` records per-tick observables
- batch analytics compute fingerprints and summaries
- regime classification is post hoc and behavior-based
- optional profiling and world-frame sampling exist when explicitly requested

## Current Open Edges

The main remaining issues are no longer architectural emergencies. They are freeze-boundary decisions and Stage III preparation tasks.

### Stage III interactions are not implemented yet

The project is still missing the next layer of explicit local interaction mechanics:

- collision / crowding rules
- local competition semantics beyond shared-cell harvest
- Stage III-specific invariants

### A few public-surface quirks remain

- `tail_fraction` exists on the experiment request, but `run_experiment_mode()` does not currently pass it into `AnalysisConfig`
- snapshot restore currently forces `collect_world_view = False` after reconstruction
- `landscape_spec.contrast` and `landscape_spec.floor` are carried through config but not yet used in fertility generation

### Validation is green but still selective

The suite is passing, but the contract layer is still intentionally narrower than the full regime registry:

- hard contract checks currently focus on `stable`, `extinction`, and `saturated`
- separation checks cover several cross-regime comparisons
- `collapse` and `abundant` are runnable and classified, but not yet hard-contract-covered

### Spatial analytics are present but still lighter than the Stage III target

The codebase now has:

- world-frame sampling
- occupancy and density summaries
- resource heterogeneity and density/resource correlation

But the richer Stage III spatial diagnostics are still a next-step area, not a finished layer.

## Freeze Assessment

This repository is ready to be described as a `v0.2.5` pre-Stage III freeze baseline.

That means:

- the Stage II line is no longer in flux
- the deterministic foundations are strong
- the documentation now matches the code much more closely
- the remaining rough edges are known and bounded

It does **not** mean Stage III is implemented yet.

## Recommended Next Priorities

1. Finalize the pre-Stage III freeze artifact and keep the current baseline green.
2. Decide whether `tail_fraction` should be fully wired or removed from the public experiment request.
3. Decide whether snapshot restoration should preserve `world_frame_flag` or continue forcing it off.
4. Extend validation contracts if `collapse`, `fragile`, or `abundant` should become harder public guarantees.
5. Document Stage III interaction rules before implementing them.

## Navigation

- **README / top-level overview:** [README.md](../../README.md)
- **Strategic roadmap:** [ROADMAP.md](ROADMAP.md)
- **Performance status:** [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
- **Performance reference snapshot:** [PERF_ref.md](PERF_ref.md)
- **Pre-Stage III freeze release note:** [v0.2.5.md](../releases/v0.2.5.md)
- **Canonical architecture docs:** [ARCHITECTURE.md](../canonical_docs/ARCHITECTURE.md)
- **Canonical experiment docs:** [EXPERIMENTS.md](../canonical_docs/EXPERIMENTS.md)
