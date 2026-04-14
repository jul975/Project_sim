"""Transform raw execution artifacts into derived analysis products.

This module owns post-run processing such as analysis, summarization,
and classification. It does not execute simulations or present outputs.
"""
# FestinaLente/app/execution/workflows/processing_workflow.py
from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.analytics.orchestrator import process_results
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.utils.results import BatchRunResults


def process_workflow(
    processing_plan: ProcessingPlan,
    batch_results: BatchRunResults,
) -> AnalyticsBundle:
    
    return process_results(batch_results=batch_results, processing_plan=processing_plan)


if __name__ == "__main__":
    pass