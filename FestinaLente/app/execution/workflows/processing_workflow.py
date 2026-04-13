"""Transform raw execution artifacts into derived analysis products.

This module owns post-run processing such as analysis, summarization,
and classification. It does not execute simulations or present outputs.
"""
# FestinaLente/app/execution/workflows/processing_workflow.py
from FestinaLente.analytics.contracts.request import AnalysisOptions, AnalysisRequest
from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.analytics.orchestrator import process_results
from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.results import BatchRunResults

def _build_analysis_request(processing_plan: ProcessingPlan) -> AnalysisRequest:
    return AnalysisRequest(
        regime_label=processing_plan.regime_label,
        options=AnalysisOptions(
            tail_start=processing_plan.tail_start,
            tail_fraction=processing_plan.tail_fraction,
            include_perf=processing_plan.options.include_perf,
            include_world_frames=processing_plan.options.include_world_frames,
        ),
    )

def process_workflow(
    processing_plan: ProcessingPlan,
    batch_results: BatchRunResults,
) -> AnalyticsBundle:
    request: AnalysisRequest = _build_analysis_request(processing_plan)
    return process_results(batch_results=batch_results, request=request)


if __name__ == "__main__":
    pass