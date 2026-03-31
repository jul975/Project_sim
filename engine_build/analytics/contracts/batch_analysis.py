
from dataclasses import dataclass
from typing import Dict
import numpy as np

from engine_build.analytics.contracts.metadata import BatchMetadata
from engine_build.analytics.batch_level.aggregate_fingerprint import AggregatedFingerprint
from engine_build.analytics.batch_level.aggregate_performance import BatchPhaseProfile
from engine_build.analytics.batch_level.aggregate_world_frames import BatchWorldFrameAnalysis
from engine_build.analytics.run_level.fingerprint import Fingerprint
from engine_build.runner.batch_runner import RunArtifacts

# derived experiment interpretation 
@dataclass
class BatchAnalysis:
    """ Analysis of a batch of runs. 
    
    Attributes:
        - batch_metadata:       Batch metadata.
        - all_runs:             Dictionary of run artifacts.
        - aggregate_fingerprint: Aggregated fingerprint.
        - run_fingerprints:     Dictionary of run fingerprints.
        - batch_phase_profile:  Batch phase profile.
        - batch_world_frames:   Batch world frames analysis.
        - regime_label:         Regime label.
    """
    batch_metadata : BatchMetadata

    all_runs : Dict[np.int64, RunArtifacts]

    aggregate_fingerprint : AggregatedFingerprint
    run_fingerprints : Dict[np.int64, Fingerprint]
    
    batch_phase_profile : BatchPhaseProfile | None = None
    batch_world_frames : BatchWorldFrameAnalysis | None = None
    regime_label : str | None = None

