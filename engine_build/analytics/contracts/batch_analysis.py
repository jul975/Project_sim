
from dataclasses import dataclass

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

