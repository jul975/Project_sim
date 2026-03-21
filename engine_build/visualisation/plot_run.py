import numpy as np
import matplotlib.pyplot as plt

from engine_build.metrics.metrics import SimulationMetrics
from engine_build.core.step_results import WorldView


def _require_batch_metrics(batch_metrics: dict[int, SimulationMetrics]) -> None:
    if not batch_metrics:
        raise ValueError("No batch metrics provided.")


def _stack_metric(
    batch_metrics: dict[int, SimulationMetrics],
    attr: str,
) -> np.ndarray:
    """
    Stack a per-tick metric across runs into shape (n_runs, n_ticks).

    Raises if run lengths are inconsistent.
    """
    series = [np.asarray(getattr(metrics, attr), dtype=float) for metrics in batch_metrics.values()]
    lengths = {len(x) for x in series}
    if len(lengths) != 1:
        raise ValueError(f"Inconsistent lengths for metric '{attr}': {sorted(lengths)}")
    return np.vstack(series)


def _ensemble_stats(stacked: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = stacked.mean(axis=0)
    std = stacked.std(axis=0)
    ticks = np.arange(stacked.shape[1])
    return ticks, mean, std


def _plot_ensemble_panel(
    ax: plt.Axes,
    batch_metrics: dict[int, SimulationMetrics],
    attr: str,
    title: str,
    ylabel: str,
    alpha_runs: float = 0.15,
) -> None:
    stacked = _stack_metric(batch_metrics, attr)
    ticks, mean, std = _ensemble_stats(stacked)

    for metrics in batch_metrics.values():
        ax.plot(ticks, getattr(metrics, attr), alpha=alpha_runs)

    ax.plot(ticks, mean, linewidth=2)
    ax.fill_between(ticks, mean - std, mean + std, alpha=0.25)

    ax.set_title(title)
    ax.set_xlabel("Tick")
    ax.set_ylabel(ylabel)


def _build_density_from_positions(
    positions: np.ndarray,
    world_shape: tuple[int, int],
) -> np.ndarray:
    """
    Convert positions array of shape (n_agents, 2) into a density grid of shape (H, W).
    Assumes positions are stored as [x, y].
    """
    height, width = world_shape
    density = np.zeros((height, width), dtype=np.int32)

    if positions.size == 0:
        return density

    for x, y in positions:
        density[y, x] += 1

    return density


def plot_batch_metrics(batch_metrics: dict[int, SimulationMetrics]) -> None:
    """
    Batch-level overview of the updated metric system.

    Produces:
    1) Population ensemble
    2) Mean energy ensemble
    3) Births ensemble
    4) Deaths ensemble
    """
    _require_batch_metrics(batch_metrics)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    _plot_ensemble_panel(
        axes[0, 0],
        batch_metrics,
        attr="population",
        title="Population Trajectory (Mean ±1 STD)",
        ylabel="Population",
    )

    _plot_ensemble_panel(
        axes[0, 1],
        batch_metrics,
        attr="mean_energy",
        title="Mean Energy Trajectory (Sampled Frames)",
        ylabel="Mean Energy",
    )

    _plot_ensemble_panel(
        axes[1, 0],
        batch_metrics,
        attr="births",
        title="Births Per Tick (Mean ±1 STD)",
        ylabel="Births",
    )

    _plot_ensemble_panel(
        axes[1, 1],
        batch_metrics,
        attr="deaths",
        title="Deaths Per Tick (Mean ±1 STD)",
        ylabel="Deaths",
    )

    fig.suptitle("Batch Metrics Overview", fontsize=14)
    plt.tight_layout()
    plt.show()


def plot_single_run_metrics(metrics: SimulationMetrics, run_id: int | None = None) -> None:
    """
    Single-run diagnostic plots.

    Produces:
    1) Population over time
    2) Mean energy over sampled world-view frames
    3) Births and deaths over time
    4) Death causes over time
    """
    title_suffix = f" | Run {run_id}" if run_id is not None else ""

    ticks = np.arange(len(metrics.population))
    energy_ticks = np.arange(len(metrics.mean_energy))

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    axes[0, 0].plot(ticks, metrics.population)
    axes[0, 0].set_title(f"Population{title_suffix}")
    axes[0, 0].set_xlabel("Tick")
    axes[0, 0].set_ylabel("Population")

    axes[0, 1].plot(energy_ticks, metrics.mean_energy)
    axes[0, 1].set_title(f"Mean Energy (Sampled Frames){title_suffix}")
    axes[0, 1].set_xlabel("Sample Index")
    axes[0, 1].set_ylabel("Mean Energy")

    axes[1, 0].plot(ticks, metrics.births, label="Births")
    axes[1, 0].plot(ticks, metrics.deaths, label="Deaths")
    axes[1, 0].set_title(f"Births vs Deaths{title_suffix}")
    axes[1, 0].set_xlabel("Tick")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].legend()

    for cause, values in metrics.death_causes.items():
        axes[1, 1].plot(ticks, values, label=cause)

    axes[1, 1].set_title(f"Death Causes{title_suffix}")
    axes[1, 1].set_xlabel("Tick")
    axes[1, 1].set_ylabel("Deaths")
    axes[1, 1].legend()

    fig.suptitle("Single Run Metrics", fontsize=14)
    plt.tight_layout()
    plt.show()


