

import numpy as np

""" lightweight matrix collection module, main goal is to set it up without polluting the engine

    should collect agent data and lifecycle matrics only using public engine data. 

    implementations steps should be watched, regulated in order to avoid breaking determenism.
"""
class SimulationMetrics:
    def __init__(self) -> None:


        # lightweight first metrics
        self.population : list[np.int64] = []
        self.mean_energy : list[np.float64] = []
        self.births : list[np.float64] = []
        self.deaths : list[np.float64] = []




