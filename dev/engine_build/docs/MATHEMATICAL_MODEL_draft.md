# Mathematical Model

This document formalizes the **current Stage II system** (energy/resource coupling + reproduction + death + cap) as implemented in `engine_build/core/*`.

The simulator is a discrete-time transition system:

$$
S_{t+1} = T(S_t)
$$

All randomness is produced by **explicit, isolated RNG streams**, so for fixed *(seed, config, code version)* the evolution is reproducible.

---

## 1. State

Let the world have size $W$ (`world_size`) with **1D toroidal topology**:

$$
\mathrm{wrap}(x) = x \bmod W
$$

The global state at time $t$ is:

$$
S_t = \big(F,\; R_t,\; \{(x_i(t),E_i(t),\mathrm{age}_i(t),\mathrm{alive}_i(t))\}_{i\in\mathcal{I}_t},\; \text{next\_id}\big)
$$

Where:

- $F\in\{0,\dots,R_{\max}-1\}^{W}$ is the **fertility/capacity** field (static).
- $R_t\in\mathbb{Z}_{\ge 0}^{W}$ is the **resource** field (dynamic), constrained by:

$$
0 \le R_t(x) \le F(x) \quad \forall x
$$

- Each agent $i$ has:
  - position $x_i(t)\in\{0,\dots,W-1\}$
  - energy $E_i(t)\in\mathbb{Z}$
  - age $\mathrm{age}_i(t)\in\mathbb{N}$
  - alive flag $\mathrm{alive}_i(t)\in\{0,1\}$

Agents are iterated in **sorted ID order**.

---

## 2. Parameters

### 2.1 World and population

- $W$ = `world_size`
- $R_{\max}$ = `max_resource_level`
- $r$ = `resource_regen_rate`
- $H_{\max}$ = `max_harvest`

- $N_0$ = `initial_agent_count`
- $N_{\max}$ = `max_agent_count`
- $A_{\max}$ = `max_age`

### 2.2 Energy and reproduction

Energy initialization range: $(E_{\min}, E_{\max}) = \text{energy\_init\_range}$ (NumPy high-exclusive).

Two reproduction probabilities exist (selected by `change_condition`):

- $p_0$ = `reproduction_probability`
- $p_1$ = `reproduction_probability_change_condition`

During a run, each agent uses $p\in\{p_0,p_1\}$.

### 2.3 Ratio-derived energy parameters

Ratios (`EnergyRatios`): $\alpha$ (metabolic pressure), $\beta$ (repro depletion), $\gamma$ (maturity).

Derived integer parameters (`EnergyParams`), using Python `int(...)` truncation:

$$
\begin{aligned}
 c_m &= \lfloor \alpha\,H_{\max}\rfloor \\
 \theta &= \lfloor \gamma\,c_m\rfloor \\
 c_r &= \lfloor \beta\,\theta\rfloor
\end{aligned}
$$

- $c_m$: movement cost per tick
- $\theta$: reproduction energy threshold
- $c_r$: reproduction energy cost

---

## 3. Initialization

### 3.1 World

Fertility is sampled i.i.d. per cell:

$$
F(x) \sim \mathrm{Unif}\{0,\dots,R_{\max}-1\}
$$

Resources start at capacity:

$$
R_0(x) = F(x)
$$

### 3.2 Agents

For each initial agent $i\in\{0,\dots,N_0-1\}$:

$$
\begin{aligned}
 x_i(0) &\sim \mathrm{Unif}\{0,\dots,W-1\} \\
 E_i(0) &\sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\} \\
 \mathrm{age}_i(0) &= 0,\quad \mathrm{alive}_i(0)=1
\end{aligned}
$$

---

## 4. Tick Transition $T$

A full tick consists of:

$$
T = G \circ C \circ U
$$

- $U$: sequential per-agent updates (movement -> harvest -> reproduction -> age)
- $C$: commit deaths then births (cap-aware)
- $G$: resource regrowth

This matches the current implementation: **agents consume first**, regrowth occurs at the end.

---

