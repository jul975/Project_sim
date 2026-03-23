# 7. Agent Layer

## Conceptual view

Agents are the **individual state-bearing entities**.

Each agent has:

- identity
- species or role
- position
- energy
- alive/dead status
- age or lifecycle state
- behavior rules

## Schematic view

```
Agent
├── id
├── species
├── position
├── energy
├── alive
├── age
└── behavior rules
```

## Mathematical view

For agent $i$:

$$
A_i(t) = \{x_i(t), y_i(t), E_i(t), alive_i(t), age_i(t), \dots\}
$$

Its evolution is:

$$
A_i(t+1) = f_i\big(A_i(t), O_i(t), \xi_i(t)\big)
$$

Where:

- $O_i(t)$ = local observation / local environment
- $\xi_i(t)$ = agent-level stochastic input

---