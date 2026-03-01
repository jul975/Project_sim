


from engine_build.analytics.fingerprint import compute_fingerprint, aggregate_fingerprints
from engine_build.core.engineP4 import Engine

from engine_build.core.config import SimulationConfig
from engine_build.metrics.metrics import SimulationMetrics
import numpy as np

"""
CAVE:
        No math.
        No policy.
        No regime logic.
        No state.
        Just orchestration.


        input: config, seeds, ticks
        output: structured result object

"""
# regime: str = "stable"
# seeds = [42, 1234, 5678, 91011, 121314]
# ticks = 1000

def run_regime_batch(regime_config : SimulationConfig, seeds : list[np.int64], ticks : np.int64) -> tuple[dict, dict]:
    """ only return aggregates and results."""

    
# cave regime_config has a,b, g preset. logic here is only running the regime not setting it up 
# regime_config comes preset from experiments module, (for now)
        


    
    fingerprints_dict = {}

    for seed in seeds:

        eng = Engine(seed, regime_config)
        metrics = SimulationMetrics()
        for _ in range(ticks):
            births_this_tick, deaths_this_tick, pending_death = eng.step()
            metrics.record(eng, births_this_tick, deaths_this_tick, pending_death)

            
        # NOTE: tail start is hardcoded for now. simple to get working tests for now, 
        tail_start = ticks // 4

        fingerprint = compute_fingerprint(metrics, tail_start)
        fingerprints_dict[seed] = fingerprint
        
    
    aggregate_fingerprint = aggregate_fingerprints(fingerprints_dict.values())

    return aggregate_fingerprint, fingerprints_dict



def main():
    


    regime, aggregate_fingerprint, fingerprints_dict = run_regime_batch("stable")
    print("================================================================")
    print(f"Regime: {regime}")
    print(f"Aggregate Fingerprint: ")
    for k, v in aggregate_fingerprint.items():
        print(f"    {k}: {v}")

    print("================================================================")
    print(f"Individual Fingerprints: ")
    for seed, fingerprint in fingerprints_dict.items():
        print(f"    Seed: {seed}")
        for k, v in fingerprint.items():
            print(f"        {k}: {v}")
        print("----------------------------------------------------------------")
    
    

if __name__ == "__main__":
    main()