## 5. Per-Agent Update $U$ (Sequential, Ordered)

Let $\langle i_1,\dots,i_{N_t}\rangle$ be the sorted IDs at tick start. Updates are applied in this order, mutating $R$ in-place (**implicit competition**).

For each agent $i$:

### 5.1 Alive gate
If $\mathrm{alive}_i=0$, the agent does not act and is removed in commit phase.

> Age-death is set at the end of the agent's step and is therefore removed on the **next** tick.

### 5.2 Movement + metabolic death
Sample $\Delta x_i\in\{-1,+1\}$ and apply:

$$
E_i \leftarrow E_i - c_m
$$

$$
x_i \leftarrow \mathrm{wrap}(x_i + \Delta x_i)
$$

If:

$$
E_i \le 0 \Rightarrow \mathrm{alive}_i \leftarrow 0
$$

the agent is scheduled for death and performs no harvest or reproduction.

### 5.3 Harvest (resource consumption)

$$
h_i = \min\big(R(x_i),\,H_{\max}\big)
$$

$$
R(x_i) \leftarrow R(x_i) - h_i
$$

$$
E_i \leftarrow E_i + h_i
$$

**Ordering effect:** if multiple agents occupy the same cell, earlier agents harvest first.

### 5.4 Reproduction (energy-gated + stochastic)
Eligibility:

$$
E_i \ge \theta
$$

If eligible, draw $u_i\sim\mathrm{Unif}(0,1)$. Reproduce if:

$$
u_i < p
$$

On reproduction success:

$$
E_i \leftarrow E_i - c_r
$$

If $E_i\le 0$, schedule a **post-reproduction death**:

$$
E_i \le 0 \Rightarrow \mathrm{alive}_i \leftarrow 0
$$

### 5.5 Age update

$$
\mathrm{age}_i \leftarrow \mathrm{age}_i + 1
$$

$$
\mathrm{age}_i \ge A_{\max} \Rightarrow \mathrm{alive}_i \leftarrow 0
$$

---

## 6. Commit Phase $C$: Deaths then Births (Capacity-Aware)

Let $D_t$ be deaths scheduled this tick, and $B_t^{\mathrm{raw}}$ be the number of reproduction successes requested.

Effective population after deaths:

$$
N_t^{\mathrm{eff}} = N_t - D_t
$$

Available capacity:

$$
\mathrm{cap}_t = N_{\max} - N_t^{\mathrm{eff}}
$$

Committed births:

$$
B_t = \min\big(B_t^{\mathrm{raw}},\;\mathrm{cap}_t\big)
$$

### 6.1 Death commit
Remove all agents with $\mathrm{alive}=0$.

### 6.2 Birth commit
For each committed reproducer $i$, spawn a child $j$ with:

$$
\begin{aligned}
 x_j &\leftarrow x_i \\
 E_j(0) &\sim \mathrm{Unif}\{E_{\min},\dots,E_{\max}-1\} \\
 \mathrm{age}_j &\leftarrow 0,\quad \mathrm{alive}_j \leftarrow 1
\end{aligned}
$$

(Seed lineage is deterministic and handled by the engine; omitted here because it does not alter the ecological equations.)

---

## 7. Resource Regrowth $G$

After commits, resources regrow toward fertility:

$$
R_{t+1}(x) = \min\big(F(x),\; R_t'(x) + r\big)
$$

where $R_t'$ is the post-harvest resource field.

---

## 8. Closed-Loop Ecology (Minimal Emergence Layer)

The system forms a minimal ecological feedback loop:

$$
R \rightarrow h \rightarrow E \rightarrow (\text{birth/death}) \rightarrow N \rightarrow R
$$

Key properties of the current model:

- **Implicit competition** via sequential resource depletion
- **Energy-gated reproduction** with stochastic triggering
- **Metabolic death**, **post-reproduction death**, and **age death**
- **Hard population cap** with capacity-aware births
- **Toroidal movement** and bounded resource regrowth

This is the stable mathematical base for Stage III (explicit spatial competition, 2D topology, traits/strategies).

---
