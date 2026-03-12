

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



import numpy as np

from engine_build.core.engineP4 import Engine
from engine_build.core.step_results import StepReport


class SimulationMetrics:
    def __init__(self, eng : Engine) -> None:
        
        
        self.max_agent_count : int = eng.max_agent_count
        self.max_age : int = eng.max_age

        self.population: list[int] = []
        self.mean_energy: list[float] = []
        self.births: list[int] = []
        self.deaths: list[int] = []

        self.death_causes: dict[str, list[int]] = {
            "age_deaths": [],
            "metabolic_deaths": [],
            "post_harvest_starvation": [],
            "post_reproduction_death": [],
        }

        # optional later
        #self.resources_mean: list[float] = []
        #self.occupancy_metrics: list[dict[str, float]] = []

    def record(self, step_report: StepReport) -> None:
        """ records metrics for a given engine state and step report. """

        

        energies = step_report.world_view.energies

        self.population.append(int(step_report.commit_report.population))
        self.mean_energy.append(float(np.mean(energies)) if energies.size else 0.0)

        births = int(step_report.commit_report.births_count)
        deaths = int(step_report.commit_report.deaths_count)

        self.births.append(births)
        self.deaths.append(deaths)

        age_deaths = int(step_report.movement_report.age_deaths_count)
        metabolic_deaths = int(step_report.movement_report.metabolic_deaths_count)
        post_harvest_starvation = int(step_report.interaction_report.pending_starvation_death_count)
        post_reproduction_death = int(step_report.biology_report.post_reproduction_death_count)

        self.death_causes["age_deaths"].append(age_deaths)
        self.death_causes["metabolic_deaths"].append(metabolic_deaths)
        self.death_causes["post_harvest_starvation"].append(post_harvest_starvation)
        self.death_causes["post_reproduction_death"].append(post_reproduction_death)
        """
        resources = step_report.world_view.resources
        self.resources_mean.append(float(np.mean(resources)))
        self.occupancy_metrics.append({
            "occupied_cells" : len(step_report.world_view.positions),
            "mean_occupancy" : float(np.mean(step_report.world_view.energies)),
            "max_occupancy" : float(np.max(step_report.world_view.energies)),
            "ratio_t" : float(np.max(step_report) / np.mean()),
        })
        """

        if __debug__:
            cause_total = (
                age_deaths
                + metabolic_deaths
                + post_harvest_starvation
                + post_reproduction_death
            )
            assert cause_total == deaths, (
                f"Death cause mismatch: causes={cause_total}, committed={deaths}"
            )
            

if __name__ == "__main__":
    pass