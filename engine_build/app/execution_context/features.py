from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionFeatures:
    profiling: bool = False
    world_frames: bool = False
    plotting: bool = False
    export: bool = False
    verbose: bool = False