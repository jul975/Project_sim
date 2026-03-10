
"""
NOTE: 
    - STEP METRICS REPRESENTS OBSERVABILITY FROM OUTSIDE THE ENGINE. 
    - NO STATE MUTATION LOGIC SHOULD BE PERFORMED IN THIS LAYER.

"""


from dataclasses import dataclass, field
import numpy as np





# NOTE: not holding agent references, only ids.
@dataclass(frozen=True)
class MovementReport:
    metabolic_deaths_count : int = 0
    age_deaths_count : int = 0


@dataclass(frozen=True)
class InteractionReport:
    pending_starvation_death_count : int = 0


@dataclass(frozen=True)
class BiologyReport:
    reproducing_agents_count : int = 0
    post_reproduction_death_count : int = 0


@dataclass(frozen=True)
class CommitReport:
    births_count : int = 0
    deaths_count : int = 0

@dataclass(frozen=True)
class PositionalMetrics:
    positions : np.ndarray = field(default_factory=np.ndarray)
    energies : np.ndarray = field(default_factory=np.ndarray)


@dataclass(frozen=True)
class StepMetrics:
    tick : int = 0
    movement_report : MovementReport = field(default_factory=MovementReport)
    interaction_report : InteractionReport = field(default_factory=InteractionReport)
    biology_report : BiologyReport = field(default_factory=BiologyReport)











##################################
"""
occupied_cells = len(context.occupied_positions)
moved_surviving_agents  = sum(len(v) for v in context.occupied_positions.values())
mean_occupancy = (moved_surviving_agents  / len(context.occupied_positions)) if context.occupied_positions else 0
max_occupancy = max(len(v) for v in context.occupied_positions.values()) if context.occupied_positions else 0
ratio_t = max_occupancy / mean_occupancy if mean_occupancy > 0 else 0

occupancy_metrics : dict[str, np.float64] = {
    "occupied_cells" : occupied_cells,
    "mean_occupancy" : mean_occupancy,
    "max_occupancy" : max_occupancy,
    "ratio_t" : ratio_t
}"""