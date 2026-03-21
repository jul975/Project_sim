
from engine_build.runner.regime_runner import RunArtifacts
from typing import Dict
import numpy as np
from dataclasses import dataclass, field

from engine_build.core.step_results import WorldView

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


@dataclass
class RunFrames:
    """ Metrics of world frames. """
    densities: list[np.ndarray] = field(default_factory=list)
    resources: list[np.ndarray] = field(default_factory=list)
    energies: list[np.ndarray] = field(default_factory=list)






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


# NOTE: 0.1 is a magic number, should be a parameter, will set rel to max_resource_level, so threshold = 0.1 * max_resource_level => 10% of max_resource_level
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



def build_density_grid(positions: np.ndarray, world_shape: tuple[int, int]) -> np.ndarray:
    """Build a density grid from agent positions."""
    height, width = world_shape
    density = np.zeros((height, width), dtype=np.int32)

    if positions.size == 0:
        return density

    for x, y in positions:
        density[y, x] += 1

    return density


def sort_run_frames(world_view: list[WorldView]) -> RunFrames:
    """Convert world views into analysis-ready frame arrays."""
    if not world_view:
        raise ValueError("No world view provided.")

    run_frames = RunFrames()

    for frame in world_view:
        density = build_density_grid(frame.positions, frame.resources.shape)

        run_frames.densities.append(density)
        run_frames.resources.append(frame.resources.copy())
        run_frames.energies.append(frame.energies.copy())

    return run_frames





def analyze_single_run_world_frames( world_frames : list[WorldView]) -> SingleRunWorldFrameSummary:
    """ analyze single run world frames. """
    if world_frames is None:
        raise ValueError("world_frames is None")
    
    run_frames = sort_run_frames(world_frames)

    densities = run_frames.densities
    resources = run_frames.resources
    energies = run_frames.energies
     
    if not (len(densities) == len(resources) == len(energies)):
        raise ValueError("world_frames captured arrays have inconsistent lengths")
    
    # compute the metrics
    mean_occupancy_rate = np.mean([get_occupancy_rate(density) for density in densities])
    mean_crowding_nonzero = np.mean([get_mean_crowding_nonzero(density) for density in densities])
    peak_density_mean = np.mean([get_peak_density(density) for density in densities])

    mean_resource_level = np.mean([get_mean_resource_level(resource) for resource in resources])
    mean_resource_heterogeneity = np.mean([get_resource_heterogeneity(resource) for resource in resources])

    # NOTE: 0.1 is a magic number, should be a parameter
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
def analyze_batch_world_frames(batch_runs : dict[int, RunArtifacts]) -> BatchWorldFrameAnalysis:
    """ analyze batch world frames. """
    if not batch_runs:
        raise ValueError("No runs provided.")
    
    
    run_summaries = {}
    for run_id, run_results in batch_runs.items():
        if run_results.metrics is None:
            raise ValueError(f"run_results.world_frames is None for run {id}")
        
        run_summaries[run_id] = analyze_single_run_world_frames(run_results.metrics.world_view)

    aggregate_summary : BatchWorldFrameSummary = aggregate_world_frame_summaries(run_summaries)

    return BatchWorldFrameAnalysis(
        run_summaries=run_summaries,
        aggregate_summary=aggregate_summary
    )
    


    

  