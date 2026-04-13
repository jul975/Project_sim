"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""
from FestinaLente.analytics.derive.process_run import process_runs
from contracts.metadata import BatchMetadata, build_batch_metadata
from contracts.batch_analysis import BatchAnalysis
from app.execution.workflows.compile_workflow import ProcessingPlan

from derive.batch.aggregate_fingerprint import get_aggregate_fingerprints
from derive.batch.aggregate_performance import aggregate_phase_profile
from derive.batch.aggregate_world_frames import analyze_batch_world_frames

from runner.batch_runner import BatchRunResults
from derive.run.fingerprint import get_fingerprints





def analyze_batch(processing_plan : ProcessingPlan, batch_results : BatchRunResults) -> BatchAnalysis:
    """ analyze a batch of runs. """

    if batch_results.regime_config is None:
        raise ValueError("batch_results.regime_config is None")
    
    ###########
    metadata: BatchMetadata = build_batch_metadata(batch_results, processing_plan)


    ###########
    # get process run data
    processed_runs = process_runs(batch_runs=batch_results.runs, processing_plan=processing_plan)

    ##########
    

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