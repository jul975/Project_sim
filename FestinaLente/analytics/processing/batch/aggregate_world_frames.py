
from FestinaLente.analytics.processing.processing_containers.batch_containers import BatchWorldFrameAnalysis, BatchWorldFrameSummary
from FestinaLente.runner.utils.results import RunArtifacts
import numpy as np

from FestinaLente.analytics.processing.run.world_frame_summary import analyze_single_run_world_frames, SingleRunWorldFrameSummary












def aggregate_world_frame_summaries(run_summaries : dict[np.int64, SingleRunWorldFrameSummary]) -> BatchWorldFrameSummary:
    """ get the summary of a single run. """
    if not run_summaries:
        raise ValueError("No run summaries provided.")

    mean_occupancy_rate_over_runs = np.mean([summary.mean_occupancy_rate for summary in run_summaries.values()])
    mean_crowding_nonzero_over_runs = np.mean([summary.mean_crowding_nonzero for summary in run_summaries.values()])
    peak_density_mean_over_runs = np.mean([summary.mean_peak_density_sampled for summary in run_summaries.values()])

    mean_resource_level_over_runs = np.mean([summary.mean_resource_level for summary in run_summaries.values()])
    mean_resource_heterogeneity_over_runs = np.mean([summary.mean_resource_heterogeneity for summary in run_summaries.values()])
    mean_resource_depletion_rate_over_runs = np.mean([summary.mean_resource_depletion_rate for summary in run_summaries.values()])

    mean_energy_level_sampled_over_runs = np.mean([summary.mean_energy_level_sampled for summary in run_summaries.values()])
    mean_energy_std_sampled_over_runs = np.mean([summary.mean_energy_std_sampled for summary in run_summaries.values()])
    mean_energy_cv_sampled_over_runs = np.mean([summary.mean_energy_cv_sampled for summary in run_summaries.values()])

    mean_density_resource_correlation_over_runs = np.mean([summary.mean_density_resource_correlation for summary in run_summaries.values()])

    return BatchWorldFrameSummary(
        mean_occupancy_rate_over_runs=mean_occupancy_rate_over_runs,
        mean_crowding_nonzero_over_runs=mean_crowding_nonzero_over_runs,
        peak_density_mean_over_runs=peak_density_mean_over_runs,

        mean_resource_level_over_runs=mean_resource_level_over_runs,
        mean_resource_heterogeneity_over_runs=mean_resource_heterogeneity_over_runs,
        mean_resource_depletion_rate_over_runs=mean_resource_depletion_rate_over_runs,

        mean_energy_level_sampled_over_runs=mean_energy_level_sampled_over_runs,
        mean_energy_std_sampled_over_runs=mean_energy_std_sampled_over_runs,
        mean_energy_cv_sampled_over_runs=mean_energy_cv_sampled_over_runs,

        mean_density_resource_correlation_over_runs=mean_density_resource_correlation_over_runs
    )

    
# NOTE: runartifacts contains world_frames, have to review this in the future. 
def analyze_batch_world_frames(batch_runs : dict[int, RunArtifacts], max_resource_level : int) -> BatchWorldFrameAnalysis:
    """ analyze batch world frames. """
    if not batch_runs:
        raise ValueError("No runs provided.")
    
    
    run_summaries = {}
    for run_id, run_results in batch_runs.items():
        if run_results.metrics is None:
            raise ValueError(f"run_results.world_frames is None for run {id}")
        
        run_summaries[run_id] = analyze_single_run_world_frames(run_results.metrics.world_view , max_resource_level)

    aggregate_summary : BatchWorldFrameSummary = aggregate_world_frame_summaries(run_summaries)

    return BatchWorldFrameAnalysis(
        run_summaries=run_summaries,
        aggregate_summary=aggregate_summary
    )
    


    

  
  
if __name__ == "__main__":
    pass