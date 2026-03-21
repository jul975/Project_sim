"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""

from dataclasses import dataclass
from typing import Dict

from engine_build.runner.regime_runner import BatchRunResults


from engine_build.analytics.fingerprint import get_fingerprints, get_aggregate_fingerprints
from engine_build.analytics.performance import aggregate_phase_profile


from engine_build.analytics.fingerprint import AggregatedFingerprint, Fingerprint
import numpy as np

from engine_build.analytics.performance import BatchPhaseProfile


from engine_build.analytics.world_frames_analytics import analyze_batch_world_frames , BatchWorldFrameAnalysis






@dataclass(frozen=True)
class BatchMetadata:
    batch_id: int
    ticks: int
    tail_start: int
    batch_duration: float | None
    max_agent_count: int

@dataclass(frozen=True)
class AnalysisConfig:
    tail_fraction: float = 0.25
    include_perf: bool = False
    include_world_frames: bool = False

    # temp value, 
    regime_label: str | None = None


def build_batch_metadata(batch_results : BatchRunResults, analysis_config : AnalysisConfig) -> BatchMetadata:
    """ build batch metadata. """

    if batch_results.batch_id is None:
        raise ValueError("batch_results.batch_id is None")
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    if batch_results.batch_duration is None:
        raise ValueError("batch_results.batch_duration is None")
    
    tail_start = resolve_tail_start(batch_results.ticks, analysis_config.tail_fraction)
    return BatchMetadata(
        batch_id=batch_results.batch_id,
        ticks=batch_results.ticks,
        tail_start=tail_start,
        batch_duration=batch_results.batch_duration,
        max_agent_count=batch_results.max_agent_count,

    )




# derived experiment interpretation 
@dataclass
class BatchAnalysis:
    batch_metadata : BatchMetadata

    aggregate_fingerprint : AggregatedFingerprint
    run_fingerprints : Dict[np.int64, Fingerprint]
    
    batch_phase_profile : BatchPhaseProfile | None = None
    batch_world_frames : BatchWorldFrameAnalysis | None = None
    regime_label : str | None = None



def resolve_tail_start(total_tics: int, tail_fraction = 0.25) -> int:
    """ resolve tail start. """
    return int(total_tics * (1.0 - tail_fraction))



def analyze_batch(batch_results : BatchRunResults, analysis_config : AnalysisConfig) -> BatchAnalysis:
    """ analyze a batch of runs. """

    if batch_results.regime_config is None:
        raise ValueError("batch_results.regime_config is None")
    
    metadata = build_batch_metadata(batch_results, analysis_config)



    run_fingerprints = get_fingerprints(batch_results.runs, metadata.tail_start)
    aggregate_fingerprint = get_aggregate_fingerprints(list(run_fingerprints.values()))


    
    if analysis_config.include_perf:
        batch_phase_profile = aggregate_phase_profile(batch_results.runs, metadata.batch_duration)
    else:
        batch_phase_profile = None


    
    if analysis_config.include_world_frames:
        batch_world_frames = analyze_batch_world_frames(batch_results.runs)
    else:
        batch_world_frames = None    



    return BatchAnalysis(
        batch_metadata = metadata,
        aggregate_fingerprint = aggregate_fingerprint,
        
        run_fingerprints = run_fingerprints,
        batch_phase_profile = batch_phase_profile,
        
        batch_world_frames = batch_world_frames,
        #
        regime_label = analysis_config.regime_label
    )
    



    """
    fingerprints_dict = {}
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    # change to last 25% of run later on 
    tail_start = int(batch_results.ticks * 0.75)

    if perf_flag:
        batch_phase_profile = BatchPhaseProfile()
    
    aggregate_fingerprint = None
    batch_duration = batch_results.batch_duration
    


    for i, run_results in batch_results.runs.items():

        if run_results.metrics is None:
            raise ValueError(f"run_results.metrics is None for run {i}")
        fingerprints_dict[i] = compute_fingerprint(run_results.metrics, tail_start)


        aggregate_fingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))









    if batch_phase_profile is not None:
        if batch_duration is None or batch_duration <= 0:
            raise ValueError("batch_results.batch_duration must be positive when perf_flag=True")
        batch_phase_profile.movement_ratio = batch_phase_profile.movement / batch_duration
        batch_phase_profile.interaction_ratio = batch_phase_profile.interaction / batch_duration
        batch_phase_profile.biology_ratio = batch_phase_profile.biology / batch_duration
        batch_phase_profile.commit_ratio = batch_phase_profile.commit / batch_duration
        



    """
    
