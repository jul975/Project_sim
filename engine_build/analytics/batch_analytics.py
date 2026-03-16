"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""

from dataclasses import dataclass
from typing import Dict

from engine_build.runner.regime_runner import BatchRunResults


from engine_build.analytics.fingerprint import compute_fingerprint, get_aggregate_fingerprints


from engine_build.analytics.fingerprint import AggregatedFingerprint, Fingerprint
from engine_build.runner.regime_runner import RunArtifacts
import numpy as np




@dataclass
class BatchPhaseProfile:
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0

    commit_setup: float = 0.0
    commit_deaths: float = 0.0
    commit_births: float = 0.0
    commit_resource_regrowth: float = 0.0

    movement_ratio: float = 0.0
    interaction_ratio: float = 0.0
    biology_ratio: float = 0.0
    commit_ratio: float = 0.0







# derived experiment interpretation 
@dataclass
class BatchAnalysis:
    aggregate_fingerprint : AggregatedFingerprint
    fingerprints_dict : Dict[np.int64, Fingerprint]
    batch_metrics : Dict[np.int64, RunArtifacts]
    regime_label : str | None = None
    summary_stats : Dict[str, float] | None = None
    ticks : np.int64 | None = None
    batch_id : int | None = None
    tail_start : np.int64 | None = None
    batch_duration : float | None = None

    batch_phase_profile : BatchPhaseProfile | None = None




def analyze_batch(batch_results : BatchRunResults, regime_label : str | None = None, perf_flag : bool = False) -> BatchAnalysis:
    """ analyze a batch of runs. """
    fingerprints_dict = {}
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    # change to last 25% of run later on 
    tail_start = int(batch_results.ticks * 0.75)

    if perf_flag:
        batch_phase_profile = BatchPhaseProfile()
    else:
        batch_phase_profile = None
    
    for i, run_results in batch_results.runs.items():
        if run_results.metrics is None:
            raise ValueError(f"run_results.metrics is None for run {i}")
        fingerprints_dict[i] = compute_fingerprint(run_results.metrics, tail_start)
        if batch_phase_profile is not None:
            for run_results in batch_results.runs.values():
                
                batch_phase_profile.movement += run_results.phase_profile.movement
                batch_phase_profile.interaction += run_results.phase_profile.interaction
                batch_phase_profile.biology += run_results.phase_profile.biology
                batch_phase_profile.commit += run_results.phase_profile.commit

                batch_phase_profile.commit_setup += run_results.phase_profile.commit_setup
                batch_phase_profile.commit_deaths += run_results.phase_profile.commit_deaths
                batch_phase_profile.commit_births += run_results.phase_profile.commit_births
                batch_phase_profile.commit_resource_regrowth += run_results.phase_profile.commit_resource_regrowth

        aggregate_fingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))
        batch_duration = batch_results.batch_duration








    if batch_phase_profile is not None:
        batch_phase_profile.movement_ratio = batch_phase_profile.movement / batch_duration
        batch_phase_profile.interaction_ratio = batch_phase_profile.interaction / batch_duration
        batch_phase_profile.biology_ratio = batch_phase_profile.biology / batch_duration
        batch_phase_profile.commit_ratio = batch_phase_profile.commit / batch_duration
        



    



    return BatchAnalysis(
        aggregate_fingerprint=aggregate_fingerprint,
        fingerprints_dict=fingerprints_dict,
        batch_metrics=batch_results.runs,
        regime_label=regime_label,
        ticks=batch_results.ticks,
        batch_id=batch_results.batch_id,
        tail_start=tail_start,
        batch_duration=batch_duration,
        batch_phase_profile=batch_phase_profile
    )
    
