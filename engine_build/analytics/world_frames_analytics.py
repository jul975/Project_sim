
from engine_build.runner.regime_runner import RunArtifacts
from typing import Dict
import numpy as np
from dataclasses import dataclass
from engine_build.metrics.world_frames import WorldFrames

@dataclass(frozen=True)
class SingleRunWorldFrameSummary:
    """ Summary of single run world frame analytics. """
    mean_occupancy_rate: float
    mean_crowding_nonzero: float
    mean_peak_density_sampled: float

    mean_resource_level: float
    mean_resource_heterogeneity: float
    mean_resource_depletion_rate: float

    mean_energy_level_sampled: float
    mean_energy_std_sampled: float
    mean_energy_cv_sampled: float

    mean_density_resource_correlation: float

@dataclass(frozen=True)
class BatchWorldFrameSummary:
    mean_occupancy_rate_over_runs: float
    mean_crowding_nonzero_over_runs: float
    peak_density_mean_over_runs: float

    mean_resource_level_over_runs: float
    mean_resource_heterogeneity_over_runs: float
    mean_resource_depletion_rate_over_runs: float

    mean_energy_level_sampled_over_runs: float
    mean_energy_std_sampled_over_runs: float
    mean_energy_cv_sampled_over_runs: float

    mean_density_resource_correlation_over_runs: float

@dataclass(frozen=True)
class BatchWorldFrameAnalysis:
    """ Analysis of batch world frames. """
    # NOTE: 
    run_summaries: Dict[int, SingleRunWorldFrameSummary]
    aggregate_summary: BatchWorldFrameSummary








def get_occupancy_rate(density : np.ndarray) -> float:
    """ get the occupancy rate of a density grid. """
    return float(np.mean(density > 0))

####
def get_mean_crowding_nonzero(density: np.ndarray) -> float:
    occupied = density[density > 0]
    if occupied.size == 0:
        return 0.0
    return float(np.mean(occupied))
######


def get_peak_density(density : np.ndarray) -> float:
    """ get the peak density of a density grid. """
    return float(np.max(density))

def get_mean_resource_level(resources : np.ndarray) -> float:
    """ get the mean resource level of a resource grid. """
    return float(np.mean(resources))

def get_resource_heterogeneity(resources : np.ndarray) -> float:
    """ get the resource heterogeneity of a resource grid. """
    return float(np.std(resources))

def get_resource_depletion_rate(resources : np.ndarray, threshold : float) -> float:
    """ get the low resource cell rate of a resource grid. """
    return float(np.mean(resources <= threshold))

##############

def get_mean_energy_level_sampled(energies: np.ndarray) -> float:
    if energies.size == 0:
        return 0.0
    return float(np.mean(energies))


def get_energy_std_sampled(energies: np.ndarray) -> float:
    if energies.size == 0:
        return 0.0
    return float(np.std(energies))


def get_energy_cv_sampled(energies: np.ndarray) -> float:
    if energies.size == 0:
        return 0.0
    mean_energy = float(np.mean(energies))
    if mean_energy <= 0.0:
        return 0.0
    return float(np.std(energies) / mean_energy)


def get_density_resource_correlation(density: np.ndarray, resources: np.ndarray) -> float:
    density_flat = density.ravel()
    resources_flat = resources.ravel()

    if density_flat.size != resources_flat.size:
        raise ValueError("density and resources must have matching shape")

    if np.std(density_flat) == 0.0 or np.std(resources_flat) == 0.0:
        return float(0.0)

    return float(np.corrcoef(density_flat, resources_flat)[0, 1])












