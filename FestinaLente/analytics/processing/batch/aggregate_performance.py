
from dataclasses import dataclass

from FestinaLente.analytics.processing.process_run import ProcessedRun
from FestinaLente.analytics.processing.processing_containers.batch_containers import BatchPhaseProfile
from FestinaLente.runner.utils.results import RunArtifacts
from typing import Dict
import numpy as np

def aggregate_phase_profile(batch_runs : list[ProcessedRun], batch_duration : float) -> BatchPhaseProfile:
    """ aggregate phase profile over a batch of runs. """
    

    if batch_duration is None or batch_duration <= 0:
        raise ValueError("batch_duration must be positive when perf_flag=True")
    
    batch_phase_profile = BatchPhaseProfile()

    # sum up phase profile
    for run_results in batch_runs:
        if run_results.run_profile is None:
            raise ValueError("run_results.phase_profile is None")
        batch_phase_profile.movement += run_results.run_profile.movement_time
        batch_phase_profile.interaction += run_results.run_profile.interaction_time
        batch_phase_profile.biology += run_results.run_profile.biology_time
        batch_phase_profile.commit += run_results.run_profile.commit_time

        batch_phase_profile.commit_setup += run_results.run_profile.commit_setup_time
        batch_phase_profile.commit_deaths += run_results.run_profile.commit_deaths_time
        batch_phase_profile.commit_births += run_results.run_profile.commit_births_time
        batch_phase_profile.commit_resource_regrowth += run_results.run_profile.commit_resource_regrowth_time


    # compute ratios
    batch_phase_profile.movement_ratio = batch_phase_profile.movement / batch_duration
    batch_phase_profile.interaction_ratio = batch_phase_profile.interaction / batch_duration
    batch_phase_profile.biology_ratio = batch_phase_profile.biology / batch_duration
    batch_phase_profile.commit_ratio = batch_phase_profile.commit / batch_duration

    return batch_phase_profile



    
if __name__ == "__main__":
    pass