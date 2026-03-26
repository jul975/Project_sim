# 8. Energy / Resource Coupling Layer

## Conceptual view

This is the ecological core.

Energy is the **currency of survival**:

- movement costs energy
- eating increases energy
- reproduction consumes energy
- starvation kills

## Schematic view

```
Resource patch → prey energy → predator energy
        ↑              ↓             ↓
     regrowth       reproduction   reproduction
        ↓              ↓             ↓
      depletion      starvation     starvation
```

## Mathematical view

For prey:

$$
E^{\text{prey}}_{i,t+1} = E^{\text{prey}}_{i,t} + I^{\text{food}}_{i,t} - C^{\text{met}}_i - C^{\text{move}}_i - C^{\text{repr}}_{i,t}
$$

For predators:

$$
E^{\text{pred}}_{i,t+1} = E^{\text{pred}}_{i,t} + I^{\text{hunt}}_{i,t} - C^{\text{met}}_i - C^{\text{move}}_i - C^{\text{repr}}_{i,t}
$$

Alive/dead rule:

$$
alive_i(t+1) =
\begin{cases}
1 & \text{if } E_i(t+1) > 0 \\
0 & \text{if } E_i(t+1) \le 0
\end{cases}
$$

---
