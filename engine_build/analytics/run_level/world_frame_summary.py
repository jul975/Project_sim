

from dataclasses import dataclass, field
import numpy as np

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

@dataclass
class RunFrames:
    """ Metrics of world frames. """
    densities: list[np.ndarray] = field(default_factory=list)
    resources: list[np.ndarray] = field(default_factory=list)
    energies: list[np.ndarray] = field(default_factory=list)

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









def analyze_single_run_world_frames( world_frames : list[WorldView], max_resource_level : int) -> SingleRunWorldFrameSummary:
    """ analyze single run world frames. """
    if world_frames is None:
        raise ValueError("world_frames is None")
    
    # NOTE: 0.1 is a magic number, should be a parameter stored in regime config.
    threshold = 0.1 * max_resource_level
    
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

    max_resource_level = np.max([np.max(resource) for resource in resources])
    
    mean_resource_depletion_rate = np.mean([get_resource_depletion_rate(resource, threshold) for resource in resources])

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