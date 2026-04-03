# Ecosystem Engine Roadmap

## Purpose

This roadmap defines the staged path from the current Stage III freeze baseline into the follow-on Stage IV and V work.

It is updated to the April 3, 2026 repository state.

## Strategic Goals

1. Preserve deterministic reproducibility as a non-negotiable system invariant.
2. Increase ecological realism through explicit spatial interaction.
3. Introduce trait heterogeneity and inheritance only after the Stage III line is stable.
4. Build an analysis and validation stack that supports reproducible experiments rather than ad hoc inspection.
5. Ship releases that are documented against actual code behavior, not target behavior.

## Current Baseline

### Completed stages

- Stage 0: repository and workflow foundation
- Stage I: deterministic kernel (`v0.1`)
- Stage II: controlled ecological dynamics (`v0.2`)

### Current checkpoint

- `0.3.0a0`: Stage III freeze baseline
- `v0.2.5`: earlier pre-Stage III freeze checkpoint

This checkpoint represents:

- the 2D toroidal engine being live
- the performance crisis being resolved
- the deterministic core being stable
- the `experiment`, `verify`, `validate`, `dynamic`, and `menu` command surfaces being live
- the docs being realigned to the active Stage III freeze framing
- validation still needing repair before the freeze line can be called fully green again

### Current capabilities

- deterministic 2D step pipeline
- canonical state hashing
- snapshot and restore continuation
- isolated RNG streams for world, movement, reproduction, and energy
- six named regimes:
  - `stable`
  - `fragile`
  - `abundant`
  - `saturated`
  - `collapse`
  - `extinction`
- batch experimentation and post-hoc regime classification
- pytest-backed verification and validation lanes
- optional profiling, world-frame capture, and animated exploration

### Current bounded gaps

- local interaction mechanics are still lighter than the longer-term crowding / collision target
- `tail_fraction` is still not wired into the experiment analysis context
- snapshot reconstruction still forces `collect_world_view = False`
- the validation helper path currently fails before regime-contract assertions because it does not populate the `AnalysisContext` fields required by `analyze_batch()`

## Release Checkpoints

### `v0.2`

Original Stage II baseline:

- deterministic ecological core
- older topology and regime set
- earlier validation and reference-hash framing

### `v0.2.5`

Earlier pre-Stage III freeze baseline:

- 2D topology transition complete
- refactored birth and identity path
- request-based CLI surface in place
- refreshed canonical and status docs for the pre-Stage III line

### `0.3.0a0`

Current Stage III freeze line:

- active working line reflected by the updated status and canonical docs
- deterministic 2D engine, experiment pipeline, and exploration path are live
- follow-up work is now about hardening, validation repair, and deciding how much additional interaction complexity belongs in this line

Versioning note:

- package metadata is currently `0.3.0a0`
- `v0.2.5` should now be read as the earlier historical freeze checkpoint, not the current one

### `v0.3`

Target stabilized Stage III release after the current freeze-line follow-up work is complete.

## Stage III (`0.3.x`) - Active Freeze Line And Hardening

### Goal

Hold the current Stage III freeze baseline steady while tightening interaction semantics, diagnostics, and validation into a release-ready line.

### Current Stage III posture

- the deterministic 2D engine is already the active baseline
- the Stage III label is now attached to the live freeze line, not only to future work
- local interaction remains intentionally lighter than the longer-term target

### Follow-up deliverables

- explicit crowding, collision, or local-competition rules if they remain in scope for this line
- expanded death and interaction accounting where needed
- stronger 2D spatial diagnostics
- clearer Stage III invariants and validation expectations
- repaired validation helper and analysis-context wiring so contract suites are usable again

### Exit criteria for a stabilized `v0.3`

- determinism suites remain green after any interaction changes
- snapshot continuation still holds
- validation suites are green again and reflect the intended regime contracts
- the stable regime remains meaningfully bounded under the documented rules
- spatial patterning is measurable with checked-in analytics rather than only by eye
- updated docs explain the implemented rules clearly

## Stage IV (`v0.4`-`v0.6`) - Trait Variation And Selection

### Goal

Introduce heterogeneous agents and inheritance after the Stage III line is stabilized.

### Key deliverables

- trait schema in runtime state and snapshots
- inheritance and mutation during reproduction
- trait-distribution analytics over time
- controlled experiments showing regime-dependent selection behavior

### Exit criteria

- determinism and snapshot continuation still hold with traits enabled
- trait distributions evolve non-trivially across runs
- at least one reproducible selection scenario is documented end to end

## Stage V (`v0.7`-`v1.0`) - Research Platform

### Goal

Turn the simulator into a reproducible, analysis-first experimentation platform.

### Key deliverables

- regime mapping and boundary-analysis tooling
- transition-detection or early-warning analytics
- benchmark and reproducibility manifests
- release-quality reporting and artifact structure
- documentation that reads as a coherent research artifact

### Exit criteria

- reproducibility expectations are explicit and testable
- benchmark and validation workflows are repeatable
- repository docs and releases stay aligned with the live code

## Cross-Stage Quality Gates

These remain in force across all stages:

- deterministic behavior is required for merges that affect simulation logic
- no unordered structural mutation in the core pipeline
- new features must define invariants and validation intent
- documentation must describe current implementation, not future wishes
- freeze or release tags require updated docs and passing tests

## Near-Term Priorities

1. Hold the Stage III freeze baseline steady while repair work lands.
2. Repair the validation helper and analysis-context wiring so the contract suites run again.
3. Resolve the remaining public-surface quirks:
   `tail_fraction` wiring, snapshot world-frame flag behavior, and any final CLI naming decisions.
4. Decide whether the current Stage III line stops at the freeze baseline or adds explicit crowding / collision semantics before `v0.3`.
5. Extend regime contracts only where the project wants stronger public guarantees on the stabilized Stage III line.

## Version Targets

- `v0.2.5`: earlier pre-Stage III freeze baseline
- `0.3.0a0`: current Stage III freeze line
- `v0.3`: stabilized Stage III release
- `v0.4`-`v0.6`: Stage IV iterations
- `v1.0`: Stage V platform-level maturity
