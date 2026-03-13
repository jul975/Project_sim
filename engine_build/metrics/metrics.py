

"""
NOTE: 
        Observation only
    It receives step reports (later maybe or event hooks.)
    It does NOT run loops.
    It does NOT know about regimes.

"""


""" 
    NOTE: right now, clear separation between engine sate and metrics.

            S(t) | M(t) 

"""

""" TEST METRICS SETUP: V0.1

    - max_agent_count
    - population
    - mean_energy
    - births
    - deaths
    - death_causes

"""



import numpy as np
from engine_build.core.step_results import StepReport


class SimulationMetrics:
    def __init__(self, max_agent_count : int ) -> None:
        """Stores canonical per-tick observed signals for one simulation run."""
        
        self.max_agent_count : int = max_agent_count
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



    def record(self, step_report: StepReport) -> None:
        """Stores per-tick observed signals for one simulation run."""

        
        # population
        self.population.append(int(step_report.commit_report.population))

        # energies
        energies = step_report.world_view.energies
        mean_energy = float(np.mean(energies)) if energies.size else 0.0 
        self.mean_energy.append(mean_energy)


        # births and deaths
        births = int(step_report.commit_report.births_count)
        deaths = int(step_report.commit_report.deaths_count)

        self.births.append(births)
        self.deaths.append(deaths)


        # death causes
        age_deaths = int(step_report.movement_report.age_deaths_count)
        metabolic_deaths = int(step_report.movement_report.metabolic_deaths_count)
        post_harvest_starvation = int(step_report.interaction_report.pending_starvation_death_count)
        post_reproduction_death = int(step_report.biology_report.post_reproduction_death_count)

        self.death_causes["age_deaths"].append(age_deaths)
        self.death_causes["metabolic_deaths"].append(metabolic_deaths)
        self.death_causes["post_harvest_starvation"].append(post_harvest_starvation)
        self.death_causes["post_reproduction_death"].append(post_reproduction_death)


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