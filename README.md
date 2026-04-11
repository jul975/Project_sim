# Festina Lente

**Festina Lente** or "make haste slowly" was one of the favorite motto's of Caesar Augustus.

It's a reminder that in order to make progress, we need to take our time to build a solid foundation, in order to move forward more steadily. Keeping momentum without loosing scope and direction.

## Ecosystem Emergent Behavior Simulator

**Figure 1.** Emergent behavior in a flock of birds.
![Alt text](docs/images/birds_geo.png)

Emergent Behavior is the apparent result of simple rules being followed by individuals in a system, leading to complex and often unpredictable patterns at the level of the group.

Like a flock of birds flying together in a seemingly coordinated manner, even though each bird is only following simple rules of avoiding collisions and staying close to neighbors.

Every level of our complex world can be seen as a result of emergent behavior. From simple rules of physics, we get chemistry, from simple rules of chemistry we get biology, and from simple rules of biology we get behavior of animals, and so on...

Once you conceptualize this phenomenon, you'll start to see it everywhere. From the traffic patterns in cities, to the price of goods in the economy, to the behavior of people in social media.

This project tries to emulate such behavior in a simple ecosystem with two species, prey and predators. The goal is to study the behavior of the system and how it changes when we modify the rules of the game.

## Dynamic overview

<table align="center">
  <tr>
    <td align="center" width="48%">
      <strong>Figure 1.</strong> Place-holder stable dynamics visuals<br/>
      <img src="docs/video/updated_dynamics24.gif" alt="Place-holder stable dynamics visuals" width="100%" />
    </td>
    <td align="center" width="48%">
      <strong>Figure 2.</strong> Place-holder collapse dynamics visuals<br/>
      <img src="docs/video/COLLAPSE_GIF.gif" alt="Place-holder collapse dynamics visuals" width="100%" />
    </td>
  </tr>
</table>

In it's current state, the simulator creates a 2d world where each world field has a certain fertility level. The fertility level determines how much resources the resource field can regenerate each turn.

Each tick, the agents move, harvest resources, reproduce and/or dies. Agents have a certain energy level, . The energy level is depleted each turn and is replenished by harvesting resources. If the energy level reaches zero, the agent dies.

## Conceptual view

Deterministic multi-agent ecology simulator for reproducible experiments on a 2D toroidal resource landscape.

The simulator is a **discrete-time stochastic state-transition system**.

At each tick, it takes the current global state, applies a fixed update schedule, consumes controlled randomness, and produces the next state.

$$S_{t+1} = F(S_t, \xi_t; \theta)$$

Where:

- $S_t$ = full simulator state at time $t$
- $\xi_t$ = stochastic input at tick $t$
- $\theta$ = parameter set / regime configuration
- $F$ = simulator transition operator

---

The system runs for a given amount of 'ticks', where each tick represents a unit of time or 'change', controlled and orchestrated by the engine.

The engine makes a 'step' in time for each tick. Where a step can be formalized as the Transition operator T.

The T operator takes the current state of the system and applies a set of rules to determine the next state. The rules are applied in a specific order, which is defined by the engine. The order is as follows:

1. Movement Phase

    - Agents die of old age.
    - Agents move to a neighboring cell.
    - Agents pay the metabolic cost of movement.
    - if agent energy level <= 0, agent dies of metabolic starvation.

2. Interaction Phase

    - Spatial index is updated.
    - Agents harvest resources from local field, sharing the harvest according to the number of agents in the local field.
    - Agents die of starvation if they don't have enough energy.

3. Biology Phase

    - Agents reproduce with a certain probability.
    - if agent energy level <= 0, agent dies of reproduction.
    - Agents age.

4. Commit phase

    - Births are committed.
    - Deaths are committed.
    - Resources regrow according to fertility.

The T operator is deterministic, meaning that given the same initial state, it will always produce the same output. This is achieved by using a pseudo-random number generator (PRNG) that is initialized with a seed value. The seed value is the only source of randomness in the system.

## Current state

As of March 23, 2026, the repository is at package version `0.3.0a0` and represents the current pre-Stage III / pre-`v0.3` freeze candidate. The 2D engine transition is live, determinism is still a hard constraint, and the main public surface is a small CLI for experiments plus suite-based verification and validation.

