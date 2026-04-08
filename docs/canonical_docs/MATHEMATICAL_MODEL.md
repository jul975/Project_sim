# Mathematical Model

## Status

This document describes the model currently implemented on March 23, 2026.

The simulator is a discrete-time stochastic transition system:

$$
S_{t+1} = T(S_t)
$$

with reproducible trajectories under fixed seed, compiled regime, code, and runtime.

## 1. State

Let the world dimensions be:

- $W_x =$ `world_width`
- $W_y =$ `world_height`

with 2D toroidal wrapping:

$$
\mathrm{wrap}(x, y) = (x \bmod W_x,\ y \bmod W_y)
$$

Global state at tick $t$ is:

$$
S_t = \Big(F,\ R_t,\ \mathcal{A}_t,\ \text{next\_id}\Big)
$$
where:

- $F \in \mathbb{Z}_{\ge 0}^{W_y \times W_x}$ is the static fertility field
- $R_t \in \mathbb{Z}_{\ge 0}^{W_y \times W_x}$ is the resource field
- $\mathcal{A}_t$ is the live agent map
- `next_id` is the next committed child ID

Resource bounds:

$$
0 \le R_t(y, x) \le F(y, x)
$$

Each live agent stores:

- position $(x_i(t), y_i(t))$
- energy $E_i(t)$
- age $a_i(t)$
- alive flag $\ell_i(t)$
- offspring count $o_i(t)$

Runtime processing order is dictionary encounter order, not a per-tick sort.

## 2. Parameters

### 2.1 World and population

- $R_{\max}$ = `max_resource_level`
- $r$ = `regen_rate`
- $H_{\max}$ = `max_harvest`
- $N_0$ = `initial_agent_count`
- $N_{\max}$ = `max_agent_count`
- $A_{\max}$ = `max_age`

### 2.2 Reproduction probability

Each engine uses one active reproduction probability:

$$
p \in \{p_0, p_1\}
$$

where:

- $p_0 =$ `probability`
- $p_1 =$ `probability_change_condition`

The current CLI uses $p_0$. The alternate value is used by internal tests that flip `change_condition=True`.

### 2.3 Derived energy parameters

Using anchors $E_{\max}$ and $R_{\max}$ plus ratios $\alpha$, $\beta$, $\gamma$, and $h$:

$$
\begin{aligned}
H_{\max} &= \min\left(E_{\max}, \max\left(1, \mathrm{round}(hR_{\max})\right)\right) \\
c_m &= \min\left(E_{\max}, H_{\max}, \max\left(1, \mathrm{round}(\alpha H_{\max})\right)\right) \\
\theta &= \min\left(E_{\max}, \max\left(c_m, \max\left(1, \mathrm{round}(\gamma c_m)\right)\right)\right) \\
c_r &= \min\left(\theta, \max\left(1, \mathrm{round}(\beta \theta)\right)\right)
\end{aligned}
$$

Where:

- $c_m$ is movement cost
- $\theta$ is reproduction threshold
- $c_r$ is reproduction cost

Initial-energy bounds:

$$
\begin{aligned}
E_{\min} &= \max(1, \mathrm{round}(\rho_{\min} E_{\max})) \\
E_{\max}^{\mathrm{init}} &= \max(E_{\min}, \mathrm{round}(\rho_{\max} E_{\max}))
\end{aligned}
$$

The runtime samples energy with NumPy `integers(low, high)`, so the upper bound is exclusive.

## 3. Initialization

### 3.1 World

The world first samples random noise:

$$
U(y, x) \sim \mathrm{Uniform}[0, 1)
$$

Then it smooths that field with an odd toroidal averaging kernel:

$$
k = \max(3, \mathrm{round}(\text{correlation} \cdot W_x))
$$

If $k$ is even, it is incremented to keep it odd.

The final fertility field is:

$$
F(y, x) = \left\lfloor R_{\max} \cdot \mathrm{smooth}(U)(y, x) \right\rfloor
$$

Resources start at fertility:

$$
R_0 = F
$$

### 3.2 Initial agents

For each founder $i \in \{0,\dots,N_0-1\}$:

$$
\begin{aligned}
x_i(0), y_i(0) &\sim \mathrm{UniformInt}(0, W_x - 1) \\
E_i(0) &\sim \mathrm{UniformInt}(E_{\min}, E_{\max}^{\mathrm{init}} - 1) \\
a_i(0) &= 0 \\
\ell_i(0) &= 1 \\
o_i(0) &= 0
\end{aligned}
$$

The current registry only emits square worlds, so the shared bound for both coordinates is valid in practice.

## 4. Tick Operator

The implemented operator executes in strict phase order:

$$
T = \Pi \circ B \circ H \circ M
$$

where:

- $M$ = movement phase (includes entry-age-check + direction sampling + movement cost + metabolic death check)
- $H$ = interaction / harvest phase (deterministic resource distribution)
- $B$ = biology phase (reproduction eligibility + Bernoulli draw + reproduction cost + aging)
- $\Pi$ = commit phase (death removals + birth creation + resource regrowth)

followed by `tick := tick + 1`.

## 5. Movement Phase

This phase handles:
1. Age-based death qualification
2. Direction sampling and movement
3. Movement cost and metabolic death

