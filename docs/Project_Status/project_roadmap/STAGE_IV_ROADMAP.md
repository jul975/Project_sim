# Stage IV Roadmap

## Trait Variation, Inheritance, and Selection

**Target line:** `v0.4 -> v0.6`  
**Project:** Ecosystem Emergent Behavior Simulator  
**Status assumption:** Stage III ecological baseline is stable enough to support traitful agents without reopening core engine semantics.

---

## 1. Stage IV purpose

Stage IV upgrades the simulator from a **homogeneous ecological system** to a **heterogeneous, heritable ecological system**.

The core shift is:

- from one agent template with shared ecological rules
- to populations with explicit trait variation
- where traits are inherited, may mutate, and can be differentially favored under ecological pressure

This stage is not about adding broad ML complexity or turning the simulator into a general optimization platform. Its purpose is narrower and more foundational:

> establish a deterministic evolutionary layer on top of the stabilized ecological engine.

---

## 2. Why Stage IV exists

Stage I–III establish the core modeling substrate:

- deterministic stepping
- canonical state and snapshot logic
- explicit ecological phase ordering
- resource-mediated ecology
- reproducible experiments
- structured metrics and analysis pathways

That baseline is necessary but not yet sufficient for studying selection-like processes.

Stage IV exists to make the simulator capable of expressing the three minimum conditions needed for evolutionary change:

1. **variation**
2. **heritability**
3. **differential ecological consequence**

Only once those three are present can the simulator move from:

- ecological fluctuation only

to:

- ecology plus trait dynamics under selection.

---

## 3. Stage IV scope

### In scope

- explicit agent trait state
- deterministic inheritance
- bounded mutation
- ecological coupling of traits to existing engine phases
- trait-aware metrics and summaries
- controlled selection experiments
- release-quality evolutionary baseline documentation

### Out of scope

The following belong to later work unless strictly required:

- reinforcement learning agents
- learned policies
- inverse parameter inference
- collapse prediction ML
- learned transition operators
- large multi-species trophic expansion
- genotype-heavy recombination systems
- broad platformization / dashboard work

Stage IV is not the “advanced AI” stage.  
It is the **traitful ecology** stage.

---

## 4. Stage IV success definition

Stage IV is complete when all of the following are true:

1. agents carry explicit trait state in the canonical runtime model
2. trait state is serialized, hashed, and restored through snapshots
3. offspring inherit parent traits deterministically under fixed seed/state
4. mutation is explicit, bounded, and reproducible
5. at least one trait affects ecological outcomes through existing engine phases
6. at least one controlled experiment shows an interpretable shift in trait distribution under ecological pressure
7. all of the above remain compatible with determinism, replay, and batch analysis

---

## 5. Working principles

### 5.1 Determinism remains the hard constraint

All trait logic must preserve the project’s reproducibility contract.

New randomness must:

- come only through controlled RNG pathways
- be restorable from snapshot state
- never introduce hidden entropy
- never bypass canonical state machinery

### 5.2 Traits are canonical state, not metadata

Once introduced, traits are part of the actual simulator state.

They must therefore be represented in:

- runtime agent state
- snapshots
- hashing / canonical serialization
- validation logic
- experiment manifests where relevant

### 5.3 Traits must map to ecology

A trait is valid only if it changes something ecologically meaningful.

Bad Stage IV traits:

- decorative labels
- traits with no engine consequence
- traits added “for future ML”

Good Stage IV traits:

- movement cost modifiers
- harvest efficiency modifiers
- reproduction threshold modifiers
- mortality / resilience modifiers
- sensory or competition modifiers

### 5.4 Add one degree of freedom at a time

Do not introduce many interacting trait systems simultaneously.

Stage IV should progress by controlled increments:

- one trait
- then inheritance
- then mutation
- then ecological coupling
- then experiments

### 5.5 Keep phenotype-level inheritance first

Stage IV does not require a full genotype/phenotype architecture.

A phenotype-level trait vector is sufficient for this stage, provided it is:

- explicit
- inheritable
- mutable
- ecologically active
- analyzable

A deeper genetic architecture can be introduced later only if justified.

---

## 6. Stage IV release map

- **Stage IV.A** — Trait-capable state model (`v0.4.0a*`)
- **Stage IV.B** — Deterministic inheritance and mutation (`v0.4.x`)
- **Stage IV.C** — Trait-to-ecology coupling (`v0.5.0a*`)
- **Stage IV.D** — Trait analytics and lineage observation (`v0.5.x`)
- **Stage IV.E** — Controlled selection experiments (`v0.6.0a*`)
- **Stage IV.F** — Stabilized evolutionary baseline (`v0.6`)

---

# 7. Stage IV.A — Trait-capable state model

