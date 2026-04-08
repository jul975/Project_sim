# RNG Isolation

## Purpose

This document defines the **RNG-isolation verification contract** for the current movement system.

It exists because the meaning of "movement RNG isolation" changed once movement stopped being a uniform random walk and became a **state-dependent weighted draw**.

Under the old movement model, reproduction policy could change reproduction outcomes without changing the original cohort's movement path.

Under the current movement model, that stronger invariant is no longer generally valid.

The goal of this document is to make the distinction explicit:

* **RNG isolation** is about whether one random stream contaminates another random stream.
* **state coupling** is about whether one subsystem legitimately changes the inputs seen by another subsystem.

These are not the same thing.

---

## Current Movement Model

Movement is no longer sampled as a direct uniform draw over the four von Neumann directions.

The current flow is conceptually:

1. rebuild the live occupancy index for the current tick,
2. build legal destination candidates for each occupied source cell,
3. score each candidate from local spatial features,
4. convert those scores into a probability distribution,
5. sample one destination with the agent's `move_rng`.

In the current spatial-query implementation, candidate scores include a crowding penalty:

```text
score = resource_weight * resource_level - crowding_weight * occupancy_count
```

Those scores are then converted into probabilities through softmax.

That means movement is now a function of:

* the agent's `move_rng`, and
* the current occupancy / local spatial state.

So even if the movement RNG stream remains perfectly isolated, a reproduction-policy change can still alter movement outcomes indirectly by changing occupancy.

---

## The Old Invariant And Why It Broke

The old engine-level regression effectively assumed:

> If only reproduction policy changes, the original cohort's positions should remain identical.

That invariant held only while movement was independent of local population structure.

Once movement became occupancy-weighted, the invariant became too strong.

A reproduction-policy toggle can now change:

* how many births occur,
* which cells become crowded,
* the local `occupancy_count` seen during candidate scoring,
* and therefore the movement probabilities of surviving base-cohort agents.

At that point, path divergence is not evidence of RNG contamination.
It is evidence of legitimate ecological feedback.

So the old test contract had to be split into two separate checks.

---

## What RNG Isolation Means In This Project

For this project, RNG isolation means:

> draws from one concern-specific stream must not perturb draws from another concern-specific stream **when the sampled subsystem inputs are held fixed**.

Examples:

* `repro_rng` usage must not alter `move_rng` choices when movement candidates and probabilities are unchanged,
* `move_rng` usage must not perturb reproduction Bernoulli draws,
* world RNG usage must not perturb per-agent movement or reproduction streams.

This definition is intentionally narrower and more precise than full-engine path equality.

---

## Verification Surface

The current / intended verification surface is split into **two distinct tests**.

### 1. Fixed-input movement RNG isolation test

This test checks the mechanical stream-isolation invariant.

It holds the movement inputs fixed:

* same candidate list,
* same probability vector,
* same initial agent movement RNG state.

Then it deliberately consumes reproduction RNG on one side only and verifies that movement outcomes remain identical.

#### What this proves

It proves that `move_rng` is not being polluted by `repro_rng` consumption.

#### What this test must not do

It must not let the engines diverge in occupancy, births, or local movement inputs, because then the test would no longer be isolating the RNG stream itself.

---

### 2. Occupancy-coupled divergence integration test

This test checks the new model semantics.

It runs two engines with the same seed but different reproduction policy and verifies that base-cohort movement paths can diverge once occupancy-weighted movement feeds back on population structure.

#### What this proves

It proves that the new spatial coupling is live and that movement is responding to population state, not just to a raw movement RNG stream.

#### Why this matters

Without this test, a future refactor could accidentally remove occupancy feedback while keeping determinism intact.

---

## Planned Third Test

A third test is planned once movement weights are injected through configuration or policy objects instead of being hardcoded in the transition layer.

### 3. Zero-crowding legacy-invariant test

This test would run the engine with:

```text
crowding_weight = 0.0
```

Under that configuration, reproduction should no longer feed back into movement through occupancy pressure.

The expected invariant would then be:

> with crowding disabled, changing reproduction policy alone should not change base-cohort movement paths.

#### Why this test is not implemented yet

At the current stage, movement weights are hardcoded in the movement phase.
Until weights are injected explicitly, there is no clean way to express this as a model configuration rather than a hidden test-only branch.

---

## Why We Do Not Use A Hidden Test-Only Bypass

A tempting workaround is to selectively disable occupancy weighting only inside the verification suite.

That is the wrong fix.

Why:

* it hides real model coupling,
* it creates a test-only code path that production never uses,
* it makes failures harder to interpret,
* and it weakens the meaning of the verification surface.

The correct approach is to:

* test stream isolation at the unit boundary,
* test ecological coupling at the integration boundary,
* and only recover the old invariant through an explicit model configuration such as `crowding_weight = 0.0`.

---

## Failure Interpretation Guide

### If the fixed-input isolation test fails

Interpretation:

* movement RNG is actually contaminated by reproduction RNG,
* or movement is accidentally consuming a non-movement stream,
* or the test no longer holds movement inputs fixed.

This is a real RNG-architecture bug until proven otherwise.

### If the occupancy-coupled divergence test fails

Interpretation:

* occupancy may no longer influence movement,
* the crowding term may have been disabled,
* or reproduction-policy differences may no longer propagate into movement.

This is not an RNG bug.
It is a movement-model / integration semantics issue.

### If a full-engine path-equality test fails under occupancy-weighted movement

Interpretation:

* by itself, this is **not** evidence of RNG pollution.

It may simply mean that the engines experienced different population states and therefore different movement probability fields.

---

## Practical Rule

When movement is state-dependent, do **not** use full-engine path equality as the primary proof of RNG isolation unless the movement state is explicitly controlled.

Use:

* **unit-like tests** for stream isolation,
* **integration tests** for ecological/state coupling,
* and later **configuration-specific tests** for recovering narrower invariants.

---

## Summary

The current project distinguishes three ideas:

1. **stream isolation**

   * one RNG stream must not perturb another when subsystem inputs are fixed.

2. **state coupling**

   * one subsystem may legitimately change the state seen by another subsystem.

3. **configuration-specific invariants**

   * stronger path-equality claims should only be tested in parameter regimes where the coupling term is explicitly disabled.

This split keeps the verification suite coherent after introducing occupancy-weighted movement.
