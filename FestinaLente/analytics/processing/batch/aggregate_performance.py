
from dataclasses import dataclass

from FestinaLente.analytics.processing.processing_containers.batch_containers import BatchPhaseProfile
from FestinaLente.runner.utils.results import RunArtifacts
from typing import Dict
import numpy as np

def aggregate_phase_profile(batch_runs : Dict[np.int64, RunArtifacts], batch_duration : float) -> BatchPhaseProfile:
    """ aggregate phase profile over a batch of runs. """
    

    if batch_duration is None or batch_duration <= 0:
        raise ValueError("batch_duration must be positive when perf_flag=True")
    
    batch_phase_profile = BatchPhaseProfile()

    # sum up phase profile
    for run_results in batch_runs.values():
        if run_results.phase_profile is None:
            raise ValueError("run_results.phase_profile is None")
        batch_phase_profile.movement += run_results.phase_profile.movement
        batch_phase_profile.interaction += run_results.phase_profile.interaction
        batch_phase_profile.biology += run_results.phase_profile.biology
        batch_phase_profile.commit += run_results.phase_profile.commit

        batch_phase_profile.commit_setup += run_results.phase_profile.commit_setup
        batch_phase_profile.commit_deaths += run_results.phase_profile.commit_deaths
        batch_phase_profile.commit_births += run_results.phase_profile.commit_births
        batch_phase_profile.commit_resource_regrowth += run_results.phase_profile.commit_resource_regrowth


    # compute ratios
    batch_phase_profile.movement_ratio = batch_phase_profile.movement / batch_duration
    batch_phase_profile.interaction_ratio = batch_phase_profile.interaction / batch_duration
    batch_phase_profile.biology_ratio = batch_phase_profile.biology / batch_duration
    batch_phase_profile.commit_ratio = batch_phase_profile.commit / batch_duration

    return batch_phase_profile



    
if __name__ == "__main__":
    pass