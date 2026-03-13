"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""

from dataclasses import dataclass
from typing import Dict

from engine_build.runner.regime_runner import BatchRunResults


from engine_build.analytics.fingerprint import compute_fingerprint, get_aggregate_fingerprints


from engine_build.analytics.fingerprint import AggregatedFingerprint, Fingerprint
from engine_build.runner.regime_runner import RunArtifacts
import numpy as np






# derived experiment interpretation 
@dataclass
class BatchAnalysis:
    aggregate_fingerprint : AggregatedFingerprint
    fingerprints_dict : Dict[np.int64, Fingerprint]
    batch_metrics : Dict[np.int64, RunArtifacts]
    regime_label : str | None = None
    summary_stats : Dict[str, float] | None = None
    ticks : np.int64 | None = None
    batch_id : int | None = None
    tail_start : np.int64 | None = None



def analyze_batch(batch_results : BatchRunResults, regime_label : str | None = None) -> BatchAnalysis:
    """ analyze a batch of runs. """
    fingerprints_dict = {}
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    # change to last 25% of run later on 
    tail_start = int(batch_results.ticks * 0.75)

    
    for i, run_results in batch_results.runs.items():
        if run_results.metrics is None:
            raise ValueError(f"run_results.metrics is None for run {i}")
        fingerprints_dict[i] = compute_fingerprint(run_results.metrics, tail_start)

    aggregate_fingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))

    return BatchAnalysis(
        aggregate_fingerprint=aggregate_fingerprint,
        fingerprints_dict=fingerprints_dict,
        batch_metrics=batch_results.runs,
        regime_label=regime_label,
        ticks=batch_results.ticks,
        batch_id=batch_results.batch_id,
        tail_start=tail_start,

    )
    
