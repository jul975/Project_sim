
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.analytics.processing.process_batch import analyze_batch
from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.analytics.interpretation.regime_summary import RegimeSummary, summarise_regime
from FestinaLente.analytics.interpretation.regime_classification import RegimeClass, classify_regime


from FestinaLente.runner.results import BatchRunResults

def process_results(
    batch_results: BatchRunResults,
    processing_plan: ProcessingPlan,
) -> AnalyticsBundle:
    
    # validate and pass

    # NOTE: processing request should be bases for processing plan/template as main entry point. 

    # execute analysis

    # execute interpretation



    
    

    batch_analysis: BatchAnalysis = analyze_batch(
        processing_plan=processing_plan, 
        batch_results=batch_results)


    regime_summary: RegimeSummary = summarise_regime(batch_analysis)
    regime_class: RegimeClass = classify_regime(regime_summary)

    return AnalyticsBundle(
        batch_analysis=batch_analysis,
        regime_summary=regime_summary,
        regime_class=regime_class,
    )
