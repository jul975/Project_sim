

from .agent import Agent


from engine_build.dev.perf import PerfSink, NullPerfSink, measure_block




def create_initial_agent(engine, agent_id, agent_seed, perf: PerfSink | None = None) -> Agent:
    perf = perf or NullPerfSink()
    return measure_block(
        perf,
        "agent_factory.initial.total",
        lambda: Agent(engine, agent_id, agent_seed),
    )

def create_newborn_agent(engine, agent_id, child_seed, position, perf: PerfSink | None = None) -> Agent:
    perf = perf or NullPerfSink()
    return measure_block(
        perf,
        "agent_factory.newborn.total",
        lambda: Agent(engine, agent_id, child_seed, position, perf=perf),
    )