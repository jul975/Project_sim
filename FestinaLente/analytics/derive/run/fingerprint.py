
import numpy as np
from FestinaLente.analytics.observation.simulation_metrics import SimulationMetrics
from dataclasses import dataclass


from FestinaLente.runner.results import RunArtifacts
from typing import Dict
from analytics.derive.run.run_container import Fingerprint

"""
Fingerprint

AggregatedFingerprint

compute_fingerprint

aggregate_fingerprints

"""




def compute_fingerprint( metrics : SimulationMetrics, tail_start : np.int64)-> Fingerprint:
    """ compute tail-window fingerprint of a single simulation run. """
    """if tail_start <= 0 or tail_start >= len(metrics.population):
        raise ValueError(f"tail_start {tail_start} out of bounds for metrics of length {len(metrics.population)}")"""

    population_tail = np.asarray(metrics.population[tail_start:], dtype=float)
    births_tail = np.asarray(metrics.births[tail_start:], dtype=float)
    deaths_tail = np.asarray(metrics.deaths[tail_start:], dtype=float)
    
    total_deaths_tail = int(np.sum(deaths_tail))


    # note what about extinction and early termination? 
    final_population = int(population_tail[-1])
    min_tail = int(np.min(population_tail))
    max_tail = int(np.max(population_tail))
    mean_tail = float(np.mean(population_tail))
    std_tail = float(np.std(population_tail))
    range_tail = float(max_tail - min_tail)
    cap_hit_rate = float((np.asarray(population_tail) == metrics.max_agent_count).mean())
    mean_deaths_per_tick = float(np.mean(deaths_tail))
    mean_births_per_tick = float(np.mean(births_tail))
    
    extinction_tick = next((i + tail_start for i, pop in enumerate(population_tail) if pop == 0), None)
    
    
    
    

    mean_deaths_cause_tail = {
        cause : float(np.mean(death_causes[tail_start:]))
        for cause, death_causes in metrics.death_causes.items()}
    
    if total_deaths_tail > 0:
        proportion_deaths_cause_tail = {
            cause: float(np.sum(death_causes[tail_start:]) / total_deaths_tail)
            for cause, death_causes in metrics.death_causes.items()
    }
    else:
        proportion_deaths_cause_tail = {
            cause: 0.0
            for cause in metrics.death_causes
    }
        
    near_cap_rate = float((np.asarray(population_tail) >= 0.9 * metrics.max_agent_count).mean())
    low_population_rate = float((np.asarray(population_tail) <= 0.1 * metrics.max_agent_count).mean())



    return Fingerprint(

        # population at end of run? 
        final_population=final_population,
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
        proportion_deaths_cause_tail=proportion_deaths_cause_tail,

        near_cap_rate=near_cap_rate,
        low_population_rate=low_population_rate,
        
    )



def get_fingerprints(batch_runs : Dict[np.int64, RunArtifacts], tail_start : int):
    """ get fingerprints for a batch of runs. """
    """if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")"""
    
    if tail_start <= 0:
        raise ValueError(f"tail_start {tail_start} must be positive")

    fingerprints = {}
    
    for i, run_results in batch_runs.items():
        if run_results.metrics is None:
            raise ValueError(f"run_results.metrics is None for run {i}")
        fingerprints[i] = compute_fingerprint(run_results.metrics, tail_start)
    return fingerprints


if __name__ == "__main__":
    pass