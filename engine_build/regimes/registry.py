

from engine_build.core.config import SimulationConfig, EnergyConfig, EnergyRatios

## TESTING REGIMES
REGIMES = {
    "extinction": (1.2, 1.0, 5),
    "stable": (0.6, 0.8, 10),
    "saturated": (0.4, 0.6, 6),
}





def make_config(alpha, beta, gamma) -> SimulationConfig:
    return SimulationConfig(
        energy_config=EnergyConfig(
            ratios=EnergyRatios(alpha=alpha, beta=beta, gamma=gamma)
        )
    )


def get_regime_config(regime : str) -> SimulationConfig:
    if regime not in REGIMES:
        raise ValueError(f"Unknown regime: {regime}")
    return make_config(*REGIMES[regime])