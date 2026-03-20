# World Frames Analytics Overview

This document organizes the proposed world-frame analytics into three priority groups:

1. `Must-have / now`: the smallest high-value set to build first.
2. `Good second-wave metrics`: useful extensions once the first layer is stable.
3. `Not yet`: legitimate ideas, but not worth the implementation complexity yet.

Throughout, let:

- $D \in \mathbb{R}^{H \times W}$ be the agent-density grid for a sampled frame.
- $R \in \mathbb{R}^{H \times W}$ be the resource grid for the same frame.
- $E = (e_1, \dots, e_n)$ be the sampled agent energies for that frame.
- $N = H \cdot W$ be the total number of cells.
- $\mathbf{1}[\cdot]$ be the indicator function.
- $\tau$ be a low-resource threshold.

All per-frame metrics can later be summarized across sampled frames with statistics such as mean, max, min, or standard deviation.

## 1. Must-Have / Now

These are the core metrics worth implementing first. They are simple, interpretable, and together give a strong picture of spatial usage, ecological conditions, and agent condition.

### 1.1 Occupancy Rate

Question: how much of the world is actually being used?

$$
\mathrm{occupancy\_rate}
=
\frac{\sum_{i=1}^{N} \mathbf{1}[D_i > 0]}{N}
$$

Interpretation:

- Low occupancy suggests strong clustering or sparse occupation.
- High occupancy suggests broad dispersal across the map.

This is one of the most useful first-pass spatial indicators.

### 1.2 Mean Nonzero Crowding

Question: when a cell is occupied, how crowded is it?

$$
\mathrm{mean\_crowding\_nonzero}
=
\operatorname{mean}\left(D_i \mid D_i > 0\right)
$$

Equivalent implementation form:

$$
\mathrm{mean\_crowding\_nonzero}
=
\operatorname{mean}(D[D > 0])
$$

Interpretation:

- Separates "spread thinly" from "packed into hotspots".
- More informative than population alone.

### 1.3 Peak Local Density

Question: how bad do local density hotspots get?

$$
\mathrm{peak\_density} = \max_i D_i
$$

Interpretation:

- Catches extreme pileups.
- Useful for identifying congestion or strongly clustered regimes.

For batch summaries, the most useful rollups are usually:

- Mean peak density across sampled frames.
- Max peak density across sampled frames.

### 1.4 Mean Resource Level

Question: is the world generally resource-rich or resource-poor?

$$
\mathrm{mean\_resource} = \operatorname{mean}(R)
$$

Interpretation:

- Tracks average environmental abundance.
- Serves as a baseline ecological measure.

### 1.5 Resource Heterogeneity

Question: are resources smooth or patchy?

$$
\mathrm{resource\_heterogeneity} = \operatorname{std}(R)
$$

Interpretation:

- High standard deviation means a patchy or uneven environment.
- Low standard deviation means a flatter environment.

This matters because the same mean resource level can correspond to very different worlds.

### 1.6 Resource Depletion Pressure

Question: how much of the world is sitting near empty?

$$
\mathrm{low\_resource\_cell\_rate}
=
\frac{\sum_{i=1}^{N} \mathbf{1}[R_i \le \tau]}{N}
$$

Possible choices for $\tau$:

- An absolute threshold, such as $\tau = 0.1 \cdot R_{\max}$.
- A fixed threshold if the resource scale is stable across runs.

Interpretation:

- Gives an ecological stress footprint.
- Often more informative than mean resource alone.

Possible naming:

- `resource_depletion_rate`
- `low_resource_cell_rate`

### 1.7 Mean Sampled Energy

Question: what is the average condition of agents in the sampled frame?

$$
\mathrm{mean\_energy} = \operatorname{mean}(E)
$$

Interpretation:

- Captures average agent condition.
- Complements existing run-level energy metrics.

Even if this overlaps with current metrics, it is still useful as a world-frame cross-check.

### 1.8 Energy Dispersion / Inequality

Question: are agents similarly healthy, or is condition highly uneven?

Raw dispersion:

$$
\mathrm{energy\_std} = \operatorname{std}(E)
$$

Normalized dispersion:

