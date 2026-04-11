"""Transform raw execution artifacts into derived analysis products.

This module owns post-run processing such as analysis, summarization,
and classification. It does not execute simulations or present outputs.
"""




from FestinaLente.analytics.contracts import batch_analysis
from FestinaLente.analytics.contracts.batch_analysis import BatchAnalysis
from FestinaLente.analytics.analyze_batch import analyze_batch
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.results import BatchRunResults




def process_workflow(processing_plan : ProcessingPlan, batch_results : BatchRunResults) -> BatchAnalysis:


    batch_data : batch_analysis = analyze_batch(batch_results=batch_results, processing_plan=processing_plan )

    return batch_data


if __name__ == "__main__":
    pass