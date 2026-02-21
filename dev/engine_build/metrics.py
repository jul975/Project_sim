import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engineP4 import Engine



""" lightweight matrix collection module, main goal is to set it up without polluting the engine

    should collect agent data and lifecycle matrics only using public engine data. 

    implementations steps should be watched, regulated in order to avoid breaking determenism.
"""


""" 
    NOTE: right now, clear separation between engine sate and mesurements.

            S(t) | M(t) 

"""
class SimulationMetrics:
    def __init__(self) -> None:


        # lightweight first metrics
        self.population : list[np.int64] = []
        self.mean_energy : list[np.float64] = []
        self.births : list[np.float64] = []
        self.deaths : list[np.float64] = []


    def record(self, engine : "Engine", births_this_tick : np.int64 = 0, deaths_this_tick : np.int64 = 0) -> None:
        """ records metrics for a given engine state. """
        """ NOTE: 
                -   as of now I'm using 4 lists to store the metrics, need to make sure that no ticks are missed. 
                    => should be ok as is, as the recording is done after the tick is completed.
                    => but keep in mind  
        """
        agents = engine.agents.values()
        agent_count = len(agents)

        self.population.append(agent_count)

        if agent_count > 0:
            # check efficiency, compared to standard python sum / len
            self.mean_energy.append(np.mean([agent.energy_level for agent in agents]))
        else:
            # 
            self.mean_energy.append(0.0)
        
        self.births.append(births_this_tick)
        self.deaths.append(deaths_this_tick)


    



