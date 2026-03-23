# 1. Configuration Layer

## Conceptual view

This layer defines the **laws of the world before the world begins**.

It contains:

- world dimensions
- initial populations
- energy parameters
- resource parameters
- reproduction parameters
- activation regime
- seed

This layer is **not the state**. It is the **parameterization of the state-transition process**.

## Schematic view

```
Config / Regime
    ├── world_size
    ├── initial populations
    ├── energy parameters
    ├── resource parameters
    ├── reproduction parameters
    ├── activation mode
    └── seed
```

## Mathematical view

$$
\theta = \{W, H, N_{\text{prey},0}, N_{\text{pred},0}, r, K, c_m, c_r, p_{\text{birth}}, \dots\}
$$

Where:

- $W, H$ = world width and height
- $r$ = resource regrowth parameter
- $K$ = carrying capacity / max resource
- $c_m$ = metabolic cost
- $c_r$ = reproduction cost

---