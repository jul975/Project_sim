
# engine_build/validation/contracts.py
from dataclasses import dataclass

@dataclass(frozen=True)
class RegimeContract:
    min_extinction_rate: float | None = None
    max_extinction_rate: float | None = None

    min_cap_hit_rate: float | None = None
    max_cap_hit_rate: float | None = None

    min_low_population_rate: float | None = None
    max_low_population_rate: float | None = None

    min_birth_death_ratio: float | None = None
    max_birth_death_ratio: float | None = None

    min_mean_population_ratio: float | None = None
    max_mean_population_ratio: float | None = None

    min_time_cv: float | None = None
    max_time_cv: float | None = None



REGIME_CONTRACTS = {
    "stable": RegimeContract(
        max_extinction_rate=0.10,
        max_cap_hit_rate=0.20,
        min_birth_death_ratio=0.95,
        max_birth_death_ratio=1.05,
        max_time_cv=0.10,
        max_mean_population_ratio=0.20,   # if true stable should stay low/interior
    ),
    "extinction": RegimeContract(
        min_extinction_rate=0.80,
        max_cap_hit_rate=0.10,
        max_mean_population_ratio=0.10,
        max_birth_death_ratio=0.95,
    ),
    "saturated": RegimeContract(
        min_cap_hit_rate=0.20,
        min_mean_population_ratio=0.80,
        max_extinction_rate=0.05,
    ),
}