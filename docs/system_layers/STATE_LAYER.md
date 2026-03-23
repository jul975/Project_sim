# 2. State Layer

## Conceptual view

This is the **authoritative simulator state**.

It includes:

- current tick
- world resource field
- all agents and their properties
- occupancy / spatial index state
- RNG states
- optionally metric buffers

This is the layer that must be serializable and reproducible.

## Schematic view

```
S_t
├── tick
├── world
│   ├── resources
│   └── terrain / fertility
├── agents
│   ├── prey
│   └── predators
├── spatial index
├── RNG states
└── metric buffers
```

## Mathematical view

$$
S_t = \{t, W_t, A_t, I_t, R_t, M_t\}
$$

Where:

- $t$ = current tick
- $W_t$ = world state
- $A_t$ = agent set
- $I_t$ = spatial index state
- $R_t$ = RNG state
- $M_t$ = metric state / buffers