def plot_population_envelope(batch_metrics: dict[int, SimulationMetrics]) -> None:
    """
    Cleaner dedicated population figure:
    all runs + mean ± std envelope.
    """
    _require_batch_metrics(batch_metrics)

    populations = _stack_metric(batch_metrics, "population")
    ticks, mean_pop, std_pop = _ensemble_stats(populations)

    plt.figure(figsize=(11, 6))

    for metrics in batch_metrics.values():
        plt.plot(ticks, metrics.population, alpha=0.18)

    plt.plot(ticks, mean_pop, linewidth=2)
    plt.fill_between(ticks, mean_pop - std_pop, mean_pop + std_pop, alpha=0.25)

    plt.title("Population Ensemble Trajectory")
    plt.xlabel("Tick")
    plt.ylabel("Population")
    plt.tight_layout()
    plt.show()


def plot_world_view_frame(
    world_view: WorldView,
    frame_index: int | None = None,
) -> None:
    """
    Plot one sampled world-view frame as:
    1) resource grid
    2) density grid
    3) agent energy histogram
    """
    resources = world_view.resources
    density = _build_density_from_positions(world_view.positions, resources.shape)
    energies = world_view.energies

    title_suffix = f" | Frame {frame_index}" if frame_index is not None else ""

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    im0 = axes[0].imshow(resources)
    axes[0].set_title(f"Resources{title_suffix}")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)

    im1 = axes[1].imshow(density)
    axes[1].set_title(f"Agent Density{title_suffix}")
    plt.colorbar(im1, ax=axes[1], fraction=0.046)

    axes[2].hist(energies, bins=20)
    axes[2].set_title(f"Energy Distribution{title_suffix}")
    axes[2].set_xlabel("Energy")
    axes[2].set_ylabel("Count")

    for ax in axes[:2]:
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    plt.show()


def plot_world_view_samples(
    metrics: SimulationMetrics,
    sample_indices: list[int] | None = None,
) -> None:
    """
    Plot a few sampled world-view frames from one run.

    Default: first, middle, last available sampled frame.
    """
    if not metrics.world_view:
        raise ValueError("No world_view data available for this run.")

    n_frames = len(metrics.world_view)

    if sample_indices is None:
        sample_indices = sorted(set([0, n_frames // 2, n_frames - 1]))

    for idx in sample_indices:
        if idx < 0 or idx >= n_frames:
            raise IndexError(f"Frame index out of range: {idx}")
        plot_world_view_frame(metrics.world_view[idx], frame_index=idx)


def plot_world_view_summary(metrics: SimulationMetrics) -> None:
    """
    Summarize sampled world-view frames over one run.

    Produces:
    1) occupancy rate per sampled frame
    2) mean resource level per sampled frame
    3) mean sampled energy per sampled frame
    4) peak density per sampled frame
    """
    if not metrics.world_view:
        raise ValueError("No world_view data available for this run.")

    occupancy_rates = []
    mean_resources = []
    mean_energies = []
    peak_densities = []

    for frame in metrics.world_view:
        density = _build_density_from_positions(frame.positions, frame.resources.shape)

        occupancy_rates.append(float(np.mean(density > 0)))
        mean_resources.append(float(np.mean(frame.resources)))
        mean_energies.append(float(np.mean(frame.energies)) if frame.energies.size else 0.0)
        peak_densities.append(float(np.max(density)))

    x = np.arange(len(metrics.world_view))

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    axes[0, 0].plot(x, occupancy_rates)
    axes[0, 0].set_title("Occupancy Rate per Sampled Frame")
    axes[0, 0].set_xlabel("Sample Index")
    axes[0, 0].set_ylabel("Occupancy Rate")

    axes[0, 1].plot(x, mean_resources)
    axes[0, 1].set_title("Mean Resource Level per Sampled Frame")
    axes[0, 1].set_xlabel("Sample Index")
    axes[0, 1].set_ylabel("Mean Resource")

    axes[1, 0].plot(x, mean_energies)
    axes[1, 0].set_title("Mean Energy per Sampled Frame")
    axes[1, 0].set_xlabel("Sample Index")
    axes[1, 0].set_ylabel("Mean Energy")

    axes[1, 1].plot(x, peak_densities)
    axes[1, 1].set_title("Peak Density per Sampled Frame")
    axes[1, 1].set_xlabel("Sample Index")
    axes[1, 1].set_ylabel("Peak Density")

    fig.suptitle("World View Summary", fontsize=14)
    plt.tight_layout()
    plt.show()