from dataclasses import dataclass
from typing import Optional

from .modes import ExecutionMode
from .features import ExecutionFeatures

@dataclass(frozen=True)
class ExecutionContext:
    mode: ExecutionMode
    regime_name: Optional[str] = None
    seed: Optional[int] = None
    ticks: Optional[int] = None
    runs: Optional[int] = None
    suite: Optional[str] = None
    features: ExecutionFeatures = ExecutionFeatures()