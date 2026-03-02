import matplotlib.pyplot as plt
from engine_build.metrics.metrics import SimulationMetrics


def plot_metrics(batch_metrics: dict[int, SimulationMetrics]) -> None:
    """
    Plot metrics for all runs in batch_metrics.
    Each metric category gets its own figure.
    """

    # -----------------------
    # 1) Population
    # -----------------------
    plt.figure(figsize=(10, 6))
    for seed, metrics in batch_metrics.items():
        plt.plot(metrics.population, label=f"seed {seed}")
    plt.title("Population Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Population")
    plt.legend()
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    pass