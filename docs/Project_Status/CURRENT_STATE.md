# Current Project State (March 2026)

## Overview
The Ecosystem Emergent Behavior Simulator is in **active pre-Stage III development** with rapid iteration and continuous refactoring. Recent work (100+ commits in ~4 weeks) transitioned the world model from 1D to 2D topology and decoupled energy initialization from agent core logic. The codebase provides a determinism-preserving foundation for explicit spatial interactions, suitable for experimental work but subject to ongoing architectural improvements.

**Last Updated:** March 15, 2026  
**Current Version:** beta v0.2.1 (post-refactor, actively developed)  
**Commit Velocity:** 100+ commits in ~4 weeks (rapid iteration phase)  
**Next Target:** v0.3 (Stage III - Explicit Interaction and Spatial Competition)

## Development Approach

This project employs **continuous refactoring with determinism-preserving principles**:
- Frequent commits capture experimental and stabilization work
- Major architectural changes (1D→2D, energy decoupling) delivered incrementally
- Deterministic reproducibility maintained as non-negotiable constraint throughout
- High commit frequency reflects active problem-solving and optimization, not instability
- All changes validated against determinism suites before merge

**Timeline Expectations:** Given the active development pace and ongoing optimization work, delivery timelines for Stage III and beyond should be considered provisional and subject to adjustment as discoveries emerge.

## Project Status

### ✅ Recently Completed & Determinism-Verified

**Major Systems Refactoring (Pre-Stage III, March 8-15, 2026)**

This week's work transitioned the core engine architecture to support 2D spatial models while maintaining deterministic reproducibility. These changes are now in daily use but remain subject to optimization refinement.

- **2D World Model Implementation** (completed, active optimization)
  - Replaced 1D wrapped topology with 2D (height × width) grid system
  - Fertility and resource fields refactored to 2D numpy arrays
  - Agent positions now `(x, y)` tuples enabling neighborhood-based queries
  - Toroidal boundary wrapping updated for 2D semantics
  - Deterministic state serialization verified across topology transition
  - All position-based invariants re-validated for 2D space
  - **Note:** Performance still being optimized; 15-20min batch runs currently, <5min target

- **Decoupled Energy System Architecture** (completed, usage patterns emerging)
  - Agent initialization restructured into four phases:
    - `_init_identity()` — agent ID and lineage setup
    - `_init_lineage()` — RNG seed sequence management
    - `_init_rngs()` — spawn domain-specific RandomGenerators
    - `_init_state()` — energy, position, and lifecycle initialization
  - Each phase independently measurable for performance profiling
  - Energy parameters now separately configurable from agent identity
  - Prepares foundation for heterogeneous agent traits (Stage IV)
  - **In-progress:** Agent creation identified as bottleneck; optimization underway

- **Agent Factory Pattern** (completed, integrated into workflows)
  - Extracted agent creation into `agent_factory.py` module
  - Dual code paths optimized for initial population vs. newborn reproduction
  - Cleaner separation between engine orchestration and agent construction
  - Performance measurement integrated at factory level

- **Performance Profiling Framework** (completed, actively generating insights)
  - Implemented `PerfSink` abstraction in `dev/perf.py`
  - `measure_block()` utility enables fine-grained bottleneck tracking
  - Agent initialization identified as primary performance constraint (~70% of batch time)
  - Framework supports iterative optimization without breaking determinism
  - Metrics pipeline enhanced to capture performance data per batch

- **State Serialization & Snapshots Updated** (completed, fully validated)
  - Schema refactored to handle 2D agent positions
  - State hash verified unchanged (determinism preserved)
  - Snapshot/restore round-trip tested post-refactoring
  - All structural invariants re-validated with new topology

**Pre-Refactor Capabilities (Preserved & Extended)**

- **Deterministic simulation core** (stable, post-refactoring verified)
  - Reproducible state trajectories with fixed seeds (verified post-refactoring)
  - Canonical state hashing via SHA256 remains gold standard
  - Snapshot/restore continuation equivalence maintained
  - Isolated RNG streams (world, movement, reproduction, energy)

- **Ecological model dynamics** (stable, now 2D)
  - 2D toroidal world with fertility/resource fields (newly implemented)
  - Energy-gated movement, reproduction, harvesting, and death pathways
  - Bounded resource regeneration with configurable rates
  - Population capacity enforcement with 2D occupancy checks

