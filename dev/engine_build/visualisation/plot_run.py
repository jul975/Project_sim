import matplotlib.pyplot as plt
from engine_build.core.engineP4 import Engine
from engine_build.core.config import SimulationConfig



def plot_metrics(metrics):


    plt.figure(figsize=(10,8))

    plt.subplot(3,1,1)
    plt.plot(metrics.population)
    plt.title("Population")

    plt.subplot(3,1,2)
    plt.plot(metrics.births, label="Births")
    plt.plot(metrics.deaths, label="Deaths")
    plt.legend()
    plt.title("Births / Total Deaths")

    plt.subplot(3,1,3)
    for cause, series in metrics.death_causes.items():
        plt.plot(series, label=cause)

    plt.legend()
    plt.title("Deaths by Cause")

    plt.tight_layout()
    plt.show()
    
def main():
    SEED = 42
    STEPS = 1000

    eng = Engine(SEED, SimulationConfig())
    metrics = eng.run_with_metrics(STEPS)

    plot_metrics(metrics)

if __name__ == "__main__":
    main()


# python -m engine_build.analysis.plot_run