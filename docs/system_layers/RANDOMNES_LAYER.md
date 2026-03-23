# 4. Randomness Layer

## Conceptual view

This layer governs **controlled stochasticity**.

Randomness is not outside the model. It is an explicit input stream.

## Schematic view

```
Master seed
    ↓
RNG construction
    ├── world RNG
    ├── movement RNG
    ├── reproduction RNG
    └── other role-specific RNGs
```

## Mathematical view

$$
\xi_t \sim \mathcal{R}(\text{seed})
$$

Operationally, under a fixed seed:

$$
\xi_0, \xi_1, \xi_2, \dots
$$

is a deterministic pseudorandom sequence.

So the simulator is a **deterministic stochastic system**:

$$
S_{t+1} = F(S_t, \xi_t)
$$

## Important distinction

- **Deterministic system**: no stochastic term
- **Seeded stochastic system**: stochastic rules, but reproducible trajectories under fixed seed

---