- **Batch execution infrastructure** (stable, extended for 2D)
  - Multi-run orchestration via `Runner` class
  - Automatic seed sequence generation from master seed
  - Per-tick metrics collection via `SimulationMetrics`
  - Tail-window fingerprint analysis and regime classification

- **Validation framework** (stable, extended for 2D)
  - Determinism checks verified post-refactoring
  - Snapshot round-trip equivalence tested
  - Structural invariants extended for 2D topology (position bounds, neighbors, caps)
  - RNG isolation tests passing
  - Stable regime behavioral validation

- **CLI interface** (stable, unchanged)
  - Experiment execution: `python -m engine_build.main experiment`
  - Validation runners: `python -m engine_build.main validate`
  - Batch execution with configurable seed/runs/ticks
  - Optional visualization support

### 🔄 In Transition & Refinement

- **Regime validation suite**
  - Tests currently reference legacy regime names (extinction/saturated)
  - Pending refactor to use current regime set (stable/fragile/abundant)
  - Behavioral classification framework in place, not yet enforced in validation gates
  - Post-hoc classification via `classify_regime()` ready for integration

- **Performance optimization roadmap**
  - Agent initialization identified as critical path
  - Next phase: systematic optimization of spawn/initialization sequence
  - Goal: reduce batch run time to <5min for 1000-tick baseline
  - Maintains determinism throughout optimization work

- **Metrics pipeline refinement**
  - Recently restructured to support performance profiling
  - Pending integration of 2D-specific metrics (occupancy patterns, neighborhood effects)
  - Regime fingerprints working, Stage III will extend for spatial patterns

### ⏳ Next Priority (Stage III Ready)

**Explicit Spatial Interactions** — Foundation Now Ready
  - **Why ready**: 2D topology complete, neighborhood queries now possible
  - **What's needed**: collision/crowding rules, local competition mechanics
  - **Implementation path**: Minimal changes to core loop, localized to movement/interaction phase
  - **Validation**: Existing determinism suite extends naturally to collision mechanics

**Additional Stage III Candidates**
  - Optional local interaction metrics (clustering, territory formation)
  - Spatial occupancy statistics for fingerprinting
  - Distance-aware resource competition (local vs. global)

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

1. **Regime validation test inconsistency** (in progress)
   - Tests reference "extinction"/"saturated" regimes removed from registry
   - Requires refactoring test suite to use current regime names
   - Fix priority: medium (code cleanup, not blocking functionality)

2. **Performance optimization ongoing**
   - Agent initialization bottleneck identified
   - Current batch runtime ~15-20 min for 1000-tick × 10-run experiments
   - Optimization roadmap in place, implementations pending

3. **2D spatial metrics not yet captured**
   - Grid topology now available, but occupancy/clustering metrics not integrated
   - Fingerprint analysis still uses legacy 1D-era metrics
   - Stage III will extend metrics for spatial patterns

4. **Behavioral classification not enforced**
   - Post-hoc classification framework exists but isn't gated in validation
   - Validation still uses hardcoded threshold checks
   - Pending integration in validation refactor

5. **No explicit agent-agent interactions yet**
   - 2D topology enables them but not yet implemented
   - Competition remains implicit (resource depletion + update order)
   - Core Stage III deliverable

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

1. **Refactor regime validation tests** (code cleanup)
   - Update test suite to use current regime names (stable/fragile/abundant)
   - Verify all determinism checks pass with new regime set
   - ~2-4 hour task, no logical changes

2. **Define validation thresholds for fragile and abundant regimes**
   - Run empirical baseline for each regime
   - Extract fingerprint statistics (extinction_rate, cap_hit_rate, etc.)
   - Define pass/fail thresholds based on distribution
   - ~4-6 hour empirical work

3. **Optimize agent initialization performance**
   - Profile each `_init_*` phase using PerfSink data
   - Target: reduce per-agent initialization time by 30-50%
   - Maintain determinism throughout
   - ~1-2 days development time

4. **Extend metrics for 2D spatial patterns**
   - Add occupancy distribution tracking
   - Implement neighborhood density metrics
   - Enable clustering/patterning analysis
   - Foundation for Stage III validation

5. **Design Stage III spatial interaction mechanics**
   - Document collision/crowding rules
   - Specify local competition alternatives
   - Define new invariants for interaction model
   - Before implementation: ~4-6 hours design work

6. **Create v0.3 development branch**
   - Checkpoint current stable state
   - Begin Stage III feature development
   - Keep main branch at v0.2.1 (post-refactor baseline)