def analyze_single_run_world_frames(world_frames : WorldFrames) -> SingleRunWorldFrameSummary:
    """ analyze single run world frames. """
    if world_frames is None:
        raise ValueError("world_frames is None")
    
    
    # get all the frames 
    densities = world_frames.density
    resources = world_frames.resources
    energies = world_frames.run_agent_energies
    
    # compute the metrics
    mean_occupancy_rate = np.mean([get_occupancy_rate(density) for density in densities])
    mean_crowding_nonzero = np.mean([get_mean_crowding_nonzero(density) for density in densities])
    peak_density_mean = np.mean([get_peak_density(density) for density in densities])

    mean_resource_level = np.mean([get_mean_resource_level(resource) for resource in resources])
    mean_resource_heterogeneity = np.mean([get_resource_heterogeneity(resource) for resource in resources])
    mean_resource_depletion_rate = np.mean([get_resource_depletion_rate(resource, 0.1) for resource in resources])

    mean_energy_level_sampled = np.mean([get_mean_energy_level_sampled(energy) for energy in energies])
    mean_energy_std_sampled = np.mean([get_energy_std_sampled(energy) for energy in energies])
    mean_energy_inequality = np.mean([get_energy_cv_sampled(energy) for energy in energies])

    mean_density_resource_correlation = np.mean([get_density_resource_correlation(density, resource) for density, resource in zip(densities, resources)])

    return SingleRunWorldFrameSummary(
        mean_occupancy_rate=mean_occupancy_rate,
        mean_crowding_nonzero=mean_crowding_nonzero,
        mean_peak_density_sampled= peak_density_mean,

        mean_resource_level=mean_resource_level,
        mean_resource_heterogeneity=mean_resource_heterogeneity,
        mean_resource_depletion_rate=mean_resource_depletion_rate,

        mean_energy_level_sampled=mean_energy_level_sampled,
        mean_energy_std_sampled=mean_energy_std_sampled,
        mean_energy_cv_sampled=mean_energy_inequality,

        mean_density_resource_correlation=mean_density_resource_correlation
    )

def get_batch_run_summary(run_results : dict[np.int64, SingleRunWorldFrameSummary]) -> BatchWorldFrameSummary:
    """ get the summary of a single run. """

    mean_occupancy_rate_over_runs = np.mean([summary.mean_occupancy_rate for summary in run_results.values()])
    mean_crowding_nonzero_over_runs = np.mean([summary.mean_crowding_nonzero for summary in run_results.values()])
    peak_density_mean_over_runs = np.mean([summary.mean_peak_density_sampled for summary in run_results.values()])

    mean_resource_level_over_runs = np.mean([summary.mean_resource_level for summary in run_results.values()])
    mean_resource_heterogeneity_over_runs = np.mean([summary.mean_resource_heterogeneity for summary in run_results.values()])
    mean_resource_depletion_rate_over_runs = np.mean([summary.mean_resource_depletion_rate for summary in run_results.values()])

    mean_energy_level_sampled_over_runs = np.mean([summary.mean_energy_level_sampled for summary in run_results.values()])
    mean_energy_std_sampled_over_runs = np.mean([summary.mean_energy_std_sampled for summary in run_results.values()])
    mean_energy_cv_sampled_over_runs = np.mean([summary.mean_energy_cv_sampled for summary in run_results.values()])

    mean_density_resource_correlation_over_runs = np.mean([summary.mean_density_resource_correlation for summary in run_results.values()])

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
def analyze_batch_world_frames(batch_runs : Dict[np.int64, RunArtifacts]) -> BatchWorldFrameAnalysis:
    """ analyze batch world frames. """
    if not batch_runs:
        raise ValueError("No runs provided.")
    
    
    run_summaries : Dict[np.int64, SingleRunWorldFrameSummary] = {}
    for id, run_results in batch_runs.items():
        if run_results.world_frames is None:
            raise ValueError(f"run_results.world_frames is None for run {id}")
        
        run_summaries[id] = analyze_single_run_world_frames(run_results.world_frames)

    aggregate_summary : BatchWorldFrameSummary = get_batch_run_summary(run_summaries)

    return BatchWorldFrameAnalysis(
        run_summaries=run_summaries,
        aggregate_summary=aggregate_summary
    )
    


    

  