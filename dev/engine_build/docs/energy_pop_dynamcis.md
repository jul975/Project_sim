Excellent — I’ll turn this into a clean, structured, copy-paste-ready documentation file suitable for your `/docs` folder (e.g., `docs/energy_resource_population_dynamics.md`).

This is written as a **formal backbone document**, not conversational explanation.

---

# Energy–Resources–Population Dynamics

## Formal Coupled Discrete-Time System

---

# 1. System Overview

We define a deterministic, discrete-time dynamical system:

[
S_{t+1} = T(S_t)
]

where the global state is:

[
S_t = (W_t, A_t, R_t)
]

* (W_t) — world state (resources, fertility, time, regime flags)
* (A_t) — agent states (position, energy, alive, lineage, RNG)
* (R_t) — RNG states (movement / reproduction streams)

This document formalizes:

1. Exact micro-level dynamics (matches operator chain)
2. Mean-field reduction
3. Equilibrium and regime conditions
4. Role of dimensionless parameters ( \alpha, \beta, \gamma )
5. Practical parameter selection rules

---

# 2. Exact Micro-Level Dynamics

## 2.1 World Definition

For cell index ( x \in {0, \dots, L-1} ):

* Resource: ( R_t(x) \in [0, F(x)] )
* Fertility cap: ( F(x) )
* Regeneration rate: ( r \ge 0 )
* Harvest cap: ( H_{\max} > 0 )

Agents ( i = 1, \dots, N_t ):

* Position: ( x_i(t) )
* Energy: ( E_i(t) )
* Alive flag: ( A_i(t) \in {0,1} )

---

## 2.2 Operator Chain

[
T = \Pi \circ B \circ D \circ G \circ H \circ M
]

---

## 2.3 Movement Operator (M)

[
x_i'(t) = (x_i(t) + \Delta_i(t)) \bmod L
\quad\text{where}\quad \Delta_i(t) \in {-1,+1}
]

[
E_i'(t) = E_i(t) - c_m
]

---

## 2.4 Harvest Operator (H)

Sequential deterministic processing (sorted by ID):

