

from dataclasses import dataclass, field
import numpy as np

from ...analytics.observation.world_view import WorldView
from .profiling import CommitProfile, StepProfile

@dataclass(frozen=True)
class AgentSetup:
    identity_words : tuple[np.int64, ...]



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
    population : int = 0
    births_count : int = 0
    deaths_count : int = 0
    commit_profile : CommitProfile | None = None



@dataclass(frozen=True)
class StepReport:
    tick : int = 0
    movement_report : MovementReport = field(default_factory=MovementReport)
    interaction_report : InteractionReport = field(default_factory=InteractionReport)
    biology_report : BiologyReport = field(default_factory=BiologyReport)
    commit_report : CommitReport = field(default_factory=CommitReport)

    world_view : WorldView | None = None

    step_profile : StepProfile | None = None



