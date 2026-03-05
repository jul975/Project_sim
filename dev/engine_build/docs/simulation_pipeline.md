# Simulation Pipeline

## Purpose

This document defines the **canonical execution order of a single simulation step**.

Maintaining a fixed execution order is essential for:

- deterministic execution
- reproducible simulations
- avoiding hidden state mutations
- preventing future integration bugs

All system updates must follow this pipeline unless the architecture is intentionally modified.

---

# Engine Step Execution

Each simulation tick executes the following ordered sequence:


Engine.step()

1. world.regenerate()

2. agent update loop

3. register births

4. remove dead agents

5. enforce population cap

6. collect metrics

7. increment tick


---

# Step Breakdown

## 1. Resource Regeneration

The environment updates its resource field.


world.regenerate()


Typical behavior:


resources += regen_rate
resources = min(resources, fertility)


This step ensures resources evolve **before agent interaction**.

---

## 2. Agent Update Loop

Agents are processed **in deterministic order**.


for agent_id in sorted(agents):
agent.step()


Each agent may:

- expend energy through movement
- change position
- harvest resources
- trigger reproduction
- die if energy is depleted

No structural changes to the agent list occur during this phase.

---

## 3. Birth Registration

New agents created during the update loop are registered.


new_agents → agents


Agent identifiers must remain **strictly monotonic**.

---

## 4. Death Cleanup

Agents marked as dead are removed from the simulation.


agents = {a for a in agents if a.alive}


This maintains a consistent active population set.

---

## 5. Population Cap Enforcement

The engine ensures the population does not exceed the configured limit.


population ≤ max_agent_count


If the cap is reached, further reproduction is suppressed.

---

## 6. Metrics Collection

Simulation statistics are recorded.

Examples:

- population size
- births per tick
- deaths per tick
- resource levels
- energy statistics

These metrics feed the analytics and validation pipeline.

---

## 7. Tick Increment

The simulation advances to the next timestep.


tick += 1


---

# Deterministic Requirements

The pipeline must preserve the following properties:

### Stable iteration order

Agents must always be processed in sorted ID order.

### Controlled structural mutation

Births and deaths must occur **outside the agent iteration loop**.

### RNG isolation

Random processes must only use their designated RNG streams.

---

# Summary

The simulation step follows a strict deterministic pipeline:


environment update
→ agent actions
→ births
→ deaths
→ population constraints
→ metrics
→ next tick


This ordering guarantees **consistent system evolution and reproducibility across runs**.