import matplotlib.pyplot as plt
import numpy as np

from engine_build.analytics.observation.simulation_metrics import SimulationMetrics
from engine_build.runner.results import BatchRunResults


def _get_metrics_list(batch_results: BatchRunResults) -> list[SimulationMetrics]:
    """Extract run metrics from batch results and validate they exist."""
    if not batch_results.runs:
        raise ValueError("No runs found in batch results.")

    metrics_list = [
        run_artifacts.metrics
        for run_artifacts in batch_results.runs.values()
        if run_artifacts.metrics is not None
    ]

    if not metrics_list:
        raise ValueError("No metrics found in batch results.")

    return metrics_list


def _stack_series(
    metrics_list: list[SimulationMetrics],
    attr: str,
) -> np.ndarray:
    """Stack one metric across runs and require a consistent series length."""
    series = [np.asarray(getattr(metrics, attr), dtype=float) for metrics in metrics_list]
    lengths = {len(values) for values in series}

    if len(lengths) != 1:
        raise ValueError(
            f"Inconsistent lengths for metric '{attr}': {sorted(lengths)}"
        )

    return np.vstack(series)


def plot_development_metrics(
    batch_results: BatchRunResults,
    seed: int | None = None,
) -> None:
    """
    Quick development plots for batch run inspection.

    Produces:
    1) Population ensemble trajectory
    2) Mean births vs deaths per tick
    3) Mean energy trajectory, if sampled world-view frames exist
    4) Mean death-cause totals per run
    """
    metrics_list = _get_metrics_list(batch_results)

    populations = _stack_series(metrics_list, "population")
    births = _stack_series(metrics_list, "births")
    deaths = _stack_series(metrics_list, "deaths")

    n_runs, n_ticks = populations.shape
    ticks = np.arange(n_ticks)

    mean_pop = populations.mean(axis=0)
    std_pop = populations.std(axis=0)

    plt.figure(figsize=(10, 6))

    for metrics in metrics_list:
        plt.plot(ticks, metrics.population, alpha=0.15)

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

    plt.figure(figsize=(10, 6))
    plt.plot(ticks, births.mean(axis=0), label="Mean births / tick")
    plt.plot(ticks, deaths.mean(axis=0), label="Mean deaths / tick")

    plt.title("Birth / Death Dynamics")
    plt.xlabel("Tick")
    plt.ylabel("Events")
    plt.legend()
    plt.tight_layout()
    plt.show()

    energy_lengths = {
        len(metrics.mean_energy)
        for metrics in metrics_list
        if metrics.mean_energy
    }
    if energy_lengths:
        if len(energy_lengths) != 1:
            raise ValueError(
                f"Inconsistent lengths for metric 'mean_energy': {sorted(energy_lengths)}"
            )

        mean_energy = _stack_series(metrics_list, "mean_energy")
        energy_samples = np.arange(mean_energy.shape[1])
        energy_mean = mean_energy.mean(axis=0)
        energy_std = mean_energy.std(axis=0)

        plt.figure(figsize=(10, 6))
        plt.plot(energy_samples, energy_mean, linewidth=2, label="Mean energy")
        plt.fill_between(
            energy_samples,
            energy_mean - energy_std,
            energy_mean + energy_std,
            alpha=0.25,
            label="±1 STD",
        )

        plt.title("Mean Energy Trajectory")
        plt.xlabel("Sample Index")
        plt.ylabel("Energy")
        plt.legend()
        plt.tight_layout()
        plt.show()

    cause_totals: dict[str, list[float]] = {}
    for metrics in metrics_list:
        for cause, values in metrics.death_causes.items():
            cause_totals.setdefault(cause, []).append(float(np.sum(values)))

    labels = list(cause_totals.keys())
    values = [float(np.mean(cause_values)) for cause_values in cause_totals.values()]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values)

    plt.title("Mean Death Causes (per run)")
    plt.ylabel("Deaths")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pass
