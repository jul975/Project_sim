# 6. Spatial Interaction Layer

## Conceptual view

This layer defines **who can interact with whom**.

Without it, neighbor search is naive $O(n^2)$. With a spatial hash or occupancy grid, interactions become local and scalable.

## Schematic view

```
Agent positions
    ↓
Spatial hash / occupancy index
    ↓
Neighborhood query
    ↓
Interaction candidates
```

## Mathematical view

For agent $i$ at time $t$, define its neighborhood:

$$
\mathcal{N}_i(t) = \{j \neq i \mid d(i,j) \le R\}
$$

Where:

- $d(i,j)$ = spatial distance
- $R$ = interaction radius

Then local behavior depends on:

$$
A_i(t+1) = f\big(A_i(t), \mathcal{N}_i(t), W_t, \xi_i(t)\big)
$$

---