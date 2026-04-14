
from dataclasses import dataclass

from FestinaLente.app.execution.workflows.compile_workflow import ProcessingPlan
from FestinaLente.runner.utils.results import BatchRunResults

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







def build_batch_metadata(
    batch_results: BatchRunResults,
    request: ProcessingPlan,
) -> BatchMetadata:
    if batch_results.batch_id is None:
        raise ValueError("batch_results.batch_id is None")
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    # if batch_results.batch_duration is None:
    #     raise ValueError("batch_results.batch_duration is None")
    if batch_results.regime_config is None:
        raise ValueError("batch_results.regime_config is None")

    return BatchMetadata(
        batch_id=batch_results.batch_id,
        ticks=int(batch_results.ticks),
        n_runs=len(batch_results.runs),
        tail_start=request.tail_start(int(batch_results.ticks)),
        batch_duration=batch_results.batch_duration,
        max_agent_count=batch_results.regime_config.population_params.max_agent_count,
        max_resource_level=batch_results.regime_config.resource_params.max_resource_level,
    )



if __name__ == "__main__":
    pass