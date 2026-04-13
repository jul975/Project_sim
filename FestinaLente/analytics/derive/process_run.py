






from dataclasses import dataclass

from FestinaLente.analytics.derive.run.run_container import Fingerprint, RunFrames, RunPerformanceMetrics, SingleRunWorldFrameSummary
from FestinaLente.analytics.derive.run.run_performance import compute_run_performance
from FestinaLente.analytics.derive.run.run_world_frames import compute_single_world_frames
from FestinaLente.analytics.derive.run.world_frame_summary import analyze_single_run_world_frames
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.results import RunArtifacts

from derive.run.fingerprint import compute_fingerprint, get_fingerprints
from derive.batch.aggregate_fingerprint import get_aggregate_fingerprints
from derive.batch.aggregate_performance import aggregate_phase_profile
from derive.batch.aggregate_world_frames import analyze_batch_world_frames



@dataclass(frozen=True)
class ProcessedRun:
    run_fingerprint: Fingerprint
    # add other analysis products here as needed

    run_profile : RunPerformanceMetrics | None = None

    run_frames : RunFrames | None = None

    single_run_world_frame_summary: SingleRunWorldFrameSummary | None = None
    

## First draft need to compile processing logic => processing template or plan object to pass in options and parameters for processing.


def process_run(run : RunArtifacts, processing_plan : ProcessingPlan ) -> ProcessedRun:
    # process a single run, and extract analysis products
        # get run fingerprint
    run_fingerprint: Fingerprint = compute_fingerprint(run, processing_plan.tail_start)

    if processing_plan.options.include_perf:
        run_performance : RunPerformanceMetrics = compute_run_performance(run)


    # run_frames needed for world summary and animation option. 
    if processing_plan.options.include_world_frames or processing_plan.options.animate_run:
        run_frames : RunFrames = compute_single_world_frames(run.metrics.world_view)

    if processing_plan.options.include_world_frames:
        # NOTE broken
        single_run_world_frame_summary: SingleRunWorldFrameSummary = analyze_single_run_world_frames(run.metrics.world_view, )

    
    return ProcessedRun(
        run_fingerprint=run_fingerprint,
        run_profile=run_performance if processing_plan.options.include_perf else None,
        run_frames=run_frames if processing_plan.options.animate_run else None,
        single_run_world_frame_summary=single_run_world_frame_summary if processing_plan.options.include_world_frames else None,
        
    )


    pass