## Release target: `v0.4.0a*`

### Objective

Extend the canonical simulator state so agents can carry explicit trait values without breaking the current engine.

### Deliverables

- introduce a first-class trait container
  - e.g. `TraitState`, `TraitVector`, or equivalent
- add trait state to agent runtime state
- define trait defaults for existing homogeneous regimes
- extend snapshot and restore paths to include trait state
- extend state hashing / canonical serialization to include trait state
- update analysis contracts where trait fields may appear later
- ensure older regime logic remains runnable through default trait values

### Recommended initial trait surface

Keep the first trait set deliberately small.

Candidate examples:

- `metabolic_rate_scale`
- `harvest_efficiency`
- `reproduction_threshold_scale`
- `movement_cost_scale`

These are preferable because they already map naturally onto the current ecological model.

### Acceptance criteria

- same initial seed + same trait initialization => identical trajectory
- changing a trait value changes canonical state hash
- snapshot -> restore preserves trait state exactly
- old traitless regimes still run through default values
- trait fields remain within declared bounds and dtypes

---

# 8. Stage IV.B — Deterministic inheritance and mutation

## Release target: `v0.4.x`

### Objective

Move from static heterogeneity to heritable heterogeneity.

### Deliverables

- define inheritance path from parent to child trait state
- define mutation operator for each supported trait
- document:
  - mutation probability
  - mutation magnitude
  - clamping rules
  - valid ranges
  - dtype / precision rules
- ensure child-trait construction happens in one explicit place
- ensure mutation uses only controlled RNG streams

### Design rule

Mutation must be:

- explicit
- local
- bounded
- deterministic under fixed seed/state
- snapshot-compatible

### Acceptance criteria

- inheritance works with mutation disabled
- inheritance + mutation remains deterministic under replay
- mutation never escapes declared trait bounds
- child traits are reconstructible from canonical state and RNG path
- validation tests cover both inheritance-only and inheritance+mutation paths

---

# 9. Stage IV.C — Trait-to-ecology coupling

## Release target: `v0.5.0a*`

### Objective

Ensure traits have real causal consequences inside the ecological engine.

### Deliverables

Wire selected traits into existing explicit phases.

#### Movement phase

Possible trait hooks:

- movement cost scaling
- directional bias intensity
- mobility / step efficiency

#### Interaction phase

Possible trait hooks:

- harvest efficiency
- competitive share under crowding
- local encounter advantage

#### Biology phase

Possible trait hooks:

- reproduction threshold scaling
- fecundity modifier
- post-reproduction survival tradeoff

#### Death / survival logic

Possible trait hooks:

- starvation tolerance
- energy reserve efficiency
- age-related vulnerability modifiers

### Constraint

Do not solve this by smearing trait logic everywhere.

The preferred pattern is:

- trait data lives on agent state
- phase logic reads it explicitly
- the engine remains legible about where trait effects occur

### Acceptance criteria

- at least two traits affect ecological outcomes in measurable ways
- trait effects are visible in metrics, not only visually
- traitless vs traitful runs can be compared under matched seeds/configs
- phase ownership remains understandable and documented

---

# 10. Stage IV.D — Trait analytics and lineage observation

## Release target: `v0.5.x`

### Objective

Make trait dynamics observable, inspectable, and batch-comparable.

### Deliverables

Add trait-aware observation outputs such as:

- mean trait value over time
- variance / dispersion over time
- histogram snapshots
- trait-by-fitness proxy summaries
- trait-by-regime summaries
- optional lineage summaries where feasible

### Minimum useful outputs

For each run:

- trait means
- trait variances
- population-wide trait distributions
- birth and death summaries conditioned on trait values

For each batch:

- run-aggregated trait trajectories
- final trait distribution summaries
- extinction/survival correlations by trait profile
- regime-level comparison surface

### Notes

Lineage tracking should remain lightweight unless it is already structurally cheap.
Do not build a heavy genealogy system unless the current architecture clearly supports it.

### Acceptance criteria

- trait distributions can be inspected without ad hoc one-off scripts
- batch experiments can summarize trait change cleanly
- trait metrics are documented and biologically interpretable
- added analytics do not compromise reproducibility

---

# 11. Stage IV.E — Controlled selection experiments

## Release target: `v0.6.0a*`

### Objective

Demonstrate actual selection-like behavior rather than mere mutation noise.

### Deliverables

Define 2–3 explicit experiment families with clear hypotheses.

## Experiment family 1 — Resource scarcity selection

**Question:**  
Do low-resource regimes favor lower metabolic cost or better harvest efficiency?

**Expected pattern:**  
Traits reducing energetic burden or improving resource capture should become relatively more common under scarcity.

