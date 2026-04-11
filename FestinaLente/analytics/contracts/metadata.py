
from dataclasses import dataclass

from FestinaLente.analytics.contracts.analysis_context import AnalysisContext
from FestinaLente.runner.results import BatchRunResults

@dataclass(frozen=True)
class BatchMetadata:
    """ Batch metadata. 
    
    Attributes:
        - batch_id:             Batch seed.
        - ticks:                Number of ticks.
        - tail_start:           Tail start tick.
        - n_runs:               Number of runs.
        - batch_duration:       Batch duration in seconds.
        - max_agent_count:      Maximum agent count over all runs.
        - max_resource_level:   Maximum resource level.
    """
    batch_id: int
    ticks: int
    tail_start: int
    n_runs: int
    batch_duration: float | None
    max_agent_count: int
    max_resource_level: int







def build_batch_metadata(batch_results : BatchRunResults, analysis_context : AnalysisContext) -> BatchMetadata:
    """ build batch metadata. """

    if batch_results.batch_id is None:
        raise ValueError("batch_results.batch_id is None")
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    if batch_results.batch_duration is None:
        raise ValueError("batch_results.batch_duration is None")
    
    return BatchMetadata(
        batch_id=batch_results.batch_id,
        ticks=analysis_context.total_tics,
        n_runs=analysis_context.n_runs,
        tail_start=analysis_context.tail_start,
        batch_duration=batch_results.batch_duration,
        max_agent_count=analysis_context.compiled_regime.population_params.max_agent_count,

        # NOTE: this is a bit of a hack, assumes all runs in a batch have the same max resource level
        max_resource_level=analysis_context.compiled_regime.resource_params.max_resource_level

    )


if __name__ == "__main__":
    pass