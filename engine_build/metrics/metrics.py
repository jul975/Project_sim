import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine_build.core.engineP4 import Engine
    from engine_build.core.config import DeathBucket
    from engine_build.core.config import SimulationConfig


"""
NOTE: 
        Observation only

            - MetricsCollector
            - Death counters
            - Population history
            - Tick-level logging

It receives state snapshots or event hooks.
It does not run loops.
It does not know about regimes.




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
        self.occupancy_metrics : list[dict[str, np.float64]] = []
        self.death_causes : dict[str, list[np.int64]] = {
            "old_age" : [],
            "metabolic_starvation" : [],
            "post_harvest_starvation" : [],
            "post_reproduction_death" : []
        }

    # NOTE: introduce step container to containerize metrics for each step, not now but soon
    def record(self, 
               engine : "Engine", 
               births_this_tick : np.int64 = 0, 
               deaths_this_tick : np.int64 = 0, 
               pending_death : dict[str, 'DeathBucket'] | None = None,
               occupancy_metrics : dict[str, np.float64] | None = None) -> None:
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
        
        self.occupancy_metrics.append(occupancy_metrics)
        





if __name__ == "__main__":
    pass