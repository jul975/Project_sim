
from dataclasses import dataclass
import numpy as np
from FestinaLente.analytics.derive.run.fingerprint import Fingerprint





@dataclass(frozen=True)
class AggregatedFingerprint:
    """ Aggregated fingerprint over a batch of runs. """
    final_populations: list[int] 
    mean_population_over_runs: float
    std_mean_population_over_runs: float
    extinction_rate: float
    cap_hit_rate: float
    birth_death_ratio: float
    mean_time_cv_over_runs: float

    batch_near_cap_rate: float
    batch_near_low_population_rate: float




def get_aggregate_fingerprints(fingerprints : list[Fingerprint]) -> AggregatedFingerprint:
    """Aggregate run-level fingerprints across a batch."""  
    if not fingerprints:
        raise ValueError("No fingerprints to aggregate")


    # 1) simple mean and std aggregation
    final_populations = [f.final_population for f in fingerprints]
    mean_pop_over_runs = float(np.mean([f.mean_population for f in fingerprints]))
    std_mean_population_over_runs = float(np.std([f.mean_population for f in fingerprints]))



    # 2) extinction rate
    # note, conditional 0, watch out for truncation of mean extinction! 
    extinction_rate = float(np.mean([f.extinction_tick is not None for f in fingerprints]))
    # 3) cap hit rate
    # note, cap_hit_rate can not be None, so no need to handle it. 
    cap_hit_rate = float(np.mean([f.cap_hit_rate for f in fingerprints]))

    # 4) mean deaths and births per tick
    mean_deaths_per_tick = float(np.mean([f.mean_deaths_per_tick for f in fingerprints]))
    mean_births_per_tick = float(np.mean([f.mean_births_per_tick for f in fingerprints]))

    # NOTE: No deaths in the tail window => ratio is treated as infinite.
    if mean_deaths_per_tick == 0:
        if mean_births_per_tick == 0:
            birth_death_ratio = 0.0
        else:
            birth_death_ratio = float("inf")
    else:
        birth_death_ratio = float(mean_births_per_tick / mean_deaths_per_tick)

    cv_per_run = []
    for f in fingerprints:
        if f.mean_population > 0:
            cv_per_run.append(f.std_population / f.mean_population)
        else:
            cv_per_run.append(0.0)  # extinction run → no fluctuation



    mean_time_cv_over_runs = float(np.mean(cv_per_run))

    batch_near_cap_rate = float(np.mean([f.near_cap_rate for f in fingerprints]))
    batch_near_low_population_rate = float(np.mean([f.low_population_rate for f in fingerprints]))

    return AggregatedFingerprint(
        final_populations=final_populations,

        mean_population_over_runs=mean_pop_over_runs,

        std_mean_population_over_runs=std_mean_population_over_runs,

        extinction_rate=extinction_rate,

        cap_hit_rate=cap_hit_rate,

        birth_death_ratio=birth_death_ratio,

        mean_time_cv_over_runs = mean_time_cv_over_runs,

        batch_near_cap_rate=batch_near_cap_rate,
        batch_near_low_population_rate=batch_near_low_population_rate,

    )



if __name__ == "__main__":
    pass