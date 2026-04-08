

from __future__ import annotations


import numpy as np







from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domains.world import World
    from engine_build.core.transitions.transitions import Position
    from engine_build.core.spatial.occupancy_index import OccupancyIndex



# candidate container 
@dataclass(slots=True, frozen=True)
class MoveCandidate:
    delta: tuple[int, int]
    position: tuple[int, int]
    resource_level: int
    occupancy_count: int

@dataclass(slots=True, frozen=True)
class MovementRange:
    candidates: list[MoveCandidate] = field(default_factory=list) 
    probability : np.ndarray | None = None

# build movement candidates based on passed location

def _build_move_candidates(position : "Position", world : "World", occupancy : "OccupancyIndex", include_stay=False):
    """ build_move_candidates(position, world, occupancy): """
    x, y = position

    deltas = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
    ]
    if include_stay:
        deltas.append((0, 0))

    candidates = []
    for dx, dy in deltas:
        new_pos = world.wrap_around((x + dx, y + dy))
        candidates.append(
            MoveCandidate(
                delta=(dx, dy),
                position=new_pos,
                resource_level=world.resources_at(new_pos),   # adapt to your API
                occupancy_count=occupancy.count_at(new_pos),
            )
        )
    return candidates

# score candidates 

def _score_move_candidates(
    candidates: list[MoveCandidate],
    resource_weight: float,
    crowding_weight: float,
) -> list[float]:
    scores = []
    for c in candidates:
        score = (
            resource_weight * c.resource_level
            - crowding_weight * c.occupancy_count
        )
        scores.append(score)
    """ scores are unnormalized, will be converted to probabilities later. """
    return scores

# get prob for each candidate based on score

def _softmax_probabilities(scores: list[float], temperature: float = 1.0) -> np.ndarray:
    arr = np.asarray(scores, dtype=float)

    if temperature <= 0:
        raise ValueError("temperature must be > 0")

    shifted = arr - arr.max()
    exps = np.exp(shifted / temperature)
    return exps / exps.sum()

# sample candidates and prob based on position

def sample_moves(position : "Position", world : "World", occupancy : "OccupancyIndex", resource_weight: float, crowding_weight: float, temperature: float) -> MovementRange:
    candidates = _build_move_candidates(position, world, occupancy)
    scores = _score_move_candidates(candidates, resource_weight, crowding_weight)
    probs = _softmax_probabilities(scores, temperature)
    
    return MovementRange(candidates=candidates, probability=probs)



if __name__ == "__main__":
    pass