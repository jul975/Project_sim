# Performance Refactor Report  
## Ecosystem Emergent Behavior Simulator — Pre–Stage III Assessment

## 1. Overview

This report summarizes the performance problems encountered during the transition to the 2D world / tighter energy-coupling architecture, the structural changes introduced to resolve them, and the measured impact of those changes.

The refactor was triggered by a severe runtime pathology in long-horizon `abundant` regime runs. What initially appeared to be a possible broad algorithmic scaling issue was traced more precisely to an extremely expensive **birth materialization path** inside the commit phase, compounded by unnecessary per-step reporting overhead and an engine structure that had become too rigid for further subsystem expansion.

The resulting rewrite was substantial, but justified. It improved both:

- **runtime performance**
- **architectural clarity and extensibility**

The current codebase is significantly better positioned for:

- regime classification as command-level entry points
- pytest-based regime validation
- lightweight plotting / quick visual confirmation
- occupancy metric reintroduction
- a stable pre–Stage III freeze

---

## 2. Problem Statement

After introducing the 2D world and tighter energy coupling, long-horizon runs in the `abundant` regime became prohibitively slow.

### Legacy benchmark
Command:
`python -m engine_build.main experiment --regime abundant --runs 1 --ticks 5000`

Output:
- **Batch duration:** `1682.87s`
- **Final population:** `428`
- **Tail mean population:** `417.346`

This placed a single 5000-tick abundant run at roughly **28 minutes**, which was too expensive for iterative development, batch mapping, or future validation workflows.

At that point, this was no longer a cosmetic optimization concern. The cost of simulation had become large enough to block practical extension of the system.

---

## 3. Root Cause Analysis

## 3.1 Immediate hotspot

Earlier profiling showed that the dominant hotspot was the **birth path inside commit**.

The critical legacy path was:

- `Engine.commit_phase()`
- `Engine.create_new_agent()`
- `Agent.reproduce()`
- `Agent.__init__()`

Earlier measurements showed:

- `commit_births = 246.466s`
- total batch time `= 254.445s`
- birth commit cost `= 96.86%` of total runtime
- birth commit cost `= 99.65%` of commit time

This established that the catastrophic slowdown was not spread evenly across the simulation loop. It was concentrated in committed births.

---

## 3.2 Legacy structural cause

The old engine handled newborn creation through a very heavy general-purpose path.

For each committed child, the legacy code effectively did the following:

1. derive a child `SeedSequence`
2. reconstruct lineage through spawn-key logic
3. create a full `Agent`
4. inside `Agent.__init__`, spawn three child sequences
5. construct three NumPy RNG objects
6. randomly initialize position
7. randomly initialize energy
8. then overwrite the child position with the parent position

That meant the engine paid for:

- lineage reconstruction
- multiple RNG initializations
- generic constructor logic
- wasted random position initialization

for every child birth.

In abundant long-horizon runs, this became the dominant cost center.

---

## 3.3 Clarifying the scaling issue

The runtime pathology initially resembled a possible `O(n²)` failure. In practice, the evidence suggests a more specific interpretation:

The dominant issue was **not primarily a global quadratic algorithm**.

It was:

- **high birth volume**
- multiplied by
- **very expensive per-birth construction cost**

So the practical problem was closer to:

`O(total_births) × very large constant factor`

rather than a single obvious quadratic loop dominating the whole engine.

That distinction matters because it explains why a focused redesign of child creation produced such large gains.

---

## 4. Key Structural Problems in the Legacy Design

## 4.1 Heavy newborn construction
Births used a broad generic initialization path instead of a specialized newborn materialization path.

## 4.2 Wasted initialization work
Children were given a random position during initialization and then immediately reassigned to the parent’s position.

## 4.3 Always-on world-view construction
The engine built world-view packaging on every step, including:

- sorted agent lists
- position arrays
- energy arrays
- copied resource grids

This was useful for debugging and metrics, but too expensive to keep permanently in the hot path.

## 4.4 Repeated deterministic sorting
Deterministic sorting was used repeatedly in places such as:

- movement processing
- world-view construction
- local harvest resolution

