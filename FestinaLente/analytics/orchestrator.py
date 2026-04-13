# FestinaLente/analytics/orchestrator.py



from FestinaLente.analytics.derive.process_batch import analyze_batch
from FestinaLente.analytics.contracts.request import AnalysisRequest
from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.analytics.interpretation.regime_summary import summarise_regime
from FestinaLente.analytics.interpretation.regime_classification import classify_regime
from FestinaLente.runner.results import BatchRunResults

def process_results(
    batch_results: BatchRunResults,
    request: AnalysisRequest,
) -> AnalyticsBundle:
    
    # validate and pass

    # execute analysis

    # execute interpretation

    
    

    batch_analysis = analyze_batch(batch_results, request)

    
    regime_summary = summarise_regime(batch_analysis)
    regime_class = classify_regime(regime_summary)

    return AnalyticsBundle(
        batch_analysis=batch_analysis,
        regime_summary=regime_summary,
        regime_class=regime_class,
    )
