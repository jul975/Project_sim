from dataclasses import dataclass
from enum import Enum, auto


class ExecutionMode(Enum):
    EXPERIMENT = auto()
    VALIDATION = auto()
    VERIFICATION = auto()
    EXPLORATION = auto()
    DIAGNOSTIC = auto()


@dataclass(frozen=True)
class ExecutionFeatures:
    profiling: bool = False
    world_frames: bool = False
    plotting: bool = False
    export: bool = False


@dataclass(frozen=True)
class ExecutionContext:
    mode: ExecutionMode
    regime_name: str | None
    seed: int | None
    ticks: int | None
    runs: int | None
    features: ExecutionFeatures