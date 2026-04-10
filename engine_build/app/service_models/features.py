from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionFeatures:
    perf_profiling: bool = False
    capture_world_frames: bool = False
    plotting: bool = False
    plot_dev: bool = False
    animate: bool = False

    change_condition: bool = False




if __name__ == "__main__":
    pass