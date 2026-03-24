# AGENTS.md

## Project overview

This repository contains a deterministic ecosystem / agent-based simulation project written in Python.

The project prioritizes:

- deterministic execution
- explicit scheduling
- reproducible runs
- clear separation of concerns
- validation and verification discipline
- minimal architectural bloat

Treat the codebase as a simulation/research tool, not as a generic app. Preserve reproducibility and conceptual clarity over convenience.

## Core architectural rules

- Keep orchestration, model logic, analytics, and tests separated.
- Runner modules are orchestration-only: do not move ecology logic, regime math, or analytics logic into runners.
- Regime math belongs in the regime/compiler layer, not scattered across engine or analytics code.
- Metrics collection and analytics interpretation are separate concerns.
- Validation and verification are distinct workflows and should remain distinct.

## Determinism rules

These are hard requirements.

- Do not introduce hidden randomness.
- Do not use global randomness if the project uses explicit RNG ownership.
- Do not couple unrelated stochastic processes through shared RNG streams.
- Do not change stepping order casually.
- Do not break snapshot / restore semantics.
- Do not break state hashing / canonical serialization semantics.
- Preserve stable identity semantics for agents and spawned entities.
- If a change affects determinism, update or add determinism tests.

If a task would require changing any of the above, call it out explicitly in your summary.

## Repository map

Read these first before making core changes:

- `README.md`
- architecture / roadmap documentation
- main CLI / entrypoint module
- engine core
- regime compiler / registry / specs
- metrics and analytics modules
- verification and validation tests

Before editing behavior, inspect existing tests to understand intended contracts.

## Setup commands

Use the project’s existing environment and command conventions. Prefer the documented repo workflow over inventing a new one.

Common tasks should be kept working and documented here. Update this section if commands change.

Example placeholders:

- Create environment: `python -m venv .venv`
- Install dependencies: `python -m pip install -r requirements.txt`
- Run experiment: `python -m engine_build.main experiment --regime stable --runs 5 --ticks 200`
- Run verification: `python -m engine_build.main verify --suite all`
- Run validation: `python -m engine_build.main validate --suite test_regime_contracts`

Replace commands above with the repo’s exact current commands.

## Test and validation policy

For any non-trivial code change:

- run the smallest relevant test subset first
- then run the broader affected suite
- do not claim success without noting what was actually run

When touching:

- engine / stepping / RNG / snapshots: run determinism and invariant tests
- regime math / thresholds / classification: run validation suites
- analytics / metrics / summaries: run affected analytics and regression tests
- CLI / outputs: run at least one end-to-end command path

If tests fail, fix the root cause rather than weakening assertions unless the task explicitly requires changing the contract.

## Change policy

- Prefer minimal, targeted diffs.
- Preserve existing architecture unless the task explicitly calls for refactor.
- Avoid opportunistic rewrites.
- Do not rename files, modules, or public symbols without a clear reason.
- Remove dead code only when confident it is unused and not part of an in-progress migration.
- Keep entry points simple and explicit.
- Favor readability and traceability over clever abstractions.

## Documentation policy

Update documentation when changing:

- public CLI behavior
- regime definitions or meanings
- output formats
- metrics/fingerprint semantics
- invariants
- architectural boundaries

If behavior changes but docs are not updated, mention that gap explicitly.

## Output / CLI policy

- Do not silently change output schemas, labels, or summary semantics.
- Do not change default flags or command behavior casually.
- If console summaries or exported outputs are changed, keep them readable and stable.
- Prefer additive changes over breaking changes unless requested.

## Code style guidance

- Follow the project’s existing naming and module structure.
- Keep functions focused and explicit.
- Avoid mixing data collection, formatting, and simulation logic in one function.
- Prefer straightforward control flow over abstraction-heavy patterns.
- Keep comments high-signal and explain why when needed.

## When uncertain

When the correct implementation path is ambiguous:

1. preserve determinism
2. preserve current architecture boundaries
3. preserve testability
4. choose the smaller change

State assumptions clearly in the final summary.
