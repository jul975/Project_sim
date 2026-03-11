


from engine_build.analytics.fingerprint import compute_fingerprint, get_aggregate_fingerprints, AggregatedFingerprint, Fingerprint
from engine_build.core.engineP4 import Engine
from engine_build.execution.default import DEFAULT_MASTER_SEED
from engine_build.core.step_results import StepMetrics


from engine_build.regimes.compiled import CompiledRegime

from engine_build.metrics.metrics import SimulationMetrics
import numpy as np
from dataclasses import dataclass
from typing import Dict
from engine_build.metrics.world_frames import WorldFrames


"""
    'the runner should own orchestration and lifecycle, not interpretation.'
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


 
# raw one run results
@dataclass
class RunArtifacts:
    engine_final : Engine | None = None
    metrics : SimulationMetrics | None = None
    world_frames : WorldFrames | None = None
    seed : np.random.SeedSequence | None = None
    ticks : np.int64 | None = None

# raw batch results
@dataclass
class BatchRunResults:
    runs : Dict[np.int64, RunArtifacts]
    batch_id : int | None = None
    regime_config : CompiledRegime | None = None



def generate_run_sequences(master_seed: int, n_runs: int) -> list[np.random.SeedSequence]:
    """ I do NOT return master seed, state mutation must be avoided, 
        therefore the master seed is used only to generate the run seeds.
        And NEVER touched again 
    """
    ss = np.random.SeedSequence(master_seed)
    return ss.spawn(n_runs)


class Runner:
    def __init__(
            self, 
            regime_config : CompiledRegime , 
            n_runs : int, 
            
            batch_id : int| None = None
            ) -> None:
        """ set up batch run with master seed == batch_id. 
            will set up run seeds internally at initialization.
         """
        
        self.regime_config = regime_config
        self.n_runs = n_runs
        self.batch_id = batch_id if batch_id is not None else DEFAULT_MASTER_SEED

        self.run_seeds = generate_run_sequences(self.batch_id , n_runs)


#############################################################
    def run_single(self, seed : np.random.SeedSequence, ticks : np.int64) -> RunArtifacts:
        """ runs a single simulation for a given seed and ticks. """
    
        eng = Engine(seed, self.regime_config)
        # NOTE: 

        metrics = SimulationMetrics()

        world_frames = WorldFrames( capture_every=10 if ticks > 100 else 1)

        for tick in range(ticks):
            
            step_metrics : StepMetrics = eng.step()
            metrics.record(eng, step_metrics)

            if tick % world_frames.capture_every == 0:
                world_frames.capture(eng)

        return RunArtifacts(eng, metrics, world_frames, seed, ticks)
    


#############################################################
    def _continue_run(self, eng : Engine, metrics : SimulationMetrics, ticks : np.int64) -> RunArtifacts:
        for _ in range(ticks):
            step_metrics : StepMetrics = eng.step()
            metrics.record(eng, step_metrics)
        return RunArtifacts(eng, metrics, None, eng.master_ss, ticks)



#############################################################
    def run_regime_batch(self, ticks : np.int64) -> BatchRunResults:
        """ only return aggregates and results."""

        batch_data: BatchRunResults = BatchRunResults({}, self.batch_id, self.regime_config)

        for i, seed in enumerate(self.run_seeds):
            run_results : RunArtifacts = self.run_single(seed, ticks)
            batch_data.runs[i] = run_results    
        return batch_data



if __name__ == "__main__":
    pass



"""

            tail_start = ticks // 4 # NOTE: tail start is hardcoded for now. simple to get working tests for now, will be configurable later.

            fingerprint = compute_fingerprint(run_results.metrics, tail_start)
            fingerprints_dict[i] = fingerprint
            
        
        aggregate_fingerprint : AggregatedFingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))"""
