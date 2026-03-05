import matplotlib.pyplot as plt
import numpy as np
# NOTE: 
# future template, metrics not available yet.

def plot_dashboard(metrics):
    """
    Compact ecological diagnostics dashboard.

    metrics expected fields:
        population
        mean_energy
        births
        deaths
        total_resources
        mean_resources
        death_causes (dict[str, list])
    """

    T = len(metrics.population)
    time = np.arange(T)

    fig, axes = plt.subplots(5, 1, figsize=(12, 10), sharex=True)

    # -------------------------
    # 1️⃣ Population
    # -------------------------
    axes[0].plot(time, metrics.population, linewidth=2)
    axes[0].set_ylabel("Population")
    axes[0].set_title("Population Dynamics")
    axes[0].grid(True)

    # -------------------------
    # 2️⃣ Mean Energy
    # -------------------------
    axes[1].plot(time, metrics.mean_energy, linewidth=2)
    axes[1].set_ylabel("Mean Energy")
    axes[1].set_title("Energy State")
    axes[1].grid(True)

    # -------------------------
    # 3️⃣ Births vs Deaths Flux
    # -------------------------
    axes[2].plot(time, metrics.births, label="Births", alpha=0.8)
    axes[2].plot(time, metrics.deaths, label="Deaths", alpha=0.8)
    axes[2].set_ylabel("Events")
    axes[2].set_title("Demographic Flux")
    axes[2].legend()
    axes[2].grid(True)

    # -------------------------
    # 4️⃣ Resource Field Pressure
    # -------------------------
    axes[3].plot(time, metrics.total_resources, label="Total")
    axes[3].plot(time, metrics.mean_resources, label="Mean")
    axes[3].set_ylabel("Resources")
    axes[3].set_title("Resource Field")
    axes[3].legend()
    axes[3].grid(True)

    # -------------------------
    # 5️⃣ Death Causes Decomposition
    # -------------------------
    if hasattr(metrics, "death_causes") and metrics.death_causes:
        stacked = np.row_stack(list(metrics.death_causes.values()))
        labels = list(metrics.death_causes.keys())

        axes[4].stackplot(time, stacked, labels=labels, alpha=0.8)
        axes[4].legend(loc="upper right")
    else:
        axes[4].plot(time, metrics.deaths)

    axes[4].set_ylabel("Deaths")
    axes[4].set_title("Death Causes")
    axes[4].grid(True)

    axes[-1].set_xlabel("Time")

    plt.tight_layout()
    plt.show()