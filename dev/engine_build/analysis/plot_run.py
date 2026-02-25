import matplotlib.pyplot as plt
from engine_build.engineP4 import Engine
from engine_build.config import SimulationConfig

SEED = 42
STEPS = 1000

eng = Engine(SEED, SimulationConfig())
metrics = eng.run_with_metrics(STEPS)

plt.figure(figsize=(10,6))

plt.subplot(3,1,1)
plt.plot(metrics.population)
plt.title("Population")

plt.subplot(3,1,2)
plt.plot(metrics.mean_energy)
plt.title("Mean Energy")

plt.subplot(3,1,3)
plt.plot(metrics.births, label="Births")
plt.plot(metrics.deaths, label="Deaths")
plt.legend()

plt.tight_layout()
plt.show()


# python -m engine_build.analysis.plot_run