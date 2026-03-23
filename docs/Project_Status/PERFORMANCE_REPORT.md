# Performance Status Report

## Pre-Stage III Assessment (March 23, 2026)

## Executive Summary

The performance crisis that appeared during the 2D transition has been resolved.

The important project-state conclusion is no longer "the simulator is too slow to iterate on." It is now:

> the simulator is fast enough to treat as a pre-Stage III freeze baseline, even though the birth path is still the main optimization frontier in growth-heavy regimes.

The current engine is not fully optimized, but it is no longer blocked by the catastrophic abundant-run slowdown that previously made long-horizon work impractical.

## Historical Problem

During the 2D world / tighter energy-coupling transition, long-horizon `abundant` runs became prohibitively slow.

Documented reference benchmark from the refactor work:

```text
python -m engine_build.main experiment --regime abundant --runs 1 --ticks 5000
```

Legacy reference result:

- batch duration: `1682.87s`
- final population: `428`
- tail mean population: `417.346`

That placed a single 5000-tick abundant run at roughly 28 minutes, which was too expensive for normal development and validation work.

## Root Cause

The main issue was not a single broad quadratic algorithm across the whole engine.

The main issue was:

- high birth volume
- multiplied by
- a very expensive per-birth construction path

The older newborn path paid for too much generic setup work:

- heavier seed-lineage reconstruction
- multiple RNG initializations per newborn
- generic constructor behavior that founders and newborns did not actually need equally
- random child-position initialization that was immediately overwritten by the parent position

In practice, the slowdown was "too many expensive births," not "everything in the tick loop is broken."

## What Changed

The refactor improved both performance and architectural shape.

### 1. Compact child identity derivation

The older heavy `SeedSequence.spawn()` lineage path was replaced with deterministic identity words built from:

- run entropy
- child entropy from the parent's reproduction RNG
- parent ID
- parent offspring count

This preserved deterministic identity while making newborn materialization much cheaper.

### 2. Direct newborn positioning

Newborns are now initialized directly at the parent position instead of sampling and then overwriting a random position.

### 3. Cleaner agent initialization

Agent setup is split more clearly into:

- identity
- RNG setup
- state initialization

This helps both runtime cost and maintainability.

### 4. Optional world-frame collection

World-view packaging is no longer always built in the hot path. It is now explicitly optional.

### 5. In-place resource regrowth

Resource regrowth now uses in-place NumPy operations instead of allocating replacement arrays each tick.

### 6. Better phase profiling

The engine now measures:

- movement
- interaction
- biology
- commit

and commit subphases:

- setup
- deaths
- births
- resource regrowth

## Documented Reference Impact

The checked-in performance notes already capture the core result of the refactor.

Reference comparison:

| Case | Batch duration | Final population | Tail mean population |
|---|---:|---:|---:|
| Legacy abundant (`gamma = 1`) | `1682.87s` | `428` | `417.346` |
| Refactored abundant (`gamma = 1`) | `19.47s` | `429` | `416.742` |
| Refactored abundant (`gamma = 0.1`) | `43.78s` | `429` | `416.742` |

Interpretation:

- the severe structural slowdown was removed
- the macroscopic regime behavior stayed broadly similar
- the performance gains came from implementation improvements rather than a major behavioral rewrite

## Current Interpretation

As of March 23, 2026:

- performance is no longer blocking documentation, validation, or normal batch experimentation
- births remain the dominant hotspot in abundant-like runs
- movement is the next visible cost center
- the current engine shape is good enough to carry into the freeze boundary

That is a much healthier position than the earlier March state.

## Remaining Performance Debt

### Births still dominate high-growth runs

This is not an emergency anymore, but it is still the clearest optimization frontier if more work becomes necessary.

### Deep birth-subprofile detail is still limited

The highest-level timings are useful. The deepest birth-path breakdown is still not rich enough to fully explain every remaining millisecond.

### World-frame and plotting paths remain secondary

The optional observability surfaces are useful, but they are not yet the most polished or most performance-focused part of the project.

### No new benchmark rerun was captured for this doc refresh

This report uses the documented reference benchmarks already checked into the repository. The project-state conclusion still holds: the crisis is resolved and the engine is freezeable.

## Freeze Readiness Conclusion

The performance story is now good enough for a `v0.2.5` pre-Stage III freeze.

That does **not** mean performance work is over forever.

It means:

- the worst regression has been fixed
- the remaining hotspots are known
- the simulator is usable for the next stage of design work
- performance is now an optimization topic, not a blocking crisis
