# Mathematical Model

## Purpose

This document defines the mathematical model of the current system (Stage II / `beta0.2`) as implemented in `engine_build/core/*`.

The simulation is a discrete-time transition system:

$$
S_{t+1} = T(S_t)
$$

with reproducible stochasticity under fixed `(seed, config, code version, runtime)`.

## 1. State

Let the world size be $W$ (`world_size`) with 1D toroidal topology:

$$
\mathrm{wrap}(x) = x \bmod W
$$

Global state at tick $t$:

$$
S_t = \Big(F, R_t, \{(x_i(t), E_i(t), a_i(t), \ell_i(t))\}_{i \in \mathcal{I}_t}, \text{next\_id}\Big)
$$

Where:

- $F \in \{0,\dots,R_{\max}-1\}^{W}$: fertility/capacity field (static after init)
- $R_t \in \mathbb{Z}_{\ge 0}^{W}$: resource field, bounded by

$$
0 \le R_t(x) \le F(x), \quad \forall x
$$

Agent variables:

- $x_i(t)$: position
- $E_i(t)$: energy
- $a_i(t)$: age
- $\ell_i(t) \in \{0,1\}$: alive flag

Agents are processed in ascending ID order.

## 2. Parameters

### 2.1 World and population

- $W$ = `world_size`
- $R_{\max}$ = `max_resource_level`
- $r$ = `resource_regen_rate`
- $H_{\max}$ = `max_harvest`
- $N_0$ = `initial_agent_count`
- $N_{\max}$ = `max_agent_count`
- $A_{\max}$ = `max_age`

### 2.2 Reproduction probability

- $p_0$ = `reproduction_probability`
- $p_1$ = `reproduction_probability_change_condition`

Each agent receives fixed $p \in \{p_0, p_1\}$ at construction, selected by `change_condition`.

### 2.3 Energy parameterization (ratio-derived)

Ratios: $\alpha$ (metabolic pressure), $\beta$ (reproductive depletion), $\gamma$ (maturity scale).

Derived runtime values:

$$
\begin{aligned}
c_m &= \lfloor \alpha H_{\max} \rfloor \\
\theta &= \lfloor \gamma c_m \rfloor \\
c_r &= \lfloor \beta \theta \rfloor
\end{aligned}
$$

(using Python `int(...)` truncation).

## 3. Initialization

### 3.1 World

$$
F(x) \sim \mathrm{Unif}\{0,\dots,R_{\max}-1\}, \qquad R_0(x)=F(x)
$$

### 3.2 Initial agents

For each $i \in \{0,\dots,N_0-1\}$:

$$
\begin{aligned}
x_i(0) &\sim \mathrm{Unif}\{0,\dots,W-1\} \\
E_i(0) &\sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\} \\
a_i(0) &= 0, \quad \ell_i(0)=1
\end{aligned}
$$

with `(E_min, E_max) = energy_init_range`.

## 4. Tick Operator

The implemented operator decomposes as:

$$
T = G \circ C \circ U
$$

- $U$: ordered per-agent evaluation (no structural mutation)
- $C$: commit phase (deaths then births, cap-aware)
- $G$: world regrowth

## 5. Per-Agent Evaluation $U$

For each agent in sorted order:

### 5.1 Alive gate

If $\ell_i = 0$, queue old-age removal and skip further updates.

### 5.2 Movement and metabolic check

Sample $\Delta x_i \in \{-1,+1\}$:

$$
E_i \leftarrow E_i - c_m
$$

$$
x_i \leftarrow \mathrm{wrap}(x_i + \Delta x_i)
$$

If $E_i \le 0$: set $\ell_i \leftarrow 0$, queue metabolic-starvation death, continue to next agent.

### 5.3 Harvest

$$
h_i = \min(R(x_i), H_{\max})
$$

$$
R(x_i) \leftarrow R(x_i) - h_i
$$

$$
E_i \leftarrow E_i + h_i
$$

This creates implicit competition through update order when multiple agents share a cell.

### 5.4 Reproduction gate and stochastic event

Eligibility:

$$
E_i \ge \theta
$$

If eligible, draw $u_i \sim \mathrm{Unif}(0,1)$ and reproduce iff:

$$
u_i < p
$$

On success:

$$
E_i \leftarrow E_i - c_r
$$

If $E_i \le 0$: set $\ell_i \leftarrow 0$, queue post-reproduction death, skip aging.

### 5.5 Aging (if not short-circuited)

$$
a_i \leftarrow a_i + 1
$$

$$
a_i \ge A_{\max} \Rightarrow \ell_i \leftarrow 0
$$

## 6. Commit Phase $C$ (Deaths Then Births)

Let:

- $D_t$: total queued deaths in tick $t$
- $B_t^{\mathrm{raw}}$: successful reproduction events in tick $t$
- $N_t$: pre-commit population

Effective post-death population:

$$
N_t^{\mathrm{eff}} = N_t - D_t
$$

Available capacity:

$$
\mathrm{cap}_t = N_{\max} - N_t^{\mathrm{eff}}
$$

Committed births:

$$
B_t = \min(B_t^{\mathrm{raw}}, \mathrm{cap}_t)
$$

Death commit removes queued IDs. Birth commit creates children for the first $B_t$ queued reproducers.

For child $j$ of parent $i$:

$$
x_j \leftarrow x_i, \quad a_j \leftarrow 0, \quad \ell_j \leftarrow 1
$$

$$
E_j(0) \sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\}
$$

## 7. Regrowth Operator $G$

After commits:

$$
R_{t+1}(x) = \min(F(x), R_t'(x) + r)
$$

where $R_t'$ is the post-harvest, post-commit resource field.

## 8. System Loop

The ecological feedback loop is:

$$
R \rightarrow h \rightarrow E \rightarrow (\text{birth/death}) \rightarrow N \rightarrow R
$$

## 9. Implementation Notes

- Reproduction is event-based (successes), not guaranteed by eligibility.
- Child position is explicitly overwritten to parent position at commit time.
- `post_harvest_starvation` exists as a death bucket in code, but under current update rules is effectively unreachable because energy does not decrease in harvest and metabolic death is resolved earlier.
- Determinism depends on stable environment/runtime in addition to seed/config/code.
