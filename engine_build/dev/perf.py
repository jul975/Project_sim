
import time


class PerfSink:
    def add_time(self, key: str, dt: float) -> None:
        pass

class DictPerfSink(PerfSink):
    def __init__(self) -> None:
        self.times: dict[str, float] = {}

    def add_time(self, key: str, dt: float) -> None:
        self.times[key] = self.times.get(key, 0.0) + dt

def measure_block(perf: PerfSink, key: str, fn):
    t0 = time.perf_counter()
    result = fn()
    perf.add_time(key, time.perf_counter() - t0)
    return result


class NullPerfSink(PerfSink):
    pass
