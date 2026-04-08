# Current Project State (April 8, 2026)

## Overview

The Ecosystem Emergent Behavior Simulator is at a strong Stage III freeze point.

Current baseline:

- package metadata: `0.3.0a0`
- documentation checkpoint: this status document now reflects the Stage III freeze point
- stage posture: Stage III freeze line on `0.3.0a0`
- repository posture: working deterministic 2D simulator with green tests, refreshed docs, and a small set of clearly documented freeze-point rough edges

The major architectural transition to the 2D world model is complete. The runtime is no longer in performance-triage mode, the deterministic core is stable, and the remaining work is mostly about holding the Stage III baseline steady and scoping the next post-freeze priorities rather than emergency refactoring.

The version labels need to be read carefully:

- `0.3.0a0` is the current package metadata and the active Stage III line reflected by this status document
- `v0.2.5` is the earlier documentation and release-note label for the pre-Stage III freeze baseline

## Headline Status

- **2D topology is live**
  - world state, snapshots, hashing, movement, and occupancy tracking all operate on 2D `(x, y)` positions
- **Stage III freeze point is the current working baseline**
  - the repository is no longer being described here as a pre-Stage III candidate
  - the remaining rough edges are bounded follow-up items rather than blockers to the current stage label
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

The current engine is stable enough to treat as the current Stage III freeze baseline:

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

The CLI is intentionally small, but it is coherent enough to document and freeze as a Stage III baseline.

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
- it is now in a "freezeable Stage III baseline with a few known design limitations" state

## Stable Foundations

### Deterministic engine core

The engine still centers deterministic replay and continuation:

- isolated RNG ownership across world, movement, reproduction, and energy
- canonical equivalence via state hash
- snapshot continuation behavior tested directly
- stable runtime traversal semantics
- monotonic ID allocation

### Refactored birth and identity path

The current agent and birth path use a flat identity-words architecture:

- agents derive from deterministic tuples: `(run_entropy, founder_id)` or `(run_entropy, child_entropy, parent_id, offspring_count)`
- no per-agent `SeedSequence` lineage tree is stored
- RNGs are derived from identity + domain tags, not from spawn() mutations
- newborns inherit parent position directly (no position draw)
- birth-path overhead is minimal, solving the abundant-run slowdown from earlier iterations
- detailed design in [RNG_ARCHITECTURE.md](docs/canonical_docs/RNG_ARCHITECTURE.md)

### Experiment and analytics lane

The experiment path is now one of the stronger parts of the repository:

- `Runner` owns orchestration cleanly
- `SimulationMetrics` records per-tick observables
- batch analytics compute fingerprints and summaries
- regime classification is post hoc and behavior-based
- optional profiling and world-frame sampling exist when explicitly requested

## Current Open Edges

The main remaining issues are no longer architectural emergencies. They are Stage III freeze-boundary decisions and post-freeze follow-up tasks.

### Stage III follow-up work remains bounded

The current baseline is already being treated as Stage III, but there is still obvious room to harden and extend the interaction layer:

- collision / crowding rules remain a natural expansion path
- local competition semantics beyond shared-cell harvest are still limited
- Stage III-specific invariants can still be tightened

### A few public-surface quirks remain

- snapshot restore currently forces `collect_world_view = False` after reconstruction (provisional design edge)
- `landscape_spec.contrast` and `landscape_spec.floor` are carried through config but not yet used in fertility generation

### Validation is green but still selective

The suite is passing, but the contract layer is still intentionally narrower than the full regime registry:

- hard contract checks currently focus on `stable`, `extinction`, and `saturated`
- separation checks cover several cross-regime comparisons
- `collapse` and `abundant` are runnable and classified, but not yet hard-contract-covered

### Spatial analytics are present but still lighter than the longer-term target

The codebase now has:

- world-frame sampling
- occupancy and density summaries
- resource heterogeneity and density/resource correlation

But the richer next-step spatial diagnostics are still a follow-up area, not a finished layer.

## Freeze Assessment

This repository is ready to be described as a Stage III freeze baseline on the `0.3.0a0` line.

That means:

- the repository is being held at a Stage III freeze point
- the deterministic foundations are strong
- the documentation now matches the code much more closely
- the remaining rough edges are known and bounded

It does **not** mean the post-Stage III roadmap is already implemented.

## Recommended Next Priorities

1. Hold the Stage III freeze baseline steady and keep the current baseline green.
2. Decide whether `tail_fraction` should be fully wired or removed from the public experiment request.
3. Decide whether snapshot restoration should preserve `world_frame_flag` or continue forcing it off.
4. Extend validation contracts if `collapse`, `fragile`, or `abundant` should become harder public guarantees.
5. Document the next interaction and diagnostics priorities before implementing them.

## Navigation

- **README / top-level overview:** [README.md](../../README.md)
- **Strategic roadmap:** [ROADMAP.md](ROADMAP.md)
- **Performance status:** [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
- **Performance reference snapshot:** [PERF_ref.md](PERF_ref.md)
- **Earlier pre-Stage III freeze release note:** [v0.2.5.md](../releases/v0.2.5.md)
- **Canonical architecture docs:** [ARCHITECTURE.md](../canonical_docs/ARCHITECTURE.md)
- **Canonical experiment docs:** [EXPERIMENTS.md](../canonical_docs/EXPERIMENTS.md)