[
h_i(t) = \min(H_{\max}, R_t^{(i-1)}(x_i'(t)))
]

[
E_i''(t) = E_i'(t) + h_i(t)
]

[
R_t^{(i)}(x_i'(t)) = R_t^{(i-1)}(x_i'(t)) - h_i(t)
]

---

## 2.5 Regeneration Operator (G)

[
R_{t+1}(x) = \min(F(x), R_t^{(N_t)}(x) + r)
]

---

## 2.6 Death Operator (D)

[
A_i(t+1) =
\begin{cases}
0 & \text{if } E_i''(t) \le 0 \
1 & \text{otherwise}
\end{cases}
]

---

## 2.7 Reproduction Operator (B)

### Current Model (Energy Independent)

[
B_i(t) = \mathbf{1}[U_i(t) < p]
]

### Planned Model (Energy-Gated + Depletion)

[
B_i(t) = \mathbf{1}[E_i''(t) \ge \theta] \cdot \mathbf{1}[U_i(t) < p]
]

[
E_i(t+1) = E_i''(t) - c_{\text{rep}} B_i(t)
]

---

## 2.8 Capacity Projection ( \Pi )

[
N_{\text{eff}} = N_t - |D_t|
]

[
\text{slots} = N_{\max} - N_{\text{eff}}
]

Commit first `slots` births deterministically.

---

# 3. Mean-Field Reduction

We define aggregates:

[
\bar{E}_t = \frac{1}{N_t} \sum_i E_i(t)
]

[
\bar{R}_t = \frac{1}{L} \sum_x R_t(x)
]

[
\rho_t = \frac{N_t}{L}
]

---

# 4. Mean Resource Dynamics

Total harvested per tick approximates:

[
\mathcal{H}*t \approx \min(N_t H*{\max}, \mathcal{R}_t)
]

Thus:

[
\frac{1}{L} \mathcal{H}*t \approx \min(\rho_t H*{\max}, \bar{R}_t)
]

Resource recursion:

[
\boxed{
\bar{R}_{t+1} \approx \bar{R}*t + r - \min(\rho_t H*{\max}, \bar{R}_t)
}
]

---

# 5. Mean Energy Dynamics

Mean harvest per agent:

[
\boxed{
\bar{h}*t = \min\left(H*{\max}, \frac{\bar{R}_t}{\rho_t}\right)
}
]

Energy recursion:

[
\boxed{
\bar{E}_{t+1} = \bar{E}_t - c_m + \bar{h}*t - c*{\text{rep}} \bar{b}_t
}
]

---

# 6. Population Dynamics

[
N_{t+1} \approx (s_t + \bar{b}_t) N_t
]

Stationary condition:

[
\boxed{
\bar{b}^* = 1 - s^*
}
]

Births must compensate deaths at equilibrium.

---

# 7. Equilibrium Conditions

## 7.1 Resource Equilibrium

Two regimes:

### Abundant Regime

[
\rho^* = \frac{r}{H_{\max}}
]

[
N^* \approx L \frac{r}{H_{\max}}
]

### Depleted Regime

[
\bar{R}^* = r
]

---

## 7.2 Energy Budget at Equilibrium

[
\boxed{
\bar{h}^* = c_m + c_{\text{rep}} \bar{b}^*
}
]

Energy surplus fuels reproduction.

---

# 8. Dimensionless Parameters

[
\alpha = \frac{c_m}{H_{\max}}
]

[
\beta = \frac{c_{\text{rep}}}{\theta}
]

[
\gamma = \frac{\theta}{c_m}
]

---

## 8.1 Interpretation

### α — Metabolic Pressure

Necessary survival condition:

[
\boxed{\alpha < 1}
]

If ( \alpha > 1 ), extinction pressure dominates.

---

### β — Reproductive Depletion

[
\beta \approx 1
]

Ensures reproduction forces recovery phase.

---

### γ — Maturity Scale

[
T_{\text{energy}} \approx \frac{\theta}{S} = \frac{\gamma c_m}{S}
]

Controls reproduction timescale.

---

# 9. Regime Classification

## Extinction Regime

If:

[
H_{\max} < c_m
]

Agents cannot sustain baseline metabolism.

---

## Stable Regime

Requires:

[
H_{\max} \gtrsim c_m
]

and density feedback:

[
\bar{h}(\rho) \text{ decreases with } \rho
]

---

## Explosion Risk

Occurs when reproduction is not energy-gated.

Energy gating is structurally necessary for bounded growth.

---

# 10. Practical Parameter Selection Procedure

1. Ensure ( \alpha < 1 )

2. Estimate density:

   [
   N^* \approx L \frac{r}{H_{\max}}
   ]

3. Choose:

   [
   \gamma \in [5,15]
   ]

4. Set:

   [
   \beta \approx 0.8 - 1.0
   ]

5. Validate using regime tests:

   * Extinction scenario
   * Stable bounded scenario
   * Saturation scenario

---

# 11. Variance Warning

Mean-field balance does not guarantee survival.

Near criticality:

[
\bar{h} \approx c_m
]

Random fluctuations cause extinction.

Robust systems require:

[
\bar{h} = c_m + \epsilon
]

with reproduction cost absorbing surplus.

---

# 12. Canonical Equilibrium Summary

[
\bar{h}(\bar{R}, \rho) = \min\left(H_{\max}, \frac{\bar{R}}{\rho}\right)
]

[
\bar{R}_{t+1} = \bar{R}_t + r - \rho \bar{h}
]

[
\bar{E}_{t+1} = \bar{E}*t - c_m + \bar{h} - c*{\text{rep}} \bar{b}
]

[
\bar{h}^* = c_m + c_{\text{rep}} \bar{b}^*
]

[
N^* \approx L \frac{r}{H_{\max}}
]

[
\alpha < 1 \quad \text{required for persistence}
]

---

If you'd like, I can now generate:

* A second document: `docs/energy_parameter_calibration_protocol.md`
* Or a LaTeX-ready version for formal write-up
* Or integrate this into your Stage II formalization structure

Your modeling level is now at “structured simulation theory” stage — the next step is enforcing invariants and validating regimes against this formal backbone.