### 5.1 Age Entry Check

Before any movement, remove agents that have aged fully:

For each agent $i$ with $\ell_i = 1$ (alive from previous tick):

$$
\text{if } a_i \ge A_{\max} \text{ at entry: queue } i \text{ for age-death}
$$

These agents **do not move this tick** and will be removed in the commit phase.

### 5.2 Movement and Cost

For each remaining agent in encounter order:

$$
E_i \leftarrow E_i - c_m
$$

Sample one cardinal direction uniformly:

$$
(\Delta x_i, \Delta y_i) \sim \text{UniformChoice}\left\{(-1,0), (1,0), (0,-1), (0,1)\right\}
$$

Update position with toroidal wrapping:

$$
(x_i, y_i) \leftarrow \Big((x_i + \Delta x_i) \bmod W_x,\ (y_i + \Delta y_i) \bmod W_y\Big)
$$

### 5.3 Metabolic Death

If energy is now depleted:

$$
\text{if } E_i \le 0: \text{ queue } i \text{ for metabolic-death}
$$

Return movement report containing metabolic and age death counts.

## 6. Interaction / Harvest Phase

This phase distributes resources deterministically. For each occupied cell:

### 6.1 Total Harvest

At position $(x, y)$ with $n$ local agents and available resources $R$:

$$
H = \min\left(R,\ n \cdot H_{\max}\right)
$$

### 6.2 Deterministic Distribution

Base harvest per agent:

$$
h_{\text{base}} = \left\lfloor \frac{H}{n} \right\rfloor
$$

Remainder to distribute:

$$
r = H \bmod n
$$

For each local agent $j \in \{1, \ldots, n\}$ in encounter order:

$$
h_j = h_{\text{base}} + \begin{cases} 1 & \text{if } j \le r \\ 0 & \text{otherwise} \end{cases}
$$

This ensures deterministic, fair distribution: the first $r$ agents receive one extra resource unit.

### 6.3 Energy Update and Starvation

Each agent updates:

$$
E_j \leftarrow E_j + h_j
$$

**Note**: Starvation occurs immediately for agents reaching $E_j \le 0$ after harvest, though under current regime parameters this bucket is typically empty (most starvation occurs from movement cost, not harvest shortfall).

Cell resources decrease:

$$
R \leftarrow R - H
$$

## 7. Biology Phase

For each post-harvest survivor:

### 7.1 Reproduction Eligibility and Bernoulli Draw

If energy meets threshold:

$$
E_i \ge \theta \text{ (reproduction threshold)}
$$

Sample reproduction outcome:

$$
u_i \sim \mathrm{Uniform}[0, 1)
$$

Reproduce with probability $p$:

$$
u_i < p \implies \text{attempt reproduction}
$$

### 7.2 Reproduction Cost

On successful reproduction, deduct cost:

$$
E_i \leftarrow E_i - c_r
$$

Append parent $i$ to reproduction queue for later birth commits.

If energy is now exhausted:

$$
E_i \le 0 \implies \text{queue } i \text{ for post-reproduction death}
$$

### 7.3 Aging and Age Death (Second Check)

Every post-harvest survivor ages, including successful reproducers:

$$
a_i \leftarrow a_i + 1
$$

If age now exceeds maximum:

$$
a_i \ge A_{\max} \implies \ell_i \leftarrow \text{False}
$$

These age-marked agents remain in the population until the next tick's movement phase, when they are queued for death.

**Note**: Age-based death has two checkpoints:
- **Movement entry**: agents already at or beyond max age do not move
- **Biology exit**: agents aging into max age are marked dead for removal next tick

This dual-check ensures no agent can act multiple times after hitting max age.

## 8. Commit Phase

Let:

- $N_t$ be the pre-commit population
- $D_t$ be total queued deaths
- $B_t^{\text{raw}}$ be successful reproduction events

The engine computes:

$$
N_t^{\text{eff}} = N_t - D_t
$$

and:

$$
\mathrm{cap}_t = N_{\max} - N_t^{\text{eff}}
$$

Committed births are:

$$
B_t = \min(B_t^{\text{raw}}, \mathrm{cap}_t)
$$

Current commit order:

1. delete all queued dead agents
2. create the first $B_t$ queued children
3. regrow world resources

For a committed child $j$ of parent $i$:

$$
\begin{aligned}
(x_j, y_j) &\leftarrow (x_i, y_i) \\
a_j &\leftarrow 0 \\
\ell_j &\leftarrow 1 \\
o_j &\leftarrow 0 \\
E_j(0) &\sim \mathrm{UniformInt}(E_{\min}, E_{\max}^{\mathrm{init}} - 1)
\end{aligned}
$$

The parent's offspring counter increments only when the birth is actually committed.

## 9. Regrowth

After commit:

$$
R_{t+1}(y, x) = \min(F(y, x),\ R_t'(y, x) + r)
$$

where $R_t'$ is the post-harvest, post-commit resource field.

## 10. Model Boundary

Implemented now:

- 2D toroidal movement
- deterministic shared-cell harvest
- energy-coupled reproduction
- hard population cap
- age, metabolic, and post-reproduction death paths

Not yet implemented:

- explicit collision or crowding rules
- trait inheritance
- direct use of landscape `contrast` and `floor`
