from dataclasses import dataclass

from FestinaLente.analytics.processing.processing_containers.run_container import Fingerprint, RunFrames, RunPerformanceMetrics, SingleRunWorldFrameSummary
from FestinaLente.analytics.processing.run.run_performance import compute_run_performance
from FestinaLente.analytics.processing.run.run_world_frames import compute_single_world_frames
from FestinaLente.analytics.processing.run.world_frame_summary import analyze_single_run_world_frames
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.utils.results import RunArtifacts

from FestinaLente.analytics.processing.run.fingerprint import compute_fingerprint


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
    run_fingerprint: Fingerprint = compute_fingerprint(run.metrics, processing_plan.tail_start)
    run_performance: RunPerformanceMetrics | None = None
    run_frames: RunFrames | None = None
    single_run_world_frame_summary: SingleRunWorldFrameSummary | None = None

    if processing_plan.options.include_perf:
        run_performance = compute_run_performance(run)

    if processing_plan.options.include_world_frames or processing_plan.options.animate_run:
        run_frames = compute_single_world_frames(run.metrics.world_view)

    if processing_plan.options.include_world_frames:
        #######################
            # need cleanup and dissection, logic is lost and confused right now.
            # also need to review the data flow and dependencies between processing steps, and how to structure

    # NOTE: systemic problem is located here, I'm passing in the global max resource level, but this should be the resource array modded to 0.1 for each entry.
    # this is because the threshold for depletion rate is based on the resource level, not a fixed value. This needs to be reviewed and fixed in the future.

        ########################
        single_run_world_frame_summary = analyze_single_run_world_frames(run_view=run.metrics.world_view, max_resource_level=80)

    return ProcessedRun(
        run_fingerprint=run_fingerprint,
        run_profile=run_performance,
        run_frames=run_frames,
        single_run_world_frame_summary=single_run_world_frame_summary,
    )


    