These were not the main cause of the catastrophic slowdown, but they were meaningful recurring costs.

## 4.5 Insufficient observability
The old system could tell that runs were slow, but not with enough internal resolution to isolate and optimize the correct layer cleanly.

---

## 5. Implemented Changes

The refactor addressed both performance and structural clarity.

## 5.1 Birth identity derivation redesign
The largest change was replacing the older heavy `SeedSequence`-spawn birth path with a lighter deterministic identity derivation scheme based on compact identity words.

Instead of reconstructing newborn lineage via repeated `SeedSequence.spawn(...)` logic, the current design derives child identity from a fixed deterministic tuple such as:

- run entropy
- child entropy sampled from parent reproduction RNG
- parent id
- offspring count

This preserves deterministic identity while avoiding the heavier legacy lineage machinery.

### Impact
- drastically reduces per-birth setup cost
- makes identity derivation explicit
- simplifies the reproduction path
- better matches the engine’s real deterministic requirements

---

## 5.2 Direct newborn positional initialization
The new birth path initializes newborns directly at the parent position.

This removes the earlier waste where a random child position was generated only to be overwritten immediately.

### Impact
- removes unnecessary RNG work
- removes wasted initialization logic
- simplifies child creation semantics

---

## 5.3 Agent initialization decomposition
Agent setup is now more explicitly separated into identity / RNG / state concerns.

This is a structural improvement even beyond performance.

### Impact
- easier reasoning about initialization
- easier profiling
- easier future extension
- cleaner distinction between founders and newborns

---

## 5.4 Optional world-view collection
World-view generation is no longer always active in the hot path.

It can now be selectively enabled rather than being built every step by default.

### Impact
- removes expensive packaging work from default experiment runs
- preserves the ability to inspect state when needed
- improves separation between simulation and observability

---

## 5.5 In-place resource regrowth
Resource updates were changed to use in-place NumPy operations instead of allocating replacement arrays each tick.

### Impact
- lower allocation overhead
- lower memory churn
- cleaner long-horizon performance behavior

---

## 5.6 Reduced deterministic sorting overhead
Some sorting costs were removed or reduced, especially in local harvest resolution.

### Impact
- less repeated overhead in hot loops
- improved step throughput
- better use of already-deterministic iteration order where safe

---

## 5.7 Engine-level profiling and phase observability
The refactor introduced explicit profiling for:

- movement
- interaction
- biology
- commit

and commit subprofiling for:

- setup
- deaths
- births
- resource regrowth

### Impact
- performance bottlenecks are now measurable
- optimization can be targeted rather than speculative
- the engine is more maintainable and diagnosable

---

## 6. Measured Impact

## 6.1 Benchmark comparison

### Legacy abundant run (`gamma = 1`)
- **Batch duration:** `1682.87s`
- **Final population:** `428`
- **Tail mean population:** `417.346`

### Current abundant run (`gamma = 1`)
- **Batch duration:** `19.47s`
- **Final population:** `429`
- **Tail mean population:** `416.742`

### Current abundant run (`gamma = 0.1`)
- **Batch duration:** `43.78s`
- **Final population:** `429`
- **Tail mean population:** `416.742`

---

## 6.2 Performance gains

### Comparable case (`gamma = 1`)
Legacy → current:
- `1682.87s → 19.47s`
- **~86.4× speedup**

### Alternate current benchmark
Legacy → current (`43.78s`):
- `1682.87s → 43.78s`
- **~38.4× speedup**

These are not marginal gains. They represent the removal of a severe structural performance defect.

---

## 6.3 Behavioral stability

Despite the runtime improvements, the macroscopic regime behavior remained broadly stable:

- final population stayed effectively unchanged
- tail mean population stayed effectively unchanged
- extinction rate unchanged
- cap-hit rate unchanged
- birth/death ratio unchanged
- time-series variability stayed similar

This suggests the performance gains came primarily from implementation improvements rather than from qualitative simulation drift.

---

## 6.4 Current phase profile (`gamma = 1` run)

### Batch phase profile
- movement: `3.460s`
- interaction: `1.027s`
- biology: `0.645s`
- commit: `14.269s`

