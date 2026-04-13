






from dataclasses import dataclass

from FestinaLente.analytics.derive.run.run_container import Fingerprint, RunFrames, SingleRunWorldFrameSummary
from FestinaLente.analytics.derive.run.world_frame_summary import analyze_single_run_world_frames
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.results import RunArtifacts

from derive.run.fingerprint import compute_fingerprint, get_fingerprints
from derive.batch.aggregate_fingerprint import get_aggregate_fingerprints
from derive.batch.aggregate_performance import aggregate_phase_profile
from derive.batch.aggregate_world_frames import analyze_batch_world_frames

from contracts.metadata import BatchMetadata
from contracts.batch_analysis import BatchAnalysis

@dataclass(frozen=True)
class ProcessedRun:
    run_fingerprint: Fingerprint
    # add other analysis products here as needed
    single_run_world_frame_summary: SingleRunWorldFrameSummary | None = None
    run_frames : RunFrames | None = None

def process_run(run : RunArtifacts, processing_plan : ProcessingPlan ) -> ProcessedRun:
    # process a single run, and extract analysis products
        # get run fingerprint
    run_fingerprint: Fingerprint = compute_fingerprint(run, processing_plan.tail_start)

    if processing_plan.options.include_world_frames:
        single_run_world_frame_summary = analyze_single_run_world_frames(run)

    if processing_plan.options.include_perf:
        run_frames = RunFrames(
            ticks=run.ticks,
            phase_frames=run.phase_profile,
            resource_frames=run.resource_frames
        )
    
    return ProcessedRun(
        run_fingerprint=run_fingerprint,
        single_run_world_frame_summary=single_run_world_frame_summary if processing_plan.options.include_world_frames else None,
        run_frames = run_frames if processing_plan.options.include_perf else None
    )




def process_runs(batch_runs : dict[int, RunArtifacts], processing_plan : ProcessingPlan ) -> ProcessedRuns:
    ## Process plan passed from upstream
    # unpack spec 
    ## process all runs, and aggregate results
    
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


    pass