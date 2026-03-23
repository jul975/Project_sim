# Performance Reference Snapshot

## Purpose

This file is the short-form reference companion to `PERFORMANCE_REPORT.md`.

Use this page when you want the benchmark numbers and the current interpretation quickly.

## Freeze Baseline

As of March 23, 2026, the performance crisis is considered resolved for the purposes of a pre-Stage III freeze.

That means:

- the engine is usable for normal experiments and validation work
- abundant-like growth runs are no longer catastrophically slow
- births are still the dominant hotspot, but no longer a blocking one

## Reference Benchmarks

| Case | Batch duration | Final population | Tail mean population |
|---|---:|---:|---:|
| Legacy abundant (`gamma = 1`) | `1682.87s` | `428` | `417.346` |
| Refactored abundant (`gamma = 1`) | `19.47s` | `429` | `416.742` |
| Refactored abundant (`gamma = 0.1`) | `43.78s` | `429` | `416.742` |

## Key Takeaways

- the worst slowdown came from an expensive birth materialization path
- compact child identity derivation and cleaner newborn creation removed the crisis-level cost
- phase profiling now makes the remaining hotspots visible
- births are still the main runtime frontier in high-growth regimes

## Use In Documentation

If a document only needs the short conclusion, cite this page.

If it needs the full narrative and refactor explanation, cite `PERFORMANCE_REPORT.md`.
