# Mathematical Model

This document specifies the mathematical formulation of the current Ecosystem Engine (Stage II: controlled ecological dynamics), aligned with the implementation in `engine_build/core/*`.

The simulator is a discrete-time stochastic state transition system:

$$
S_{t+1} = T(S_t)
$$

For fixed `(seed, config, code version)`, evolution is reproducible because randomness is sourced from isolated RNG streams.

---

## 1. Notation

### 1.1 Time and indices
- Discrete time: $t \in \{0,1,2,\dots\}$
- Agent IDs at tick $t$: $i \in \mathcal{I}_t$
- Iteration order: ascending sorted IDs

### 1.2 World geometry
- 1D torus of size $W$ (`world_size`)

$$
\mathrm{wrap}(x) = x \bmod W
$$

---

## 2. State

Define global state:

$$
S_t = \big(F, R_t, \{(x_i(t), E_i(t), \mathrm{age}_i(t), \mathrm{alive}_i(t))\}_{i \in \mathcal{I}_t}, \mathrm{next\_id}\big)
$$

Where:
- $F \in \{0,\dots,R_{\max}-1\}^{W}$ is static fertility (carrying capacity)
- $R_t \in \mathbb{Z}_{\ge 0}^{W}$ is dynamic resources, bounded by

$$
0 \le R_t(x) \le F(x) \quad \forall x
$$

Each agent state is:

$$
a_i(t) = \big(x_i(t), E_i(t), \mathrm{age}_i(t), \mathrm{alive}_i(t)\big)
$$

with:
- $x_i(t) \in \{0,\dots,W-1\}$
- $E_i(t) \in \mathbb{Z}$
- $\mathrm{age}_i(t) \in \mathbb{N}$
- $\mathrm{alive}_i(t) \in \{0,1\}$

---

## 3. Parameters

### 3.1 World and population
- $W$ = `world_size`
- $R_{\max}$ = `max_resource_level`
- $r$ = `resource_regen_rate`
- $H_{\max}$ = `max_harvest`
- $N_0$ = `initial_agent_count`
- $N_{\max}$ = `max_agent_count`
- $A_{\max}$ = `max_age`

### 3.2 Reproduction probabilities
- $p_0$ = `reproduction_probability`
- $p_1$ = `reproduction_probability_change_condition`

Each agent uses fixed $p \in \{p_0, p_1\}$ for the run (selected from `change_condition` at construction time).

### 3.3 Ratio-derived energy parameters
Ratios (`EnergyRatios`): $\alpha$ (metabolic pressure), $\beta$ (reproductive depletion), $\gamma$ (maturity scale).

Derived runtime parameters (`EnergyParams`):

$$
\begin{aligned}
c_m &= \lfloor \alpha H_{\max} \rfloor \\
\theta &= \lfloor \gamma c_m \rfloor \\
c_r &= \lfloor \beta \theta \rfloor
\end{aligned}
$$

(using Python `int(...)` truncation).

---

## 4. Initialization

### 4.1 World

$$
F(x) \sim \mathrm{Unif}\{0,\dots,R_{\max}-1\}, \qquad R_0(x) = F(x)
$$

### 4.2 Initial agents
For each $i \in \{0,\dots,N_0-1\}$:

$$
\begin{aligned}
x_i(0) &\sim \mathrm{Unif}\{0,\dots,W-1\} \\
E_i(0) &\sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\} \\
\mathrm{age}_i(0) &= 0, \quad \mathrm{alive}_i(0)=1
\end{aligned}
$$

where `(E_min, E_max) = energy_init_range`.

---

## 5. Tick Operator

A full tick is:

$$
T = G \circ C \circ U
$$

- $U$: ordered per-agent evaluation on current resources
- $C$: commit phase (deaths first, births second, cap-aware)
- $G$: resource regrowth

This matches implementation ordering in `Engine.step()`.

---

## 6. Per-Agent Evaluation $U$

Let $\langle i_1,\dots,i_{N_t} \rangle$ be sorted IDs at tick start. Updates are sequential and mutate $R$ in place.

For each agent $i$:

### 6.1 Alive gate
If $\mathrm{alive}_i = 0$, agent is queued for old-age removal and does not act.

### 6.2 Movement and metabolic check
Sample $\Delta x_i \in \{-1,+1\}$ and apply:

$$
E_i \leftarrow E_i - c_m
$$

$$
x_i \leftarrow \mathrm{wrap}(x_i + \Delta x_i)
$$

If $E_i \le 0$, set $\mathrm{alive}_i \leftarrow 0$ and queue metabolic-starvation death.

### 6.3 Harvest

$$
h_i = \min\big(R(x_i), H_{\max}\big)
$$

$$
R(x_i) \leftarrow R(x_i) - h_i
$$

$$
E_i \leftarrow E_i + h_i
$$

Sequential ordering creates implicit competition when multiple agents share a position.

### 6.4 Reproduction gate and draw
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

If $E_i \le 0$, queue post-reproduction death and stop evaluation for that agent.

### 6.5 Aging
For agents not short-circuited by prior death branches:

$$
\mathrm{age}_i \leftarrow \mathrm{age}_i + 1
$$

$$
\mathrm{age}_i \ge A_{\max} \Rightarrow \mathrm{alive}_i \leftarrow 0
$$

Agents marked dead by age are removed in the next tick's commit phase.

---

## 7. Commit Phase $C$ (Deaths Then Births)

Let:
- $D_t$ = total queued deaths for tick $t$
- $B_t^{\mathrm{raw}}$ = number of successful reproduction events for tick $t$
- $N_t$ = population size before commits

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
B_t = \min\big(B_t^{\mathrm{raw}}, \mathrm{cap}_t\big)
$$

Death commit removes all queued IDs. Birth commit inserts the first $B_t$ queued reproducers (encounter order), each generating one child with:

$$
x_j \leftarrow x_i, \quad \mathrm{age}_j \leftarrow 0, \quad \mathrm{alive}_j \leftarrow 1
$$

$$
E_j(0) \sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\}
$$

---

## 8. Regrowth Operator $G$

After commits:

$$
R_{t+1}(x) = \min\big(F(x), R'_t(x) + r\big)
$$

where $R'_t$ is the post-harvest/post-commit resource field.

---

## 9. Closed-Loop Dynamics

$$
R \rightarrow h \rightarrow E \rightarrow (\text{birth/death}) \rightarrow N \rightarrow R
$$

Current model properties:
- implicit competition through sequential harvest
- energy-gated stochastic reproduction
- metabolic, post-reproduction, and age death pathways
- hard population cap with capacity-aware birth commit
- toroidal movement with fertility-bounded regrowth

---

## 10. Representation Corrections Applied
The following issues were corrected in this draft:
- replaced broken symbols/encoding artifacts with valid notation
- normalized equation formatting to renderable Markdown math
- clarified that $B_t^{\mathrm{raw}}$ means successful reproduction events (not all attempts)
- clarified that aging is skipped for agents that early-exit via death branches
