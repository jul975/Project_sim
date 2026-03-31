
from dataclasses import dataclass

from engine_build.analytics.contracts.config import AnalysisConfig
from engine_build.runner.results import BatchRunResults

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


def resolve_tail_start(total_tics: int, tail_fraction = 0.25) -> int:
    """ resolve tail start. """
    return int(total_tics * (1.0 - tail_fraction))




def build_batch_metadata(batch_results : BatchRunResults, analysis_config : AnalysisConfig) -> BatchMetadata:
    """ build batch metadata. """

    if batch_results.batch_id is None:
        raise ValueError("batch_results.batch_id is None")
    if batch_results.ticks is None:
        raise ValueError("batch_results.ticks is None")
    if batch_results.batch_duration is None:
        raise ValueError("batch_results.batch_duration is None")
    
    tail_start = resolve_tail_start(batch_results.ticks, analysis_config.tail_fraction)
    return BatchMetadata(
        batch_id=batch_results.batch_id,
        ticks=batch_results.ticks,
        n_runs=len(batch_results.runs),
        tail_start=tail_start,
        batch_duration=batch_results.batch_duration,
        max_agent_count=batch_results.max_agent_count,

        # NOTE: this is a bit of a hack, assumes all runs in a batch have the same max resource level
        max_resource_level=batch_results.runs[0].engine_final.world.max_harvest

    )


if __name__ == "__main__":
    pass