$$
\mathrm{energy\_cv}
=
\frac{\operatorname{std}(E)}{\operatorname{mean}(E)}
\quad \text{if } \operatorname{mean}(E) > 0,\ \text{else } 0
$$

Interpretation:

- Distinguishes evenly healthy populations from stratified ones.
- Often more informative than mean energy alone.

If only one inequality metric is added now, the coefficient of variation is the best first choice; Gini can wait.

### 1.9 Density-Resource Correlation

Question: are agents concentrated where resources are, or are they stripping resource patches bare?

Let $\mathrm{vec}(D)$ and $\mathrm{vec}(R)$ be the flattened grids. Then:

$$
\rho_{D,R}
=
\operatorname{corr}\left(\mathrm{vec}(D), \mathrm{vec}(R)\right)
$$

Equivalent implementation form:

$$
\rho_{D,R}
=
\operatorname{corr}\left(D.\mathrm{flatten}(),\ R.\mathrm{flatten}()\right)
$$

Interpretation:

- Positive correlation means agents are located on resource-rich zones.
- Weak or negative correlation suggests depletion behind occupation, or a mismatch between occupancy and resources.

This is one of the most conceptually important metrics because it directly links ecology and spatial structure.

Implementation note: handle degenerate zero-variance cases explicitly.

## 2. Good Second-Wave Metrics

These are valuable, but they are not essential for the first clean version.

### 2.1 Occupied-Cell Resource Mean

Average resources in cells where agents are present:

$$
\mathrm{mean\_resource\_occupied}
=
\operatorname{mean}(R[D > 0])
$$

Interpretation:

- Shows whether agents are sitting in locally rich or poor areas.
- Most useful when compared to the global mean resource.

### 2.2 Unoccupied-Cell Resource Mean

Average resources in cells with no agents:

$$
\mathrm{mean\_resource\_empty}
=
\operatorname{mean}(R[D = 0])
$$

Compare the two with:

$$
\Delta_{\mathrm{resource}}
=
\mathrm{mean\_resource\_occupied}
-
\mathrm{mean\_resource\_empty}
$$

Interpretation:

- If occupied cells are poorer than empty cells, agents may be depleting local patches.
- If occupied cells are richer, agents are still aligned with abundance.

This is a strong ecological signal, but it can wait until the first wave is stable.

### 2.3 Spatial Entropy of Density

Normalize the density grid into a probability distribution over cells:

$$
p_i = \frac{D_i}{\sum_{j=1}^{N} D_j}
$$

Then define entropy:

$$
H = -\sum_{i=1}^{N} p_i \log p_i
$$

Interpretation:

- High entropy means population is spread out.
- Low entropy means population is concentrated.

This is richer than occupancy alone, but also more abstract, so it belongs in the second wave.

### 2.4 Frame-to-Frame Spatial Volatility

Question: how much does density or resource structure change between sampled frames?

For density:

$$
\mathrm{density\_change}_t
=
\operatorname{mean}\left(\left| D_t - D_{t-1} \right|\right)
$$

An analogous metric can be defined for resources.

Interpretation:

- Separates stable spatial patterns from churn-heavy ones.
- Useful once there is already confidence in the per-frame metrics.

## 3. Not Yet

These are real analytic directions, but they are not worth implementing right now relative to their complexity:

- Nearest-neighbor distances.
- Moran's $I$ / spatial autocorrelation.
- Ripley's $K$.
- Cluster labeling / connected components.
- Full patch persistence tracking.
- Gini coefficient, unless there is a very specific need for it.
- Agent pathline analysis.
- Pairwise distance matrices.

These all risk becoming second-system work before the first metric layer is stable and useful.

## Recommended First Build

If the goal is a strong first release, the best initial bundle is:

1. `occupancy_rate`
2. `mean_crowding_nonzero`
3. `peak_density`
4. `mean_resource`
5. `resource_heterogeneity`
6. `low_resource_cell_rate`
7. `mean_energy`
8. `energy_cv`
9. `density_resource_correlation`

That set gives a compact view of:

- Spatial spread
- Spatial crowding
- Ecological abundance
- Ecological depletion
- Agent condition
- Agent-resource alignment
