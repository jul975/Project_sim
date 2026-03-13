import numpy as np
import matplotlib.pyplot as plt

from engine_build.runner.regime_runner import BatchRunResults


def plot_development_metrics(batch_results: BatchRunResults, seed: int | None = None) -> None:
    """
    Quick development plots for batch run inspection.

    Produces:
    1) Population ensemble trajectory
    2) Mean births vs deaths per tick
    3) Mean energy trajectory
    4) Mean death-cause totals per run
    """

    if not batch_results.runs:
        raise ValueError("No runs found in batch results.")

    run_artifacts = list(batch_results.runs.values())

    metrics_list = [ra.metrics for ra in run_artifacts if ra.metrics is not None]
    if not metrics_list:
        raise ValueError("No metrics found in batch results.")

    # --------------------------------------------------
    # Stack time-series
    # --------------------------------------------------
    populations = np.array([m.population for m in metrics_list], dtype=float)
    births = np.array([m.births for m in metrics_list], dtype=float)
    deaths = np.array([m.deaths for m in metrics_list], dtype=float)
    mean_energy = np.array([m.mean_energy for m in metrics_list], dtype=float)

    n_runs, n_ticks = populations.shape
    ticks = np.arange(n_ticks)

    # --------------------------------------------------
    # FIGURE 1 — Population ensemble
    # --------------------------------------------------
    mean_pop = populations.mean(axis=0)
    std_pop = populations.std(axis=0)

    plt.figure(figsize=(10, 6))

    for m in metrics_list:
        plt.plot(ticks, m.population, alpha=0.15)

    plt.plot(ticks, mean_pop, linewidth=2, label="Mean population")
    plt.fill_between(
        ticks,
        mean_pop - std_pop,
        mean_pop + std_pop,
        alpha=0.25,
        label="±1 STD",
    )

    title = f"Population Dynamics | runs={n_runs} ticks={n_ticks}"
    if seed is not None:
        title += f" seed={seed}"

    plt.title(title)
    plt.xlabel("Tick")
    plt.ylabel("Population")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------------------------------------------------
    # FIGURE 2 — Mean births vs deaths
    # --------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(ticks, births.mean(axis=0), label="Mean births / tick")
    plt.plot(ticks, deaths.mean(axis=0), label="Mean deaths / tick")

    plt.title("Birth / Death Dynamics")
    plt.xlabel("Tick")
    plt.ylabel("Events")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------------------------------------------------
    # FIGURE 3 — Mean energy trajectory
    # --------------------------------------------------
    energy_mean = mean_energy.mean(axis=0)
    energy_std = mean_energy.std(axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(ticks, energy_mean, linewidth=2, label="Mean energy")
    plt.fill_between(
        ticks,
        energy_mean - energy_std,
        energy_mean + energy_std,
        alpha=0.25,
        label="±1 STD",
    )

    plt.title("Mean Energy Trajectory")
    plt.xlabel("Tick")
    plt.ylabel("Energy")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------------------------------------------------
    # FIGURE 4 — Mean death-cause totals per run
    # --------------------------------------------------
    cause_totals: dict[str, list[float]] = {}

    for m in metrics_list:
        for cause, values in m.death_causes.items():
            cause_totals.setdefault(cause, []).append(float(np.sum(values)))

    labels = list(cause_totals.keys())
    values = [float(np.mean(v)) for v in cause_totals.values()]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values)

    plt.title("Mean Death Causes (per run)")
    plt.ylabel("Deaths")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pass