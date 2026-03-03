
import numpy as np
from engine_build.metrics.metrics import SimulationMetrics
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass(frozen=True)
class Fingerprint:

    # 1) population metrics
    min_population: int
    max_population: int
    mean_population: float
    std_population: float
    range_population: float
    cap_hit_rate: float


    # 2) extinction tick
    extinction_tick: Optional[int]

    # 3) mean deaths and births per tick
    mean_deaths_per_tick: float
    mean_births_per_tick: float

    # 4) mean and proportion of deaths cause
    mean_deaths_cause_tail: Dict[str, float]
    proportion_deaths_cause_tail: Dict[str, float]


@dataclass(frozen=True)
class AggregatedFingerprint:
    mean_population_over_runs: float
    std_mean_population_over_runs: float
    extinction_rate: float
    cap_hit_rate: float
    birth_death_ratio: float
    mean_time_cv_over_runs: float

"""
# Pure transformations

    - compute_fingerprint(metrics)
    - compute_tail_stats(...)
    - compute_extinction_flags(...)
    - compute_cap_hit_rate(...)

    No engine.
    No simulation.
    Just math on arrays.


"""





def compute_fingerprint(metrics : SimulationMetrics, tail_start : np.int64)-> Fingerprint:
    if tail_start < 0 or tail_start >= len(metrics.population):
        raise ValueError(f"tail_start {tail_start} out of bounds for metrics of length {len(metrics.population)}")

    population_tail = metrics.population[tail_start:]
    births_tail = metrics.births[tail_start:]
    deaths_tail = metrics.deaths[tail_start:]
    total_deaths_tail = np.sum(deaths_tail)


    
    # 1) population metrics
    min_tail = min(population_tail)
    max_tail = max(population_tail)
    mean_tail = np.mean(population_tail)
    std_tail = np.std(population_tail)
    range_tail = max_tail - min_tail

    # NOTE: review, didnt think about mechanism at first, 
    cap_hit_rate = (
        np.array(population_tail) == metrics.max_agent_count
        ).mean()
    
    # NOTE: review next() => usefull and didnt think about it for a while. => generator so no list construction
    
    # 2) extinction tick
    extinction_tick = next((i + tail_start for i, pop in enumerate(population_tail) if pop == 0), None)
    
    
    # 3) mean deaths and births per tick
    mean_deaths_per_tick = np.mean(deaths_tail)
    mean_births_per_tick = np.mean(births_tail)
    
    # 4) mean and proportion of deaths cause
    # NOTE: divide by 0 needed to be handled 
    mean_deaths_cause_tail = {
        cause : np.mean(death_causes[tail_start:])
        for cause, death_causes in metrics.death_causes.items()}
    
    if total_deaths_tail > 0:
        proportion_deaths_cause_tail = {
            cause: np.sum(death_causes[tail_start:]) / total_deaths_tail
            for cause, death_causes in metrics.death_causes.items()
    }
    else:
        proportion_deaths_cause_tail = {
            cause: 0.0
            for cause in metrics.death_causes
    }
    

    # condense later
    return Fingerprint(
        min_population=min_tail,
        max_population=max_tail,
        mean_population=mean_tail,
        std_population=std_tail,
        range_population=range_tail,
        cap_hit_rate=cap_hit_rate,
        extinction_tick=extinction_tick,
        mean_deaths_per_tick=mean_deaths_per_tick,
        mean_births_per_tick=mean_births_per_tick,
        mean_deaths_cause_tail=mean_deaths_cause_tail,
        proportion_deaths_cause_tail=proportion_deaths_cause_tail
    )


def get_aggregate_fingerprints(fingerprints : list[Fingerprint]) -> AggregatedFingerprint:
    if not fingerprints:
        raise ValueError("No fingerprints to aggregate")


    # 1) simple mean and std aggregation
    mean_pop_over_runs = np.mean([f.mean_population for f in fingerprints])
    std_mean_population_over_runs = np.std([f.mean_population for f in fingerprints])



    # 2) extinction rate
    # note, conditional 0, watch out for truncation of mean extinction! 
    extinction_rate = np.mean([f.extinction_tick is not None for f in fingerprints])
    # NOTE: think about extinction time and mean extinction tick computes

    # 3) cap hit rate
    # note, cap_hit_rate can not be None, so no need to handle it. 
    cap_hit_rate = np.mean([f.cap_hit_rate for f in fingerprints])

    # 4) mean deaths and births per tick
    mean_deaths_per_tick = np.mean([f.mean_deaths_per_tick for f in fingerprints])
    mean_births_per_tick = np.mean([f.mean_births_per_tick for f in fingerprints])

    if mean_deaths_per_tick > 0:
        birth_death_ratio = mean_births_per_tick / mean_deaths_per_tick
    else:
        birth_death_ratio = np.inf

    cv_per_run = []
    for f in fingerprints:
        if f.mean_population > 0:
            cv_per_run.append(f.std_population / f.mean_population)
        else:
            cv_per_run.append(0.0)  # extinction run → no fluctuation



    mean_time_cv_over_runs = np.mean(cv_per_run)

    return AggregatedFingerprint(
        mean_population_over_runs=mean_pop_over_runs,

        std_mean_population_over_runs=std_mean_population_over_runs,

        extinction_rate=extinction_rate,

        cap_hit_rate=cap_hit_rate,

        birth_death_ratio=birth_death_ratio,

        mean_time_cv_over_runs = mean_time_cv_over_runs
    )
    



if __name__ == "__main__":
    pass