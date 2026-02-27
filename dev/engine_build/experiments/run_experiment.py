from engine_build.core.engineP4 import Engine
from engine_build.core.config import SimulationConfig, EnergyConfig, EnergyRatios
from engine_build.visualisation.plot_run import plot_metrics
import argparse


REGIMES = {
    "extinction": (1.2, 1.0, 5),
    "stable": (0.6, 0.8, 10),
    "saturated": (0.4, 0.6, 6),
}

def make_config(alpha, beta, gamma):
    return SimulationConfig(
        energy_config=EnergyConfig(
            ratios=EnergyRatios(alpha=alpha, beta=beta, gamma=gamma)
        )
    )

def run_experiment(alpha, beta, gamma, seed=42, steps=1000):
    config = make_config(alpha, beta, gamma)
    eng = Engine(seed, config)
    return eng.run_with_metrics(steps)

def analyze_metrics(metrics):
    plot_metrics(metrics)
    

def main(regime: str = "stable"):
    metrics = run_experiment(*REGIMES[regime])
    analyze_metrics(metrics)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ecosystem Metrics Analysis Tool")

    parser.add_argument(
        "--regime",
        choices=["extinction", "stable", "saturated"],
        default="stable",
        help="Select regime type"
    )

    args = parser.parse_args()

    if args.regime == "extinction":
        main("extinction")
    elif args.regime == "stable":
        main("stable")
    elif args.regime == "saturated":
        main("saturated")