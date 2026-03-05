# Ecosystem Engine Roadmap

## Purpose
This roadmap defines the project goals and staged milestones for evolving the engine from a deterministic ecological simulator into a research-grade experimentation platform.

## Strategic Goals
1. Preserve deterministic reproducibility as a non-negotiable system invariant.
2. Increase ecological realism through explicit interactions and spatial structure.
3. Introduce trait heterogeneity and selection dynamics.
4. Build a robust analytics and validation stack for reproducible research.
5. Deliver disciplined releases with clear verification gates.

## Current Baseline
### Completed
- Stage 0: project/workflow foundation
- Stage I: deterministic kernel (`v0.1`)
- Stage II: controlled ecological dynamics (`beta v0.2` baseline)

### Current Capabilities
- deterministic step ordering and canonical state hashing
- snapshot/restore continuation consistency
- isolated RNG streams (world/move/repro/energy)
- regime runner (`extinction`, `stable`, `saturated`)
- validation suites for determinism, invariants, dynamics, and baseline checks

## Stage Plan

## Stage III (`v0.3`) - Explicit Interaction and Spatial Competition
### Goal
Move from implicit resource competition to explicit interaction mechanics with stronger spatial behavior.

### Key Deliverables
- explicit crowding/collision or local competition rules
- expanded death classification aligned with new interactions
- improved spatial metrics (clustering/occupancy structure)
- optional 2D topology path (`World2D` or generalized world interface)

### Exit Criteria
- determinism suites remain green after interaction changes
- stable regime remains bounded under new rules
- non-trivial spatial patterning is measurable and reproducible

## Stage IV (`v0.4`-`v0.6`) - Trait Variation and Selection
### Goal
Introduce heterogeneous agents and inheritance so selection pressure can emerge.

### Key Deliverables
- trait schema in agent state and snapshots
- inheritance + mutation in reproduction flow
- trait-distribution analytics over time
- controlled experiments showing regime-dependent selection behavior

### Exit Criteria
- determinism and snapshot continuation still hold with traits enabled
- trait distributions evolve non-trivially across runs
- at least one reproducible selection scenario is documented

## Stage V (`v0.7`-`v1.0`) - Research Platform
### Goal
Package the system as a reproducible, analysis-first research platform.

### Key Deliverables
- regime mapping and boundary analysis tooling
- early-warning signal analytics for transition detection
- optional predictive/inference pipelines (classification/regression)
- benchmark and reproducibility manifest standards
- release-quality reporting and artifact structure

### Exit Criteria
- reproducibility contract enforced across documented environments
- benchmark/validation workflow is repeatable and automated
- repository documentation reads as a complete research artifact

## Cross-Stage Quality Gates (Always On)
- deterministic behavior is required for all merges affecting simulation logic
- no unordered state transitions in core pipeline
- all new features must define invariants and validation checks
- documentation must track code-level behavior, not intended behavior
- release tags require passing validation suites and updated baseline artifacts

## Near-Term Priorities
1. Freeze and maintain Stage II baseline quality (tests + docs + release hygiene).
2. Implement Stage III interaction model with minimal deterministic surface area.
3. Extend validation analytics to cover new interaction-specific invariants.
4. Keep baseline hash governance explicit when intentional model changes occur.

## Version Targets
- `v0.3`: Stage III complete
- `v0.4`-`v0.6`: Stage IV iterations
- `v1.0`: Stage V platform-level maturity
