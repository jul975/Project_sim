"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""

from engine_build.analytics.contracts.config import AnalysisConfig
from engine_build.analytics.contracts.metadata import build_batch_metadata
from engine_build.analytics.contracts.batch_analysis import BatchAnalysis

from engine_build.runner.batch_runner import BatchRunResults


from engine_build.analytics.run_level.fingerprint import get_fingerprints, get_aggregate_fingerprints
from engine_build.analytics.performance.performance import aggregate_phase_profile





from engine_build.analytics.world_frames_analytics import analyze_batch_world_frames , BatchWorldFrameAnalysis




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
        batch_world_frames = analyze_batch_world_frames(batch_results.runs, metadata.max_resource_level)
    else:
        batch_world_frames = None    



    return BatchAnalysis(
        batch_metadata = metadata,
        aggregate_fingerprint = aggregate_fingerprint,
        all_runs = batch_results.runs,
        
        run_fingerprints = run_fingerprints,
        batch_phase_profile = batch_phase_profile,
        
        batch_world_frames = batch_world_frames,
        #
        regime_label = analysis_config.regime_label
    )
    



