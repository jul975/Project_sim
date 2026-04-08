

from __future__ import annotations

from engine_build.core.spatial.occupancy_index import OccupancyIndex
from engine_build.core.domains.world import World


# NOTE: INCOMPLETE!
def query_local_neighborhood(position, world : "World", occupancy : "OccupancyIndex", mode="von_neumann", include_center=True):
    """ query_local_neighborhood(position, world, occupancy, mode="von_neumann", include_center=True):
    returns the neighboring positions and their contents around a given position, based on the specified neighborhood mode.
    modes:
    - "von_neumann": returns the 4 orthogonal neighbors (up, down, left, right).
    - "moore": returns the 8 surrounding neighbors (including diagonals).
    """
    if mode == "von_neumann":
        neighbor_positions = world.von_neumann_neighbors(position)
    elif mode == "moore":
        neighbor_positions = world.moore_neighbors(position)
    else:
        raise ValueError(f"Invalid neighborhood mode: {mode}")
    
    if include_center:
        neighbor_positions.append(position)

    neighbor_contents = {pos: occupancy.get(pos) for pos in neighbor_positions}
    
    return neighbor_contents