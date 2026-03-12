import numpy as np
import matplotlib.pyplot as plt

from engine_build.metrics.metrics import SimulationMetrics
from engine_build.runner.regime_runner import BatchRunResults


def plot_development_metrics(batch_metrics: BatchRunResults, seed: int | None = None) -> None:
    """
    Development visualization for simulation evaluation.

    Produces:
    1) Population ensemble trajectory
    2) Birth vs Death dynamics
    3) Death cause composition
    """

    if not batch_metrics:
        raise ValueError("No batch metrics provided.")

    # --------------------------------------------------
    # Stack population time-series
    # --------------------------------------------------
    populations = np.array([m.population for m in batch_metrics.batch_metrics.values()])

    n_runs, n_ticks = populations.shape
    ticks = np.arange(n_ticks)

    mean_pop = populations.mean(axis=0)
    std_pop = populations.std(axis=0)

    upper = mean_pop + std_pop
    lower = mean_pop - std_pop

    # ==================================================
    # FIGURE 1 — Population Ensemble
    # ==================================================

    plt.figure(figsize=(10,6))

    for m in batch_metrics.batch_metrics.values():
        plt.plot(ticks, m.population, alpha=0.15)

    plt.plot(ticks, mean_pop, linewidth=2, label="Mean")
    plt.fill_between(ticks, lower, upper, alpha=0.25, label="±1 STD")

    title = f"Population Dynamics | runs={n_runs} ticks={n_ticks}"
    if seed is not None:
        title += f" seed={seed}"

    plt.title(title)
    plt.xlabel("Tick")
    plt.ylabel("Population")

    plt.legend()
    plt.tight_layout()
    plt.show()

    # ==================================================
    # FIGURE 2 — Birth vs Death Dynamics
    # ==================================================

    births = np.array([m.births for m in batch_metrics.batch_metrics.values()])
    deaths = np.array([m.deaths for m in batch_metrics.batch_metrics.values()])

    mean_births = births.mean(axis=0)
    mean_deaths = deaths.mean(axis=0)

    plt.figure(figsize=(10,6))

    plt.plot(ticks, mean_births, label="Births / tick")
    plt.plot(ticks, mean_deaths, label="Deaths / tick")

    plt.title("Mean Birth / Death Dynamics")
    plt.xlabel("Tick")
    plt.ylabel("Events")

    plt.legend()
    plt.tight_layout()
    plt.show()

    # ==================================================
    # FIGURE 3 — Death Cause Composition
    # ==================================================

    cause_totals = {}

    for m in batch_metrics.batch_metrics.values():
        for cause, values in m.death_causes.items():
            cause_totals.setdefault(cause, []).append(np.sum(values))

    labels = []
    values = []

    for cause, v in cause_totals.items():
        labels.append(cause)
        values.append(np.mean(v))

    plt.figure(figsize=(8,6))
    plt.bar(labels, values)

    plt.title("Mean Death Causes (per run)")
    plt.ylabel("Deaths")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pass