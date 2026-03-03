import numpy as np
import matplotlib.pyplot as plt
from engine_build.metrics.metrics import SimulationMetrics


def plot_metrics(batch_metrics: dict[int, SimulationMetrics]) -> None:
    """
    Produces:
    1) Mean population trajectory with ±1 STD band
    2) Individual runs plotted within STD envelope
    """

    if not batch_metrics:
        raise ValueError("No batch metrics provided.")

    # --------------------------------------------------
    # Stack population time-series
    # --------------------------------------------------
    populations = np.array(
        [metrics.population for metrics in batch_metrics.values()]
    )  # shape = (n_runs, n_ticks)

    n_runs, n_ticks = populations.shape
    ticks = np.arange(n_ticks)

    # --------------------------------------------------
    # Compute ensemble statistics
    # --------------------------------------------------
    mean_pop = populations.mean(axis=0)
    std_pop = populations.std(axis=0)

    upper = mean_pop + std_pop
    lower = mean_pop - std_pop

    # ==================================================
    # FIGURE 1 — Mean + STD Band
    # ==================================================
    plt.figure(figsize=(10, 6))

    for metrics in batch_metrics.values():
        plt.plot(ticks, metrics.population, alpha=0.15)

    plt.plot(ticks, mean_pop, linewidth=2)
    plt.fill_between(ticks, lower, upper, alpha=0.3)
    
    plt.title("Mean Population Trajectory (±1 STD)")
    plt.xlabel("Tick")
    plt.ylabel("Population")
    plt.tight_layout()
    plt.show()

    # ==================================================
    # FIGURE 2 — Individual Runs Within STD Envelope
    # ==================================================
    plt.figure(figsize=(10, 6))

    # Plot STD envelope first
    plt.fill_between(ticks, lower, upper, alpha=0.2)

    # Plot individual runs
    for run_id, metrics in batch_metrics.items():
        plt.plot(ticks, metrics.population, alpha=0.6)

    plt.plot(ticks, mean_pop, linewidth=2)

    plt.title("Individual Runs Within Ensemble STD Band")
    plt.xlabel("Tick")
    plt.ylabel("Population")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pass