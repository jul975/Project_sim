from engine_build.core.engineP4 import Engine
from engine_build.core.config import SimulationConfig, EnergyConfig, EnergyRatios, REGIMES
from engine_build.visualisation.plot_run import plot_metrics 
from engine_build.metrics.metrics import SimulationMetrics
import argparse


# NOTE: 
        #   DECLARATIVE EXPERIMENT DEFINITION ONLY
        # 
        #   -   No logic, no control flow, no dependencies, no implementation details.
        #  
        #   -   STABLE_REGIME = SimulationConfig(...)
        #   -   GROWTH_REGIME = SimulationConfig(...)
        #   -   COLLAPSE_REGIME = SimulationConfig(...)


def make_config(alpha, beta, gamma) -> SimulationConfig:
    return SimulationConfig(
        energy_config=EnergyConfig(
            ratios=EnergyRatios(alpha=alpha, beta=beta, gamma=gamma)
        )
    )




def analyze_metrics(metrics):
    plot_metrics(metrics)
    

# NOTE: 
    #   -   Need to get regime as input and return regime specific config. to runner


if __name__ == "__main__":
    pass