## Experiment family 2 — Crowding / competition selection

**Question:**  
Do dense populations favor traits that improve local competition outcomes?

**Expected pattern:**  
Traits affecting local harvest share, movement efficiency, or encounter outcomes may rise under sustained crowding.

## Experiment family 3 — Reproductive tradeoff selection

**Question:**  
Does lower reproduction threshold provide short-term growth but long-term instability?

**Expected pattern:**  
Certain aggressive reproductive traits may dominate in expansion phases but underperform in stability/survival terms.

### Experiment design requirements

Each controlled experiment should define:

- hypothesis
- regime/config
- initial trait distribution
- seed policy
- measured outputs
- comparison method
- failure interpretation

### Acceptance criteria

- at least one experiment shows directional trait change that is reproducible
- the observed shift is interpretable in ecological terms
- the result can be reproduced from a documented config + seed policy
- output is good enough for inclusion in future reports / writeups

---

# 12. Stage IV.F — Stabilized evolutionary baseline

## Release target: `v0.6`

### Objective

Freeze a clean traitful-ecology baseline before broader Stage V work.

### Deliverables

- release-quality Stage IV documentation
- updated architecture overview for traitful agents
- updated validation suite for trait invariants
- explicit statement of supported Stage IV trait mechanisms
- documented Stage IV experiment set
- release note / summary of `v0.6`

### Stage IV definition of done

Stage IV is done when:

- trait state is canonical
- inheritance is deterministic
- mutation is bounded and reproducible
- trait effects are ecologically meaningful
- trait analytics are available
- controlled selection experiments are documented
- snapshot/replay guarantees still hold
- the codebase is ready for Stage V without redesigning the trait layer

---

# 13. Cross-cutting engineering requirements

## 13.1 Canonical state updates

Any new trait field must be integrated into:

- runtime state
- serialization schema
- hashing logic
- snapshot schema
- restore path
- validation checks

## 13.2 Test requirements

Stage IV requires tests for:

- trait serialization round-trip
- trait hash sensitivity
- inheritance determinism
- mutation determinism
- mutation bounds
- trait/ecology coupling correctness
- batch-level repeatability under fixed seed policy

## 13.3 Documentation requirements

Every trait introduced must be documented in one place with:

- meaning
- units or scale
- valid range
- default value
- mutation rule
- ecological effect location
- expected tradeoff

## 13.4 Performance discipline

Trait support must not become an excuse for premature architecture inflation.

Prefer:

- simple scalar trait fields
- clear deterministic logic
- minimal extra allocation
- observable causal effects

Avoid:

- heavy meta-abstraction before evidence of need
- broad generalized evolution frameworks
- opaque “future-proof” layers with no present role

---

# 14. Risks and anti-patterns

## Risk 1 — Trait explosion

Too many traits introduced too early will make Stage IV uninterpretable.

**Mitigation:**  
Start with a very small trait surface.

## Risk 2 — Non-canonical trait handling

Storing traits only in analytics or metadata will break determinism and snapshots.

**Mitigation:**  
Treat traits as true runtime state from the beginning.

## Risk 3 — Mutation without meaning

Adding mutation before ecological coupling creates noise, not evolutionary dynamics.

**Mitigation:**  
Ensure traits matter ecologically before claiming selection behavior.

## Risk 4 — Reopening Stage III boundaries

Trait work may tempt refactors of engine/world/spatial boundaries that should already be stable enough.

**Mitigation:**  
Treat Stage III engine semantics as frozen unless a trait requirement exposes a real architectural flaw.

## Risk 5 — Premature ML drift

Once traits exist, it is tempting to jump directly into learning systems.

**Mitigation:**  
Hold Stage IV to variation + heredity + selection only.

---

# 15. Immediate priorities before or at Stage IV start

The Stage IV entry gate should be:

1. confirm Stage III baseline is stable enough
2. introduce trait-capable canonical state
3. prove snapshot/hash compatibility
4. add deterministic inheritance
5. add bounded mutation
6. couple one or two traits to existing ecology
7. run first controlled selection experiments
8. freeze `v0.6` traitful ecology baseline

---

# 16. Short version

Stage IV is the stage where the simulator becomes capable of modeling:

- heterogeneous agents
- inherited trait structure
- bounded mutation
- ecological tradeoffs
- reproducible selection dynamics

It is complete when those capabilities exist **without sacrificing determinism, interpretability, or experimental clarity**.

---

# 17. Post-Stage-IV direction

Once Stage IV is frozen, later work can safely expand toward:

- richer regime mapping
- deeper evolutionary analysis
- early warning and collapse diagnostics
- ML-facing analysis infrastructure
- broader research-platform capabilities

But those belong after the traitful ecological baseline is stable.

---
