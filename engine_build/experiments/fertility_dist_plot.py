import numpy as np
import matplotlib.pyplot as plt
from engine_build.runner.regime_runner import BatchRunner
from engine_build.regimes.registry import get_regime_config


def run_fertility_experiment():
    regime_config = get_regime_config("stable")
    runner = BatchRunner(regime_config , n_runs=1, ticks=1000, batch_id=42)
    eng, _ = runner.run_single(runner.run_seeds[0], 100)
    return eng


def plot_fertility_agent_distribution(engine):
    """
    Diagnostic plot showing fertility landscape and agent density.
    Useful to verify agents cluster in fertile regions.
    """

    world = engine.world

    fertility = world.fertility

    # agent density per cell
    density = np.zeros(world.world_size)

    for agent in engine.agents.values():
        density[agent.position] += 1

    # normalize density for easier comparison
    if density.max() > 0:
        density = density / density.max()

    # normalize fertility
    fertility_norm = fertility / fertility.max()

    plt.figure()

    plt.plot(fertility_norm, label="Fertility", linewidth=2)
    plt.plot(density, label="Agent density", linewidth=2)

    plt.title("Fertility vs Agent Distribution")
    plt.xlabel("World position")
    plt.ylabel("Normalized value")

    plt.legend()
    plt.show()
    
    corr = np.corrcoef(fertility_norm, density)[0,1]
    print(f"Fertility-Agent correlation: {corr:.3f}")


def run_and_plot_population_dynamics():
    eng = run_fertility_experiment()
    plot_fertility_agent_distribution(eng)

if __name__ == "__main__":
    pass