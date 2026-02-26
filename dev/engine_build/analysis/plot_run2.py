
import matplotlib.pyplot as plt
from engine_build.engineP4 import Engine
from engine_build.config import SimulationConfig

SEED = 42
STEPS = 1000

eng = Engine(SEED, SimulationConfig())
metrics = eng.run_with_metrics(STEPS)


# Create a figure with 4 rows and 1 column
fig, axs = plt.subplots(4, 1, figsize=(10, 15), sharex=True)

# 1. Population
axs[0].plot(metrics.population)
axs[0].set_title("Population")

# 2. Mean Energy
axs[1].plot(metrics.mean_energy)
axs[1].set_title("Mean Energy")

# 3. Births/Deaths
axs[2].plot(metrics.births, label="Births")
axs[2].plot(metrics.deaths, label="Deaths")
axs[2].legend()
axs[2].set_title("Births / Total Deaths")

# 4. Death Causes
for cause, series in metrics.death_causes.items():
    axs[3].plot(series, label=cause)
axs[3].legend()
axs[3].set_title("Deaths by Cause")

# Adjust spacing so titles don't hit the x-axis of the plot above
plt.tight_layout()
plt.show()