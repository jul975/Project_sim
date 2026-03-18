# Simulation Pipeline

## Purpose

This document defines the canonical execution order of one simulation tick (`Engine.step()`).

Goals:

- deterministic execution
- reproducible state transitions
- explicit mutation boundaries
- clear lifecycle accounting (birth/death)

## Tick Pipeline (Implemented)

The current pipeline in `core/engineP4.py` executes in this order:

```text
Engine.step()
1. Build deterministic iteration view: sorted(agent_ids)
2. Agent evaluation phase (no structural mutation)
3. Compute available population capacity
4. Commit deaths
5. Commit births (capacity-limited)
6. Regrow world resources
7. Increment world tick
8. Return (births_committed, deaths_committed, death_buckets)
```

## Phase Details

### 1. Deterministic iteration view

Agents are traversed in sorted ID order to guarantee stable replay.

### 2. Agent evaluation phase

For each agent, the engine evaluates lifecycle transitions and records outcomes without editing the agent dictionary structure.

Per-agent evaluation order:

1. Old-age gate (`alive == False` from prior tick)
2. Movement + movement energy cost (`move_agent`)
3. Harvest (`harvest_resources`)
4. Reproduction eligibility and stochastic reproduction draw
5. Post-reproduction death check
6. Age increment (`agent.step`)

Deaths are accumulated into typed buckets:

- `old_age`
- `metabolic_starvation`
- `post_harvest_starvation`
- `post_reproduction_death`

Reproducing parents are queued for later birth commit.

### 3. Capacity computation

The engine computes effective free capacity before committing births:

```text
effective_population = current_population - deaths_this_tick
available_capacity = max_agent_count - effective_population
reproducers_to_commit = reproducing_agents[:available_capacity]
```

### 4. Death commit

All queued deaths are removed from `agents`.

### 5. Birth commit

New agents are created from queued reproducers, limited by `available_capacity`.

### 6. World update

Resources regrow after all agent actions and lifecycle commits.

### 7. Tick increment

`world.tick += 1`

## Determinism Contract

The pipeline must preserve these invariants:

- stable agent iteration order (`sorted(agent_ids)`)
- no in-loop structural mutation of the population map
- isolated RNG streams by concern (world, movement, reproduction, energy init)
- monotonic identity assignment (`next_agent_id`)
- bounded population (`len(agents) <= max_agent_count`)

## Responsibility Boundary

`Engine.step()` is responsible for state transition only.

Metrics collection is performed by runner/analysis layers outside the step function.

## Summary

System flow per tick:

```text
evaluate agents -> compute capacity -> commit deaths -> commit births -> regrow world -> tick++
```

This ordering is the authoritative simulation pipeline for deterministic replay and validation.
