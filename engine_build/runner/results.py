
from dataclasses import dataclass
from typing import Dict
import numpy as np

from engine_build.core.engine import Engine
from engine_build.analytics.observation.simulation_metrics import SimulationMetrics
from engine_build.regimes.compiled import CompiledRegime


@dataclass
class PhaseProfile:
    """ Phase profile. 
    
    Attributes:
        - movement:                 Movement phase duration.
        - interaction:              Interaction phase duration.
        - biology:                  Biology phase duration.
        - commit:                   Commit phase duration.
        
        - commit_setup:             Commit setup duration.
        - commit_deaths:            Commit deaths duration.
        - commit_births:            Commit births duration.
        - commit_resource_regrowth: Commit resource regrowth duration.
    """
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0

    commit_setup: float = 0.0
    commit_deaths: float = 0.0
    commit_births: float = 0.0
    commit_resource_regrowth: float = 0.0






 
# raw one run results
@dataclass
class RunArtifacts:
    """ raw run results. 
    
    Attributes:
        - engine_final:       Final engine state.
        - metrics:            Simulation metrics.
        - seed:               Run seed.
        - phase_profile:      Phase profile.
    """
    engine_final : Engine | None = None
    metrics : SimulationMetrics | None = None
    seed : np.random.SeedSequence | None = None
    phase_profile : PhaseProfile | None = None

    # world frames optional 
    # NOTE: world frames part of metrics now (SimulationMetrics.world_view)
    # world_frames : WorldFrames | None = None


# raw batch results
@dataclass
class BatchRunResults:
    """ raw batch results. 
    
    Attributes:
        - runs:               Dictionary of run artifacts.
        - batch_id:           Batch seed.
        - regime_config:      Compiled regime configuration.
        - ticks:              Number of ticks.
        - batch_duration:     Batch duration in seconds.
        - max_agent_count:    Maximum agent count over all runs.
    """
    runs : Dict[np.int64, RunArtifacts]
    batch_id : int | None = None
    regime_config : CompiledRegime | None = None
    ticks : np.int64 | None = None
    batch_duration : float | None = None
    max_agent_count : int | None = None

