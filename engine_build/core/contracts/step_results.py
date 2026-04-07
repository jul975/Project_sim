

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
    ''' MovementReport: holds data about movement outcomes, to be used for reporting and analytics. 
    attributes:
    - metabolic_deaths_count : number of agents that died from starvation during movement phase.
    - age_deaths_count : number of agents that died from old age during movement phase.
    '''
    metabolic_deaths_count : int = 0
    age_deaths_count : int = 0



@dataclass(frozen=True)
class InteractionReport:
    ''' InteractionReport: holds data about interactions and their consequences, to be used for reporting and analytics. 
    attributes:
- pending_starvation_death_count : number of agents that are expected to die from starvation after harvesting, to be applied at the end of the tick. 
    '''
    pending_starvation_death_count : int = 0


@dataclass(frozen=True)
class BiologyReport:
    ''' BiologyReport: holds data about reproduction and post-reproduction deaths, to be used for reporting and analytics. 
    attributes:
- reproducing_agents_count : number of agents that reproduced during the biology phase, to be applied at the end of the tick. 
- post_reproduction_death_count : number of agents that are expected to die from post-reproduction consequences, to be applied at the end of the tick. 
    '''
    reproducing_agents_count : int = 0
    post_reproduction_death_count : int = 0





@dataclass(frozen=True)
class CommitReport:
    ''' CommitReport: holds data about the commit phase, to be used for reporting and analytics. 
    attributes:
    - population : current population size after commit phase. 
    - births_count : number of births that occurred during the commit phase. 
    - deaths_count : number of deaths that occurred during the commit phase. 
    '''
    population : int = 0
    births_count : int = 0
    deaths_count : int = 0
    commit_profile : CommitProfile | None = None



@dataclass(frozen=True)
class StepReport:
    ''' StepReport: holds data about the entire step, to be used for reporting and analytics.   
    attributes:
    - tick : current tick number.
    - movement_report : report about the movement phase. 
    - interaction_report : report about the interaction phase. 
    - biology_report : report about the biology phase. 
    - commit_report : report about the commit phase.
    - world_view : snapshot of the world state at the end of the step, for visualization and analysis.
    - step_profile : profiling data about the step, for performance analysis.
    '''
    tick : int = 0
    movement_report : MovementReport = field(default_factory=MovementReport)
    interaction_report : InteractionReport = field(default_factory=InteractionReport)
    biology_report : BiologyReport = field(default_factory=BiologyReport)
    commit_report : CommitReport = field(default_factory=CommitReport)

    world_view : WorldView | None = None

    step_profile : StepProfile | None = None



