
from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisConfig:
    """ Analysis configuration. 
    
    Attributes:
        - tail_fraction:        Tail fraction.
        - include_perf:         Include performance analysis.
        - include_world_frames: Include world frames analysis.
        - regime_label:         Regime label.
    """
    tail_fraction: float = 0.25
    include_perf: bool = False
    include_world_frames: bool = False

    # temp value, 
    regime_label: str | None = None





if __name__ == "__main__":
    pass