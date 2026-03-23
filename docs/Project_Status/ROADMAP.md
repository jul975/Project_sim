# Ecosystem Engine Roadmap

## Purpose

This roadmap defines the staged path from the current deterministic ecology baseline into the planned Stage III, IV, and V work.

It is updated to the March 23, 2026 repository state.

## Strategic Goals

1. Preserve deterministic reproducibility as a non-negotiable system invariant.
2. Increase ecological realism through explicit spatial interaction.
3. Introduce trait heterogeneity and inheritance only after the Stage III baseline is stable.
4. Build an analysis and validation stack that supports reproducible experiments rather than ad hoc inspection.
5. Ship releases that are documented against actual code behavior, not target behavior.

## Current Baseline

### Completed stages

- Stage 0: repository and workflow foundation
- Stage I: deterministic kernel (`v0.1`)
- Stage II: controlled ecological dynamics (`v0.2`)

### Current checkpoint

- `v0.2.5`: pre-Stage III freeze baseline

This checkpoint represents:

- the 2D toroidal engine being live
- the performance crisis being resolved
- the deterministic core being stable
- the experiment / verify / validate CLI lanes being live
- the docs being refreshed to the current implementation

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
- pytest-backed verification and validation
- optional profiling and world-frame capture

## Release Checkpoints

### `v0.2`

Original Stage II baseline:

- deterministic ecological core
- older topology and regime set
- earlier validation and reference-hash framing

### `v0.2.5`

Pre-Stage III freeze baseline:

- 2D topology transition complete
- refactored birth and identity path
- request-based CLI surface in place
- green repository test suite
- refreshed canonical and status docs

Versioning note:

- the roadmap uses `v0.2.5` as the freeze checkpoint label
- package metadata is currently `0.3.0a0`

### `v0.3`

Target release for completed Stage III interaction work.

## Stage III (`v0.3`) - Explicit Interaction And Spatial Competition

### Goal

Move from implicit competition through resource sharing and cap pressure to explicit local interaction rules that remain deterministic and testable.

### Key deliverables

- explicit crowding, collision, or local-competition rules
- expanded death and interaction accounting where needed
- stronger 2D spatial diagnostics
- clear Stage III invariants and validation expectations
- a CLI and documentation surface that still stays small and coherent

### Exit criteria

- determinism suites remain green after the interaction changes
- snapshot continuation still holds
- the stable regime remains meaningfully bounded under the new rules
- spatial patterning is measurable with checked-in analytics rather than only by eye
- updated docs explain the implemented rules clearly

## Stage IV (`v0.4`-`v0.6`) - Trait Variation And Selection

### Goal

Introduce heterogeneous agents and inheritance after the Stage III interaction layer is stable.

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

1. Hold the `v0.2.5` baseline steady while Stage III rules are designed.
2. Resolve the remaining public-surface quirks:
   `tail_fraction` wiring, snapshot world-frame flag behavior, and any final CLI naming decisions.
3. Extend regime contracts only where the project wants stronger public guarantees before Stage III.
4. Design and document the Stage III interaction model before implementing it.

## Version Targets

- `v0.2.5`: pre-Stage III freeze baseline
- `v0.3`: Stage III complete
- `v0.4`-`v0.6`: Stage IV iterations
- `v1.0`: Stage V platform-level maturity
