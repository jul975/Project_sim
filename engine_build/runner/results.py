
from dataclasses import dataclass
from typing import Dict
import numpy as np

from engine_build.core.engine import Engine
from engine_build.analytics.metrics.metrics import SimulationMetrics
from engine_build.regimes.compiled import CompiledRegime


@dataclass
class PhaseProfile:
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
    runs : Dict[np.int64, RunArtifacts]
    batch_id : int | None = None
    regime_config : CompiledRegime | None = None
    ticks : np.int64 | None = None
    batch_duration : float | None = None
    max_agent_count : int | None = None

