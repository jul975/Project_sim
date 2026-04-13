





import numpy as np

from FestinaLente.analytics.derive.run.run_container import RunFrames
from FestinaLente.analytics.observation.world_view import WorldView












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




def compute_single_world_frames(world_view : WorldView) -> RunFrames:
    """ compute single world frames. """
    if world_view is None:
        raise ValueError("world_view is None")
    
    return sort_run_frames(world_view)

    
    