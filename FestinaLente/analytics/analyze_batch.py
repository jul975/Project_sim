"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""
from FestinaLente.analytics.contracts.metadata import BatchMetadata, build_batch_metadata
from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.batch_runner import BatchRunResults
from FestinaLente.analytics.derive.run.fingerprint import get_fingerprints
from FestinaLente.analytics.derive.batch.aggregate_fingerprint import get_aggregate_fingerprints
from FestinaLente.analytics.derive.batch.aggregate_performance import aggregate_phase_profile
from FestinaLente.analytics.derive.batch.aggregate_world_frames import analyze_batch_world_frames





def analyze_batch(batch_results : BatchRunResults, processing_plan : ProcessingPlan) -> BatchAnalysis:
    """ analyze a batch of runs. """

    if batch_results.regime_config is None:
        raise ValueError("batch_results.regime_config is None")
    
    ###########
    metadata: BatchMetadata = build_batch_metadata(batch_results, processing_plan)


    ###########
    run_fingerprints = get_fingerprints(batch_results.runs, metadata.tail_start)
    aggregate_fingerprint = get_aggregate_fingerprints(list(run_fingerprints.values()))


    
    if processing_plan.options.include_perf:
        batch_phase_profile = aggregate_phase_profile(batch_results.runs, metadata.batch_duration)
    else:
        batch_phase_profile = None


    
    if processing_plan.options.include_world_frames:
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
        regime_label = processing_plan.regime_label
    )
    




if __name__ == "__main__":
    pass