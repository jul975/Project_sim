# 5. World Layer

## Conceptual view

This layer defines the **environmental substrate**:

- 2D grid
- resources on patches
- optional terrain / fertility / heterogeneity
- boundary rules

## Schematic view

```
World Grid
├── width × height
├── resource field G(x,y,t)
├── optional fertility / terrain
└── boundary policy
```

## Mathematical view

Let the resource field be:

$$
G_t(x,y)
$$

A simple capped regrowth rule is:

$$
G_{t+1}(x,y) = \min\big(G_t(x,y) + r,\; K(x,y)\big)
$$

A logistic-style version is:

$$
G_{t+1}(x,y) = G_t(x,y) + r\,G_t(x,y)\left(1 - \frac{G_t(x,y)}{K(x,y)}\right)
$$

Where:

- $r$ = regrowth rate
- $K(x,y)$ = local carrying capacity / fertility ceiling

---