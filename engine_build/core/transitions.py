"""
Transition layer: the engine's authoritative view of world-state mutation.

- This module owns state-mutation logic.
- Transition functions should stage changes, then apply them in one commit.

Execution flow:
    Agents + World (state_t)
        -> Transition functions
        -> Pending state changes
        -> Commit
        -> Agents + World (state_t+1)

Treat each tick as a transaction log.

Example (tick 1023):
- Deaths: starvation [4, 9, 22]
- Births: parents 11, 17
- Energy changes: agent 3 +2, agent 7 +1
- World changes: cell (10, 4) -3 resources

Apply the transaction only at commit.

Conceptual engine-loop order:
1. Move agents
2. Build spatial groups
3. Harvest resources
4. Determine reproduction
5. Age agents
6. Aggregate death buckets
7. Compute capacity
8. Commit births
9. Commit deaths
10. Regrow resources
11. Advance tick
"""

# Inputs: agents, world
# Outputs: alive_agents, death_bucket, occupied_positions

def step_move_agents():
    pass


def step_group_positions():
    pass


# Inputs: occupied_positions, world
# Outputs: reproducing_agents, death_bucket

def step_resolve_harvest():
    pass


def step_resolve_reproduction():
    pass



def step_age_agents():
    pass
