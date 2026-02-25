This guide organizes your dimensionless ratios and calibration logic into a clean, professional Markdown format. It uses LaTeX for mathematical clarity and tables for quick reference.

---

# **Agent-Based Model: Dimensionless Ratio Calibration**

Stop tuning raw numbers blindly. By using **dimensionless ratios**, you can ensure your agents' metabolic and reproductive cycles remain stable regardless of the absolute scale of your variables.

## **1. Core Ratio Definitions**

| Ratio | Name | Formula | Recommended Range |
| --- | --- | --- | --- |
| \alpha | **Metabolic Pressure** | $\alpha = \frac{\text{movement\_cost}}{\text{max\_harvest}}$ | $0.6 - 0.9$ |
| $\beta$ | **Reproductive Depletion** | $\beta = \frac{\text{reproduction\_cost}}{\text{reproduction\_threshold}}$ | $0.8 - 1.0$ |
| $\gamma$ | **Energy Maturity Scale** | $\gamma = \frac{\text{reproduction\_threshold}}{\text{movement\_cost}}$ | $5 - 15$ |

---

## **2. Detailed Interpretation**

### **$\alpha$: Metabolic Pressure**

Determines the baseline difficulty of survival.

* **If $\alpha \to 1$:** Agents spend almost all gathered energy on movement. Survival is precarious.
* **If $\alpha \ll 1$:** Huge energy surplus. This typically leads to a population explosion.

### **$\beta$: Reproductive Depletion**

Determines the "recovery phase" after an agent gives birth.

* **If $\beta < 0.5$:** Agents remain well above the energy threshold after reproducing.
* **If $\beta \approx 1$:** Reproduction nearly exhausts the agent, requiring a significant recovery period.

### **$\gamma$: Energy Maturity Scale**

Controls the length of the lifecycle.

* **If $\gamma$ is small:** Agents reach reproductive maturity very quickly.
* **If $\gamma$ is large:** Long accumulation phase; reproduction is a rare, significant event.
* **Rule of Thumb:** $\text{reproduction\_threshold} = \gamma \times \text{movement\_cost}$.

---

## **3. Concrete Calibration Example**

Instead of picking random integers, use the following sequence to calibrate your world:

**Step 1: Set Environmental Constraints**

* $\text{movement\_cost} = 2$
* $\text{max\_harvest} = 3$
* **Result:** $\alpha = \frac{2}{3} \approx 0.67$ (Healthy survival, but requires effort).

**Step 2: Define Life Cycle via Ratios**

* Set $\gamma = 10 \rightarrow \text{reproduction\_threshold} = 20$.
* Set $\beta = 0.9 \rightarrow \text{reproduction\_cost} = 18$.

**Step 3: Analyze Timing**
If the average net surplus $S \approx 1$ per tick:

* $T_{\text{energy}} \approx 20 \text{ ticks}$ (Time to reach threshold).
* If we set probability $p = 0.1$, then the chance of reproduction $\frac{1}{p} \approx 10 \text{ ticks}$.
* **Conclusion:** Energy accumulation dominates the cycle, leading to smooth, non-explosive growth.

---

## **4. Population Stability Check ($R_0$)**

To avoid total extinction or infinite expansion, monitor the **Basic Reproduction Number ($R_0$)**:

$$R_0 = L \times R$$

Where:

* $L$ = Expected lifespan.
* $R$ = Expected reproduction rate per tick.

**Targets:**

* **$R_0 \approx 1.0 - 1.5$:** Stable/Manageable growth.
* **$R_0 \gg 1$:** Population explosion.
* **$R_0 < 1$:** Systemic extinction.

---

## **5. Implementation Strategy**

1. **Fix** $\text{movement\_cost}$ and $\text{max\_harvest}$ first.
2. **Measure** the empirical average energy gain ($\Delta E$) during a test run.
3. **Set** $\text{reproduction\_threshold} = \gamma \times \text{movement\_cost}$.
4. **Set** $\text{reproduction\_cost} \approx 0.9 \times \text{threshold}$.
5. **Choose** $p$ (probability of birth) so that $\frac{1}{p}$ is between $0.5 \times T_{\text{energy}}$ and $1.0 \times T_{\text{energy}}$.
6. **Run and Measure:** Record average lifespan and $R_0$.
7. **Adjust** only **one** ratio at a time.

**Would you like me to help you write a small Python snippet or pseudo-code to automate these ratio checks during your simulation's runtime?**