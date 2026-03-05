


from engine_build.analytics.fingerprint import compute_fingerprint, get_aggregate_fingerprints, AggregatedFingerprint, Fingerprint
from engine_build.core.engineP4 import Engine
from engine_build.execution.default import DEFAULT_MASTER_SEED


from engine_build.core.config import SimulationConfig
from engine_build.metrics.metrics import SimulationMetrics
import numpy as np
from dataclasses import dataclass
from typing import Dict

"""
CAVE:
        No math.
        No policy.
        No regime logic.
        No state.
        Just orchestration.


        input: config, seeds, ticks
        output: structured result object

        (master_seed)
              ↓
        SeedSequence
            ↓ spawn(n)
        ┌────┬────┬────┬────┬────┐
        SS0  SS1  SS2  SS3  SS4
        └────┴────┴────┴────┴────┘
            ↓     ↓     ↓     ↓
        run  run  run  run  run

        on engine level we have:
            SS2
              ↓ spawn(...)
            world_ss
            move_ss
            repro_ss
            energy_ss


"""

 

@dataclass
class RegimeBatchResults:
    aggregate_fingerprint : AggregatedFingerprint
    fingerprints_dict : Dict[np.int64, Fingerprint]
    batch_metrics : Dict[np.int64, SimulationMetrics]






def generate_run_sequences(master_seed: int, n_runs: int) -> list[np.random.SeedSequence]:
    """ I do NOT return master seed, state mutation must be avoided, 
        therefore the master seed is used only to generate the run seeds.
        And NEVER touched again 
    
    """
    ss = np.random.SeedSequence(master_seed)
    return ss.spawn(n_runs)


class BatchRunner:
    def __init__(
            self, 
            regime_config : SimulationConfig , 
            n_runs : int, 
            ticks : np.int64 ,
            batch_id : int| None = None
            ) -> None:
        """ set up batch run with master seed == batch_id. 
            will set up run seeds internally at initialization.
         """
        
        self.regime_config = regime_config
        self.n_runs = n_runs
        self.ticks = ticks
        self.batch_id = batch_id if batch_id is not None else DEFAULT_MASTER_SEED

        self.run_seeds = generate_run_sequences(self.batch_id , n_runs)

    def run_single(self, seed : np.random.SeedSequence, ticks : np.int64) -> tuple[Engine, SimulationMetrics]:
    
        eng = Engine(seed, self.regime_config)
        metrics = SimulationMetrics()
        for _ in range(ticks):
            births_this_tick, deaths_this_tick, pending_death = eng.step()
            metrics.record(eng, births_this_tick, deaths_this_tick, pending_death)

        return eng, metrics
    
    def _continue_run(self, eng : Engine, metrics : SimulationMetrics, ticks : np.int64) -> tuple[Engine, SimulationMetrics]:
        for _ in range(ticks):
            births_this_tick, deaths_this_tick, pending_death = eng.step()
            metrics.record(eng, births_this_tick, deaths_this_tick, pending_death)
        return eng, metrics



    def run_regime_batch(self) -> RegimeBatchResults:
        """ only return aggregates and results."""

        fingerprints_dict = {}
        batch_metrics = {}

        for i, seed in enumerate(self.run_seeds):
            _, metrics = self.run_single(seed, self.ticks)




            batch_metrics[i] = metrics            

            tail_start = self.ticks // 4 # NOTE: tail start is hardcoded for now. simple to get working tests for now, will be configurable later.

            fingerprint = compute_fingerprint(metrics, tail_start)
            fingerprints_dict[i] = fingerprint
            
        
        aggregate_fingerprint : AggregatedFingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))
        
        return RegimeBatchResults(aggregate_fingerprint, fingerprints_dict, batch_metrics)



if __name__ == "__main__":
    pass

