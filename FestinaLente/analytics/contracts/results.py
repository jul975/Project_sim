# AnalyticsBundle / AnalysisProducts
# FestinaLente/analytics/contracts/results.py
from dataclasses import dataclass

from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.analytics.interpretation.regime_summary import RegimeSummary
from FestinaLente.analytics.interpretation.regime_classification import RegimeClass

@dataclass(frozen=True)
class AnalyticsBundle:
    batch_analysis: BatchAnalysis
    regime_summary: RegimeSummary
    regime_class: RegimeClass
