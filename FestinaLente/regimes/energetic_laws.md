# Energetic laws and specifications defining a given Regime

## Context

Regimes need to have a central source of all truth in order to make regime comparison's, assumptions and validation possible.

As of V03, the main idea behind the first meaning full regime classification logic is formalizing the internal energy dynamics of a given simulation engine.

In order to do this, the energy dynamics of given system run has to be separated into 2 conceptually distinct parts. These being Energetic Laws, defining a given regime, and Energetic realization, defining the amount of energy inside the system on a given tick and/or over a given run.

## System Breakdown

1. theta defines regime-level ratios

    - These are abstract but interpretable regime controls.

2. compiler maps theta into world and agent energetic parameters

    - This turns ratios into actual integer-valued runtime parameters.

3. world and agent subsystems consume compiled values

    - Integration during Engine setup and run execution

4. Energetic Realization $S_t$

    - Analytics/processing level way of representing and evaluating system behaviour

## Formal

$$\Theta_E = energetic\ law$$
$$E_{int}​(t+1)−E_{int}​(t)−Φ_{in}​(t)+Φ_{loss}​(t)+Φ_{death}​(t)=0$$

What kind of energetic world did we instantiate?

$$S_t = energetic\ realization$$

What is the actual energetic configuration of that world right now?

---

### Engine level entry point

$$
Θ_E=the\ energetic\ assumptions\ of\ the\ world
$$

**Specified:**

$$
\Theta_E =
\Big(
E_{\mathrm{stock}},
\tau,
\rho_W,
\rho_A,
\eta,
\mu,
\gamma,
\beta
\Big)
$$

**where:**

- $E_{\mathrm{stock}}$ = stock scale
- $\tau$ = turnover or inflow intensity
- $\rho_W$ = world allocation fraction
- $\rho_A$ = agent scaling fraction
- $\eta$ = assimilation efficiency
- $\mu$ = maintenance intensity
- $\gamma$ = movement intensity
- $\beta$ = reproduction intensity

---

## Theta package

Defines regime-level ratios:

- mean cell capacity $\kappa$
- mean cell inflow $\phi$
- spatial inequality $\mathcal{S}$
- harvest ratio $\rho_h$
- reserve ratio $\rho_e$
- maintenance ratio $\rho_m$
- movement ratio $\rho_{\mathrm{move}}$
- reproduction threshold ratio $\rho_r$
- reproduction burden ratio $\rho_b$
