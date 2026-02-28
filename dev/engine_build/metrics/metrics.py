import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine_build.core.engineP4 import Engine
    from engine_build.core.config import DeathBucket
    from engine_build.core.config import SimulationConfig



""" lightweight matrix collection module, main goal is to set it up without polluting the engine

    should collect agent data and lifecycle matrics only using public engine data. 

    implementations steps should be watched, regulated in order to avoid breaking determenism.
"""


""" 
    NOTE: right now, clear separation between engine sate and mesurements.

            S(t) | M(t) 

"""

""" TEST METRICS SETUP: V0.1

        -   Head (tick 0 -> n)

        -   Tail (tick n denoting start tail-window)

        
        For tail window, collect: 
        Population metrics:
        -   min, max, mean population
        -   std/range population
        -   cap_hit_rate

        -   extinction_tick : None | tick_n
        -   mean deaths/tick
        -   mean births/tick

        -   mean age ?
        -   mean reproduction rate ?
        -   mean harvest rate ?
        -   mean movement rate ?

        -   mean(deaths_cause_tail)
        -   proportion: deaths_cause_tail_sum / total_deaths_tail_sum

        
        World metrics:
        1. total resources
        2. mean resources
        3. depletion fraction vs fertility



"""





class SimulationMetrics:
    def __init__(self) -> None:


        # lightweight first metrics
        # max count needed upstream, will setup on first record. 
        self.max_agent_count : np.int64 | None = None
        self.population : list[np.int64] = []
        self.mean_energy : list[np.float64] = []
        self.births : list[np.float64] = []
        self.deaths : list[np.float64] = []
        self.death_causes : dict[str, list[np.int64]] = {
            "old_age" : [],
            "metabolic_starvation" : [],
            "post_harvest_starvation" : [],
            "post_reproduction_death" : []
        }


    def record(self, engine : "Engine", births_this_tick : np.int64 = 0, deaths_this_tick : np.int64 = 0, pending_death : dict[str, 'DeathBucket'] | None = None) -> None:
        """ records metrics for a given engine state. """
        """ NOTE: 
                -   as of now I'm using 4 lists to store the metrics, need to make sure that no ticks are missed. 
                    => should be ok as is, as the recording is done after the tick is completed.
                    => but keep in mind  
        """
        if self.max_agent_count is None:
            self.max_agent_count = engine.config.population_config.max_agent_count
        agents = engine.agents.values()
        agent_count = len(agents)

        self.population.append(agent_count)

        if agent_count > 0:
            # check efficiency, compared to standard python sum / len
            self.mean_energy.append((sum(agent.energy_level for agent in agents) / agent_count) if agent_count > 0 else 0.0)
        else:
            # 
            self.mean_energy.append(0.0)
        
        self.births.append(births_this_tick)
        self.deaths.append(deaths_this_tick)

        
        for cause, bucket in pending_death.items():
            self.death_causes[cause].append(bucket.count)


def compute_fingerprint(metrics : SimulationMetrics, tail_start : np.int64)-> dict:

    population_tail = metrics.population[tail_start:]
    births_tail = metrics.births[tail_start:]
    deaths_tail = metrics.deaths[tail_start:]
    

    min_tail = min(population_tail)
    max_tail = max(population_tail)
    mean_tail = np.mean(population_tail)
    std_tail = np.std(population_tail)
    range_tail = max_tail - min_tail
    cap_hit_rate = np.array(population_tail == metrics.max_agent_count).mean()
    
    # NOTE: review next() => usefull and didnt think about it for a while. => generator so no list construction
    extinction_tick = next((i for i, pop in enumerate(population_tail) if pop == 0), None)
    mean_deaths_per_tick = np.mean(deaths_tail)
    mean_births_per_tick = np.mean(births_tail)
    
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
    mean_pop_over_runs = np.mean([f["mean_population"] for f in fingerprints])
    std_pop_over_runs = np.std([f["mean_population"] for f in fingerprints])
    # note, conditional 0, do not simplify will potential mess stat
    extinction_rate = np.mean([f["extinction_tick"] if f["extinction_tick"] is not None else 0 for f in fingerprints])

    return {
        "mean_population" : mean_pop_over_runs,
        "std_population" : std_pop_over_runs,
        "extinction_rate" : extinction_rate
    }
    