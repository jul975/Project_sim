

from dataclasses import dataclass, field
import numpy as np





# NOTE: not holding agent references, only ids.
@dataclass(frozen=True)
class MovementReport:
    metabolic_deaths_count : int = 0
    age_deaths_count : int = 0



@dataclass(frozen=True)
class InteractionReport:
    post_harvest_starvation_count : int = 0


@dataclass(frozen=True)
class BiologyReport:
    reproducing_agents_count : int = 0
    post_reproduction_death_count : int = 0


@dataclass(frozen=True)
class WorldView:
    positions : np.ndarray = field(default_factory=np.ndarray)
    energies : np.ndarray = field(default_factory=np.ndarray)
    resources : np.ndarray = field(default_factory=np.ndarray)
    



@dataclass(frozen=True)
class CommitReport:
    births_count : int = 0
    deaths_count : int = 0



@dataclass(frozen=True)
class StepMetrics:
    tick : int = 0
    movement_report : MovementReport = field(default_factory=MovementReport)
    interaction_report : InteractionReport = field(default_factory=InteractionReport)
    biology_report : BiologyReport = field(default_factory=BiologyReport)
    commit_report : CommitReport = field(default_factory=CommitReport)
    world_view : WorldView = field(default_factory=WorldView)


