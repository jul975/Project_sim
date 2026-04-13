



from FestinaLente.analytics.processing.processing_containers.run_container import RunPerformanceMetrics
from FestinaLente.runner.results import RunArtifacts


def compute_run_performance(run : RunArtifacts) -> RunPerformanceMetrics:
    """ extract performance metrics from a run artifacts, and return a run performance object. """
    if not run.phase_profile:
        raise ValueError("No phase profile found in run artifacts. Performance data is not available.")
    
    return RunPerformanceMetrics(
        movement_time=run.phase_profile.movement,
        interaction_time=run.phase_profile.interaction,
        biology_time=run.phase_profile.biology,
        commit_time=run.phase_profile.commit,
        commit_setup_time=run.phase_profile.commit_setup,
        commit_deaths_time=run.phase_profile.commit_deaths,
        commit_births_time=run.phase_profile.commit_births,
        commit_resource_regrowth_time=run.phase_profile.commit_resource_regrowth
    )