## Current Baseline (Stage III)

### What's Stable

- **2D toroidal world** with fertility and resource fields
- **Deterministic execution** with canonical state hashing and snapshot continuation
- **Isolated RNG streams** for world, movement, reproduction, and energy
- **Phase-structured tick loop**: movement → interaction → biology → commit
- **Batch analytics** with per-run metrics, fingerprints, and regime classification
- **Optional instrumentation**: performance profiling, world-frame capture, plotting

### Command Surface

```bash
python -m FestinaLente.main experiment --regime <name> [--runs N] [--ticks T] [--seed S] [--plot] [--tail-fraction F]
python -m FestinaLente.main verify --suite <all|determinism|invariants|rng|snapshots>
python -m FestinaLente.main validate --suite <all|contracts|separation>
python -m FestinaLente.main menu
```

### Named Regimes

| Regime | Behavior |
|--------|----------|
| `stable` | Balanced birth/death cycles |
| `fragile` | Stressed but usually surviving |
| `abundant` | Permissive growth |
| `saturated` | Population bottleneck |
| `collapse` | Low regeneration, systemic failure |
| `extinction` | High failure rate |

### Design Decisions

- No per-agent `SeedSequence` lineage tree; RNGs derived from deterministic identity words
- No per-tick agent re-sorting; encounter order preserved via Python dict insertion order
- No crowding / collision rules yet (planned post-freeze extension)

## Setup & Usage

### Installation

```bash
git clone https://github.com/jul975/FestinaLente.git
cd FestinaLente
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m pip install -r requirements.txt
```

Python >= 3.11 required ([from pyproject.toml](pyproject.toml)).

### Quick Examples

**Baseline stable regime:**
```bash
python -m FestinaLente.main experiment --regime stable
```

**Custom parameters:**
```bash
python -m FestinaLente.main experiment --regime abundant --runs 5 --ticks 500 --seed 42
```

**With analysis tuning:**
```bash
python -m FestinaLente.main experiment --regime collapse --runs 10 --ticks 2000 --tail-fraction 0.1
```

**With performance profiling:**
```bash
python -m FestinaLente.main experiment --regime saturated --perf-flag
```

**Interactive menu:**
```bash
python -m FestinaLente.main menu
```

### Verification & Validation

```bash
# Via CLI (routes to pytest)
python -m FestinaLente.main verify --suite all
python -m FestinaLente.main validate --suite all

# Direct pytest
python -m pytest tests/verification
python -m pytest tests/validation
```

## Documentation Map

**Essential references:**
- [ARCHITECTURE.md](docs/canonical_docs/ARCHITECTURE.md) — system structure and phase flow
- [MATHEMATICAL_MODEL.md](docs/canonical_docs/MATHEMATICAL_MODEL.md) — State-transition formalism
- [RNG_ARCHITECTURE.md](docs/canonical_docs/RNG_ARCHITECTURE.md) — Determinism via seeding
- [DETERMINISM.md](docs/canonical_docs/DETERMINISM.md) — Reproducibility contracts
- [EXPERIMENTS.md](docs/canonical_docs/EXPERIMENTS.md) — analytics and regime classification

**Status & planning:**
- [CURRENT_STATE.md](docs/Project_Status/CURRENT_STATE.md) — Stage III baseline summary
- [ROADMAP.md](docs/Project_Status/ROADMAP.md) — next priorities

**Code organization:**
- `FestinaLente/core/` — engine, world, agent state
- `FestinaLente/regimes/` — configuration compilation
- `FestinaLente/runner/` — batch orchestration
- `FestinaLente/analytics/` — metrics, fingerprints, classification
- `tests/verification/` — determinism, invariants, snapshots, RNG isolation
- `tests/validation/` — regime contracts and cross-regime checks

## Design Philosophy

The codebase prioritizes:

1. **Determinism** — fixed seed → identical trajectory (tested explicitly)
2. **Clarity** — phase separation and transparent orchestration over convenience
3. **Reproducibility** — snapshot/restore and canonical hashing as first-class concerns
4. **Research rigor** — separation of simulation logic, metrics, and analytics

Not prioritized (yet): advanced GUIs, distributed computation, complex spatial interaction rules.
