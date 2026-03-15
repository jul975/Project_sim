# Current Project State (March 2026)

## Overview
The Ecosystem Emergent Behavior Simulator is in Stage II (beta v0.2) with a deterministic simulation core, controlled ecological dynamics, and comprehensive validation coverage. The project is transitioning toward Stage III with planned work on explicit spatial interactions.

**Last Updated:** March 15, 2026  
**Current Version:** beta v0.2  
**Next Target:** v0.3 (Stage III)

## Project Status

### ✅ Completed & Stable
- **Deterministic simulation kernel**
  - Reproducible state trajectories with fixed seeds
  - Canonical state hashing via SHA256
  - Snapshot/restore continuation equivalence
  - Isolated RNG streams (world, movement, reproduction, energy)

- **Ecological model**
  - 1D toroidal world with fertility/resource fields
  - Energy-gated movement, reproduction, harvesting, and death
  - Bounded resource regeneration with configurable rates
  - Population capacity enforcement

- **Batch execution infrastructure**
  - Multi-run orchestration via `Runner` class
  - Automatic seed sequence generation from master seed
  - Per-tick metrics collection via `SimulationMetrics`
  - Tail-window fingerprint analysis and regime classification

- **Validation framework**
  - Determinism checks (same seed → same trajectory)
  - Snapshot round-trip equivalence
  - Structural invariants (position bounds, ID consistency, caps)
  - RNG isolation tests
  - Stable regime behavioral validation

- **CLI interface**
  - Experiment execution: `python -m engine_build.main experiment`
  - Validation runners: `python -m engine_build.main validate`
  - Batch execution with configurable seed/runs/ticks
  - Optional visualization (population plots, development figures)

### 🔄 In Transition
- **Regime definitions**
  - Transitioned from `extinction`/`stable`/`saturated` → `stable`/`test_stable`/`fragile`/`abundant`
  - Behavioral classification framework in place but not yet fully integrated
  - Legacy validation tests pending refactor to match current regime set

- **Test coverage**
  - Currently tests "stable" regime validation actively
  - "fragile" and "abundant" regime tests pending threshold definition
  - Post-hoc classification ready but not yet gated in validation suite

### ⏳ Not Yet Implemented (Stage III+)

- **Explicit spatial interactions**
  - Current: implicit competition via resource depletion and update order
  - Planned: crowding rules, collision detection, local competition mechanics

- **Trait heterogeneity** (Stage IV)
  - Currently: homogeneous agents
  - Planned: trait schema, inheritance, mutation, selection dynamics

- **2D topology** (optional Stage III path)
  - Currently: 1D wrapped topology
  - Planned: optional 2D world extension

- **Advanced analytics** (Stage V)
  - Regime boundary mapping
  - Early-warning signal detection
  - Predictive/inference pipelines
  - Benchmark and reproducibility manifest standards

## Regime Set (Current)

| Regime | Use Case | Characteristics |
|---|---|---|
| `stable` | Default baseline | Bounded population, moderate growth, low extinction |
| `test_stable` | Fast validation | Tighter energy budget, fewer long-running experiments |
| `fragile` | Collapse testing | Tight energy/resource constraints, higher extinction |
| `abundant` | Growth testing | High resources, relaxed energy, saturation dynamics |

**Configuration:** See [engine_build/regimes/registry.py](../../engine_build/regimes/registry.py) for parameter details.

## Known Limitations & Gaps

1. **Regime validation inconsistency**
   - Tests reference "extinction"/"saturated" regimes not in current registry
   - Pending refactor to align test suite with current regime set

2. **Behavioral classification not enforced**
   - Post-hoc classification via `classify_regime()` works but isn't gated in execution
   - Stage III should integrate classification into validation flow

3. **Spatial structure minimal**
   - 1D topology limits realism
   - No explicit agent-agent interactions
   - No clustering/occupancy metrics yet

4. **Documentation lag**
   - v0.2 release notes document old regime names
   - This file documents current interim state (transition period)

## Quality Gates & Policies

**All merges affecting simulation logic must:**
- Pass determinism test suite
- Maintain snapshot continuation equivalence
- Define and test new invariants
- Preserve canonical state hash (or document intentional change)
- Update documentation to reflect behavior changes

**Release criteria:**
- All validation suites green
- Baseline artifacts updated
- Change notes explain any hash changes
- Documentation is current and tested

## Navigation

- **Running experiments:** See [README.md](../../README.md#running-experiments)
- **Validation workflow:** See [README.md](../../README.md#validation)
- **Strategic roadmap:** See [ROADMAP.md](ROADMAP.md)
- **Architecture details:** See [docs/canonical_docs/ARCHITECTURE.md](../canonical_docs/ARCHITECTURE.md)
- **Episode validation logic:** See [docs/canonical_docs/EXPERIMENTS.md](../canonical_docs/EXPERIMENTS.md)

## Next Immediate Actions (Priority Order)

1. **Refactor regime validation tests** to use current regime names
2. **Define fragile/abundant validation thresholds** based on empirical runs
3. **Document Stage III interaction model** design before implementation
4. **Integrate post-hoc classification** into validation gates
5. **Create v0.3 baseline artifacts** once Stage III feature set stabilizes
