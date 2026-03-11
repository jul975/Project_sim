"""
BatchAnalysis

analyze_batch(batch_results, config)

classify_regime(...)

"""

from dataclasses import dataclass
from typing import Dict

from engine_build.runner.regime_runner import BatchRunResults

from engine_build.regimes.compiled import CompiledRegime



from engine_build.analytics.fingerprint import AggregatedFingerprint, Fingerprint
from engine_build.metrics.metrics import SimulationMetrics
import numpy as np

# derived experiment interpretation 
@dataclass
class BatchAnalysis:
    aggregate_fingerprint : AggregatedFingerprint
    fingerprints_dict : Dict[np.int64, Fingerprint]
    batch_metrics : Dict[np.int64, SimulationMetrics]
    regime_label : str | None = None
    summary_stats : Dict[str, float] | None = None



def analyze_batch(batch_results : BatchRunResults, regime_label : str | None = None) -> BatchAnalysis:
    """ analyze a batch of runs. """
    fingerprints_dict = {}
    for i, run_results in batch_results.runs.items():
        fingerprints_dict[i] = compute_fingerprint(run_results.metrics, tail_start)

    aggregate_fingerprint = get_aggregate_fingerprints(list(fingerprints_dict.values()))

    return BatchAnalysis(
        aggregate_fingerprint=aggregate_fingerprint,
        fingerprints_dict=fingerprints_dict,
        batch_metrics=batch_results.batch_metrics,
        regime_label=regime_label
    )
    
