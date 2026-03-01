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

    # -----------------------
    # 2) Births & Deaths
    # -----------------------
    plt.figure(figsize=(10, 6))
    for seed, metrics in batch_metrics.items():
        plt.plot(metrics.births, label=f"births seed {seed}")
        plt.plot(metrics.deaths, linestyle="--", label=f"deaths seed {seed}")
    plt.title("Births and Deaths Per Tick")
    plt.xlabel("Tick")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------
    # 3) Death Causes
    # -----------------------
    # One figure per death cause for clarity
    if batch_metrics:
        # Get cause keys from first run
        first_metrics = next(iter(batch_metrics.values()))
        for cause in first_metrics.death_causes.keys():

            plt.figure(figsize=(10, 6))

            for seed, metrics in batch_metrics.items():
                series = metrics.death_causes[cause]
                plt.plot(series, label=f"seed {seed}")

            plt.title(f"Deaths by Cause: {cause}")
            plt.xlabel("Tick")
            plt.ylabel("Count")
            plt.legend()
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    pass