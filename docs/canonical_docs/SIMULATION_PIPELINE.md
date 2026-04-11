# Simulation Pipeline

## Purpose

This document defines the tick order implemented by `FestinaLente/core/engine.py` on March 23, 2026.

The current goals are:

- deterministic execution
- explicit mutation boundaries
- clear birth/death accounting
- compatibility with canonical hashing and snapshot continuation

## Authoritative Tick Order

Both `Engine._step_fast()` and `Engine._step_instrumented()` execute the same ecological order:

```text
1. movement_phase()
2. interaction_phase()
3. biology_phase()
4. commit_phase()
5. world.tick += 1
```

The instrumented path only adds optional profiling and optional world-frame capture.

## Phase Details

### 1. Movement phase

Source: `FestinaLente/core/transitions.py::movement_phase`

Runtime order:

- iterate `engine.agents.items()` in dictionary insertion order
- if an agent is already `alive == False`, queue it into `age_deaths`
- otherwise call `agent.move_agent()`
- if movement cost kills the agent, queue it into `metabolic_deaths`
- surviving agents are inserted into `occupied_positions[position]`

Current movement semantics:

```text
energy -= movement_cost
position += one cardinal move
position = wrap(position)
```

The move set is:

```text
(-1, 0), (1, 0), (0, -1), (0, 1)
```

Outputs:

- `age_deaths`
- `metabolic_deaths`
- cell occupancy map for the interaction phase

### 2. Interaction phase

Source: `FestinaLente/core/transitions.py::interaction_phase`

For each occupied cell in encounter order:

- call `world.harvest(local_agents, position)`
- if an agent still has `energy_level <= 0`, queue `post_harvest_starvation`
- otherwise append it to `post_harvest_alive`

`World.harvest()` distributes the cell harvest deterministically:

- total harvest is capped by available resources and total local demand
- each local agent gets `harvest // n_agents`
- the first `harvest % n_agents` agents in local encounter order get `+1`

That local ordering is not explicitly re-sorted. It comes from movement-phase encounter order.

Outputs:

- `post_harvest_starvation`
- `post_harvest_alive`

### 3. Biology phase

Source: `FestinaLente/core/transitions.py::biology_phase`

For each agent in `post_harvest_alive`:

- test `agent.can_reproduce()`
- if eligible, call `agent.does_reproduce()`
- successful reproducers are appended to `reproducing_agents`
- if reproduction cost leaves the parent at `energy_level <= 0`, queue `post_reproduction_death`
- call `agent.age_agent()`

Important current behavior:

- successful reproduction does not skip aging
- even agents queued for `post_reproduction_death` still pass through `age_agent()` in the current implementation
- age-based death is marked by setting `alive = False`; removal happens on the next tick when movement phase sees that flag

Outputs:

- `reproducing_agents`
- `post_reproduction_death`

### 4. Commit phase

Source: `FestinaLente/core/engine.py::commit_phase`

Commit order:

```text
count queued deaths
compute effective population after queued deaths
slice reproducing_agents by remaining capacity
delete dead agents
create newborns
regrow resources
```

Capacity rule:

```text
effective_population = len(agents) - deaths_this_tick
available_capacity = max_agent_count - effective_population
reproducers_to_commit = reproducing_agents[:available_capacity]
```

Current newborn semantics:

- child ID is `next_agent_id`
- child position is the parent position
- child energy is sampled from `energy_init_range`
- parent `offspring_count` increments only when the birth is actually committed
- `next_agent_id` increments monotonically

Important current rule:

- deaths commit before births

This keeps the hard population cap enforced without temporary overshoot.

### 5. Tick increment

After the `StepReport` is built:

```text
world.tick += 1
```

If world-frame capture is enabled, the frame is sampled before that increment and only when the current tick is divisible by 10.

## Step Output

Each call to `Engine.step()` returns a `StepReport` containing:

- `tick`
- `movement_report`
- `interaction_report`
- `biology_report`
- `commit_report`
- optional `world_view`
- optional `step_profile`

`SimulationMetrics.record()` consumes `StepReport` rather than reaching back into engine internals.

## Determinism Invariants

The current pipeline depends on the following invariants:

- no structural mutation during movement, interaction, or biology
- stable dictionary encounter order for agent traversal
- deterministic append order inside occupancy buckets
- deaths are deleted before births are materialized
- agent IDs remain monotonic
- world regrowth happens after all births and deaths for the tick

## Current Behavioral Notes

- `post_harvest_starvation` exists as a real death bucket, but under the current energy model it is usually zero
- age-based death is deferred by one tick because `age_agent()` only flips `alive` and movement phase queues the removal on the next step
- the runtime loop does not sort agents every tick; canonical sorting happens in hashing and exported world views, not in the hot path
