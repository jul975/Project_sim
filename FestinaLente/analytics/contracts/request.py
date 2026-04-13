# AnalysisRequest / AnalysisOptions
# FestinaLente/analytics/contracts/request.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AnalysisOptions:
    tail_start: int = 0
    tail_fraction: float = 0.25
    include_perf: bool = False
    include_world_frames: bool = False

@dataclass(frozen=True)
class AnalysisRequest:
    regime_label: str | None = None
    options: AnalysisOptions = field(default_factory=AnalysisOptions)

    def tail_start(self, total_ticks: int) -> int:
        if total_ticks <= 0:
            raise ValueError("total_ticks must be positive")
        return int(total_ticks * (1.0 - self.options.tail_fraction))
