
from dataclasses import dataclass , field
from engine_build.regimes.compiled import CompiledRegime

def resolve_tail_start(total_tics: int, tail_fraction = 0.25) -> int:
    """ resolve tail start. """
    return int(total_tics * (1.0 - tail_fraction))

@dataclass(frozen=True)
class AnalysisOptions:
    include_perf: bool = False
    include_world_frames: bool = False

@dataclass(frozen=True)
class AnalysisContext:
    """ Analysis context. 
    
    Attributes:
        - n_runs:               Number of runs.
        - total_tics:           Total number of ticks.
        - tail_fraction:        Tail fraction.
        - regime_label:         Regime label.
        - compiled_regime:      Compiled regime.
        - options:              Analysis options.
    """


    n_runs: int | None = None
    total_tics: int | None = None
    tail_fraction: float = 0.25

    regime_label: str | None = None
    compiled_regime: CompiledRegime | None = None

    options: AnalysisOptions = field(default_factory=AnalysisOptions)

    @property
    def tail_start(self) -> int:
        return resolve_tail_start(self.total_tics, self.tail_fraction)





if __name__ == "__main__":
    pass