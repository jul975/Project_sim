Good. Below is a **GitHub-ready `docs/analysis.md`** template structured like a short technical research note.

This is written to:

* Match your 12-week roadmap scope
* Reflect deterministic + analytical rigor
* Avoid overclaiming
* Look professional to researchers / ML infra teams
* Be clean enough for internship review

You can paste this directly into `docs/analysis.md`.

---

# Analysis of a Deterministic Agent-Based Simulation with Resource Constraints

---

## Abstract

This document presents a formal analysis of a deterministic agent-based simulation framework with resource-limited energy dynamics and energy-gated stochastic reproduction.

The simulation is implemented as a deterministic state transition system with canonical serialization of stochastic state, enabling exact replay and controlled experimentation.

We derive:

* Mean-field population equilibrium conditions
* Reproduction timescale estimates
* Early-stage branching approximations
* Logistic-like ODE limits
* Stability and extinction regimes

Simulation outcomes are compared against analytical predictions.

---

# 1. Formal System Definition

The global state at time ( t ) is defined as:

[
S_t = (W_t, A_t, R_t)
]

Where:

* ( W_t ) — world state (resource field, fertility caps)
* ( A_t ) — agent set
* ( R_t ) — RNG internal states

The system evolves via a deterministic transition operator:

[
S_{t+1} = T(S_t)
]

All entropy sources are internalized within ( S_t ), making the system deterministic under fixed seed.

---

# 2. Agent-Level Energy Dynamics

For each agent ( i ):

[
E_i(t+1) = E_i(t) - c_m + h_i(t) - c_r B_i(t)
]

Where:

* ( c_m ) — metabolic movement cost
* ( h_i(t) = \min(R(x_i(t)), H_{\max}) )
* ( c_r ) — reproduction cost
* ( B_i(t) \in {0,1} ) — reproduction event indicator

Reproduction occurs if:

[
E_i(t) \ge \theta \quad \text{and} \quad U_i(t) < p
]

This creates a coupling between ecological constraints and branching dynamics.

---

# 3. Global Resource Balance

Let:

* ( L ) — number of spatial cells
* ( r ) — regeneration rate per cell
* ( N_t ) — population size
* ( \bar h_t ) — mean harvest per agent

Total resource inflow per tick:

[
G_t \approx L r \phi_t
]

where ( \phi_t ) is the fraction of unsaturated cells.

Total harvest per tick:

[
H_t = N_t \bar h_t
]

At steady state:

[
N^* \bar h^* \approx L r \phi^*
]

This defines a first-order equilibrium condition.

---

# 4. Mean-Field Approximation

Assuming sufficient mixing and unsaturated regime (( \phi \approx 1 )):

[
N^* \approx \frac{L r}{H_{\max}}
]

This gives a throughput-limited equilibrium population.

Limitations:

* Ignores spatial clustering
* Ignores sequential harvest bias
* Assumes availability probability ( q \approx 1 )

---

# 5. Maintenance Condition

Expected energy drift:

[
\mathbb{E}[\Delta E] \approx \bar h - c_m
]

To prevent systematic decline:

[
\bar h \gtrsim c_m
]

Define metabolic pressure:

[
\alpha = \frac{c_m}{H_{\max}}
]

If ( \alpha \to 1 ), survival requires near-maximal harvest efficiency.

---

# 6. Reproduction Timescale Approximation

Define net surplus:

[
S = \bar h - c_m
]

Energy accumulation time:

[
T_{\text{energy}} \approx \frac{\theta}{S}
]

Stochastic reproduction time:

[
T_{\text{stochastic}} = \frac{1}{p}
]

Effective reproduction interval:

[
T_{\text{rep}} \approx \max\left(\frac{\theta}{S}, \frac{1}{p}\right)
]

Expected reproduction rate:

[
R \approx \frac{1}{T_{\text{rep}}}
]

---

# 7. Branching Process Approximation

In early growth phase (low density):

Let mean offspring per agent:

[
\mu = L_{\text{life}} \cdot R
]

If:

* ( \mu < 1 ) → extinction almost certain
* ( \mu > 1 ) → non-zero survival probability

For Poisson reproduction:

[
q = e^{-\mu(1-q)}
]

gives extinction probability ( q ).

This approximates early regime classification.

---

# 8. Logistic ODE Limit

In large-scale limit:

[
\frac{dN}{dt} = \alpha N - \beta N^2
]

Where:

* Linear term arises from reproduction surplus
* Quadratic term arises from resource competition

Simulation trajectories are compared against logistic approximation.

---

# 9. Simulation vs Analytical Comparison

For parameter sets:

* ( (c_m, H_{\max}, r, \theta, p) )

We measure:

* Equilibrium population ( N^* )
* Extinction frequency
* Variance of ( N_t )
* Mean energy

Comparison:

* Mean-field equilibrium vs observed equilibrium
* Branching prediction vs extinction rate

Deviations highlight effects of:

* Sequential harvest
* Finite-size noise
* Spatial clustering

---

# 10. Stability Regimes

Regimes classified as:

| Regime     | Condition              | Observed Behavior      |
| ---------- | ---------------------- | ---------------------- |
| Extinction | ( \bar h < c_m )       | Collapse               |
| Critical   | ( \bar h \approx c_m ) | High variance          |
| Stable     | ( \bar h > c_m )       | Bounded population     |
| Saturation | Resource-limited       | Throughput equilibrium |

---

# 11. Determinism & Reproducibility

All experiments are reproducible due to:

* Canonical state hashing
* RNG state inclusion
* Deterministic event ordering
* Seed-controlled entropy streams

This ensures regime analysis is not artifact of hidden nondeterminism.

---

# 12. Limitations

* 1D toroidal spatial model
* Sequential harvest bias
* No adaptive strategy
* No distributed execution
* Mean-field approximations assume mixing

---

# 13. Future Analytical Extensions

* Explicit occupancy-based harvest probability model
* Variance and covariance structure of ( N_t )
* Formal extinction time bounds
* Stochastic differential equation approximation
* Multi-dimensional spatial extension

---

# Closing Statement

This framework demonstrates how:

* Stochastic agent systems can be formalized deterministically
* Resource constraints produce emergent logistic-like behavior
* Analytical approximations can be compared against simulation
* Architectural rigor supports experimental reproducibility

--- 
# Author
Jules Lowette
