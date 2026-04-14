"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""
from dataclasses import dataclass

from FestinaLente.analytics.processing.processing_containers.batch_containers import AggregatedFingerprint, BatchPhaseProfile, BatchWorldFrameSummary
from FestinaLente.analytics.processing.process_run import ProcessedRun, process_run

from FestinaLente.runner.utils.results import RunArtifacts
from FestinaLente.analytics.contracts.metadata import BatchMetadata, build_batch_metadata
from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan

from FestinaLente.analytics.processing.batch.aggregate_fingerprint import get_aggregate_fingerprints
from FestinaLente.analytics.processing.batch.aggregate_performance import aggregate_phase_profile
from FestinaLente.analytics.processing.batch.aggregate_world_frames import analyze_batch_world_frames

from FestinaLente.runner.batch_runner import BatchRunResults


###############

@dataclass(frozen=True)
class ProcessedRuns:
    processed_runs_dict : dict[int, ProcessedRun]


###############


def process_runs(batch_runs : dict[int, RunArtifacts], processing_plan : ProcessingPlan ) -> ProcessedRuns:

    processed_runs : dict[int, ProcessedRun] = {}
    for run_id, run in batch_runs.items():
        processed_runs[run_id] = process_run(run, processing_plan)

    return ProcessedRuns(
        processed_runs_dict = processed_runs
    )

#####################


def analyze_batch(processing_plan : ProcessingPlan, batch_results : BatchRunResults) -> BatchAnalysis:
    """ analyze a batch of runs. """

    if batch_results.regime_config is None:
        raise ValueError("batch_results.regime_config is None")
    
    ###########
    metadata: BatchMetadata = build_batch_metadata(batch_results, processing_plan)


    ###########
    # get process run data
    processed_runs: ProcessedRuns = process_runs(batch_runs=batch_results.runs, processing_plan=processing_plan)

    ##########

    run_process_list: list[ProcessedRun] = list(processed_runs.processed_runs_dict.values())



    aggregate_fingerprint: AggregatedFingerprint = get_aggregate_fingerprints(run_process_list)

    if processing_plan.options.include_perf:
        batch_phase_profile: BatchPhaseProfile = aggregate_phase_profile(run_process_list)
    else:
        batch_phase_profile = None

    if processing_plan.options.include_world_frames:
        batch_world_frames: BatchWorldFrameSummary = analyze_batch_world_frames(run_process_list)
    else:
        batch_world_frames = None
    
    

    return BatchAnalysis(
        batch_metadata = metadata,
        
        all_runs = batch_results.runs,
        aggregate_fingerprint = aggregate_fingerprint,
        run_fingerprints= processed_runs.processed_runs_dict,
        batch_phase_profile = batch_phase_profile,
        
        batch_world_frames = batch_world_frames,
        #
        regime_label = processing_plan.regime_label
    )
    





if __name__ == "__main__":
    pass