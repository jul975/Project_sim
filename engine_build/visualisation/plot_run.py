import numpy as np
import matplotlib.pyplot as plt


from engine_build.metrics.metrics import SimulationMetrics
from engine_build.core.engineP4 import Engine
from engine_build.runner.regime_runner import BatchRunner
from engine_build.regimes.registry import get_regime_config



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



def plot_world_state() -> None:
    """
    Visualize the spatial state of the world.

    Produces three heatmaps:
        1) Fertility landscape
        2) Current resource levels
        3) Agent spatial density
    """
    regime_config = get_regime_config("stable")

    runner = BatchRunner(regime_config, n_runs=1, ticks=1000, batch_id=42)
    eng, _ = runner.run_single(runner.run_seeds[0], 1000)
    world = eng.world

    fertility = world.fertility
    resources = world.resources

    height, width = fertility.shape

    # --------------------------------------------------
    # Build agent density map
    # --------------------------------------------------
    density = np.zeros((height, width))

    for agent in eng.agents.values():
        x, y = agent.position
        density[y, x] += 1

    # --------------------------------------------------
    # Plot heatmaps
    # --------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Fertility
    im0 = axes[0].imshow(fertility, vmin=0, vmax=eng.config.max_resource_level)
    axes[0].set_title("Fertility Field")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)

    # Resources
    im1 = axes[1].imshow(resources)
    axes[1].set_title("Current Resources")
    plt.colorbar(im1, ax=axes[1], fraction=0.046)

    # Agent density
    im2 = axes[2].imshow(density)
    axes[2].set_title(f"Agent Density | {eng.get_agent_count()} agents")
    plt.colorbar(im2, ax=axes[2], fraction=0.046)

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_world_state()
    pass