### Commit breakdown
- setup: `0.014s`
- deaths: `0.245s`
- births: `13.924s`
- resource regrowth: `0.066s`

### Interpretation
The birth path is still the dominant hotspot, but its absolute cost has been reduced dramatically.

This is an important result:

The refactor did **not** move the bottleneck elsewhere.  
It successfully reduced the cost of the true bottleneck.

---

## 7. Architectural Impact

The refactor improved more than raw speed.

## 7.1 Clearer phase structure
The engine is now much easier to reason about as an explicit sequence of:

- movement
- interaction
- biology
- commit

This is the correct shape for a simulation core intended to grow.

## 7.2 Better separation of execution and analytics
Metrics, summaries, phase profiles, and plotting concerns are increasingly separated from the core simulation path.

That is essential for future validation and regime classification work.

## 7.3 Improved Stage III readiness
The current architecture is much more suitable for:

- occupancy metrics
- richer local interaction measurements
- classified regimes as stable CLI entry points
- pytest-based regime validation
- future subsystem growth without rebreaking the loop

---

## 8. Remaining Technical Debt

The performance crisis is resolved, but the pre–Stage III freeze still requires cleanup.

## 8.1 Births remain the dominant runtime cost
The birth path is much cheaper than before, but still dominates total runtime in abundant runs.

This is no longer an emergency, but it remains the main performance frontier if future optimization becomes necessary.

## 8.2 Fine-grained birth subprofile is not yet trustworthy
Current output shows:
- `seed_creation = 0.000`
- `agent_creation = 0.000`
- `dict_insertion = 0.000`

while total birth cost remains large.

This means the deepest birth-subphase instrumentation is not yet accurately wired or resolved enough to explain the remaining cost.

## 8.3 Plotting path needs alignment with world-view collection
The lightweight plotting option still needs cleanup and better integration with optional world-view collection.

## 8.4 Occupancy metrics need reimplementation
These are still missing and need to be restored before the pre–Stage III freeze if they are part of the intended validation / visualization workflow.

## 8.5 CLI / `main.py` cleanup remains
The experiment surface is close, but still needs cleanup to become a stable command-level interface for classified regimes.

## 8.6 Regime validation suite must be aligned with current registry
The pytest validation system should reflect the current regime names and current empirical outputs, not older assumptions.

## 8.7 Documentation lags the codebase
The architecture and performance story have changed significantly. Docs should be updated before freezing this version.

---

## 9. Assessment of the Rewrite

This rewrite was justified.

The 2D world and closer energy coupling exposed structural weaknesses that would have made further expansion increasingly inefficient and difficult to validate. The old architecture could still execute, but it was not well shaped for sustained growth.

The refactor solved that by:

- specializing the most expensive path
- restoring a clean phase structure
- improving performance observability
- reducing hot-path reporting overhead
- making the engine viable again for long-horizon experimentation

This should be understood not as wasted time, but as a necessary architectural reset.

---

## 10. Recommended Pre–Stage III Freeze Checklist

Before freezing the pre–Stage III version, the highest-value remaining tasks are:

1. clean `main.py` and stabilize regime command entry points  
2. update lightweight plotting and align it with optional world-view collection  
3. reintroduce occupancy metrics  
4. finalize classified regimes as user-facing commands  
5. migrate regime validation into the pytest module  
6. update documentation to reflect the current architecture and performance improvements  
7. freeze the version as the stable pre–Stage III baseline  

---

## 11. Final Conclusion

The performance issue that emerged after the 2D-world / energy-coupling transition was severe enough that it had to be addressed before Stage III.

That intervention succeeded.

The current engine is:

- **dramatically faster**
- **architecturally clearer**
- **more observable**
- **more suitable for validation**
- **much closer to a proper expansion base**

The key technical result is that abundant 5000-tick runs improved from **1682.87s** to **19.47s** in the comparable `gamma=1` case while preserving essentially the same macroscopic regime behavior.

That makes the present snapshot a strong candidate for a **pre–Stage III freeze**, once the remaining cleanup, plotting, occupancy metrics, validation alignment, and documentation updates are completed.