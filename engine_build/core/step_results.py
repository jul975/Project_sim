

from dataclasses import dataclass, field
import numpy as np



@dataclass(frozen=True)
class AgentCreationProfile:
    seed_creation : float = 0.0
    agent_creation : float = 0.0
    dict_insertion : float = 0.0

@dataclass(frozen=True)
class CommitProfile:

    setup : float = 0.0
    deaths : float = 0.0
    births : float = 0.0
    resource_regrowth : float = 0.0


# temp
@dataclass(frozen=True)
class StepProfile:
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0


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
class WorldView:
    positions : np.ndarray = field(default_factory=np.ndarray)
    energies : np.ndarray = field(default_factory=np.ndarray)
    resources : np.ndarray = field(default_factory=np.ndarray)
    



@dataclass(frozen=True)
class CommitReport:
    population : int = 0
    births_count : int = 0
    deaths_count : int = 0
    commit_profile : CommitProfile | None = None
    agent_creation_profiles : AgentCreationProfile | None = None



@dataclass(frozen=True)
class StepReport:
    tick : int = 0
    movement_report : MovementReport = field(default_factory=MovementReport)
    interaction_report : InteractionReport = field(default_factory=InteractionReport)
    biology_report : BiologyReport = field(default_factory=BiologyReport)
    commit_report : CommitReport = field(default_factory=CommitReport)

    world_view : WorldView | None = None

    step_profile : StepProfile | None = None



