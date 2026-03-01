
import numpy as np
from engine_build.metrics.metrics import SimulationMetrics


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





def compute_fingerprint(metrics : SimulationMetrics, tail_start : np.int64)-> dict:

    population_tail = metrics.population[tail_start:]
    births_tail = metrics.births[tail_start:]
    deaths_tail = metrics.deaths[tail_start:]
    
    # 1) population metrics
    min_tail = min(population_tail)
    max_tail = max(population_tail)
    mean_tail = np.mean(population_tail)
    std_tail = np.std(population_tail)
    range_tail = max_tail - min_tail
    cap_hit_rate = np.array(population_tail == metrics.max_agent_count).mean()
    
    # NOTE: review next() => usefull and didnt think about it for a while. => generator so no list construction
    
    # 2) extinction tick
    extinction_tick = next((i for i, pop in enumerate(population_tail) if pop == 0), None)
    
    
    # 3) mean deaths and births per tick
    mean_deaths_per_tick = np.mean(deaths_tail)
    mean_births_per_tick = np.mean(births_tail)
    
    # 4) mean and proportion of deaths cause
    mean_deaths_cause_tail = {cause : np.mean(death_causes) for cause, death_causes in metrics.death_causes.items()}
    proportion_deaths_cause_tail = {cause : np.sum(death_causes) / np.sum(deaths_tail) for cause, death_causes in metrics.death_causes.items()}

    fingerprint = {
        "min_population" : min_tail,
        "max_population" : max_tail,
        "mean_population" : mean_tail,
        "std_population" : std_tail,
        "range_population" : range_tail,
        "cap_hit_rate" : cap_hit_rate,
        "extinction_tick" : extinction_tick,
        "mean_deaths_per_tick" : mean_deaths_per_tick,
        "mean_births_per_tick" : mean_births_per_tick,
        "mean_deaths_cause_tail" : mean_deaths_cause_tail,
        "proportion_deaths_cause_tail" : proportion_deaths_cause_tail
    }
    return fingerprint


def aggregate_fingerprints(fingerprints : list[dict]) -> dict:


    # 1) simple mean and std aggregation
    mean_pop_over_runs = np.mean([f["mean_population"] for f in fingerprints])
    std_pop_over_runs = np.std([f["mean_population"] for f in fingerprints])



    # 2) extinction rate
    # note, conditional 0, do not simplify will potential mess stats
    extinction_rate = np.mean([f["extinction_tick"] if f["extinction_tick"] is not None else 0 for f in fingerprints])

    return {
        "mean_population" : mean_pop_over_runs,
        "std_population" : std_pop_over_runs,
        "extinction_rate" : extinction_rate
    }
    



if __name__ == "__main__":
    pass