

"""
All object construction becomes centralized, deterministic, and explicit.

factories.py is responsible for constructing fully-configured runtime objects from specifications.

The factory functions are the only place where objects are constructed.

Composition layer

"""

from dataclasses import dataclass

from numpy.random import SeedSequence

from engine_build.app.execution.workflows.compile_workflow import EngineTemplate


@dataclass(frozen=True)
class EngineBuildRequest:
    ''' Immutable request for building a single engine instance, containing a seed and an engine template. '''
    run_seed: SeedSequence
    engine_template: EngineTemplate


@dataclass(frozen=True)
class SingleRunPlan:
    ''' Plan for executing a single run, containing the run index, tick count, and engine build request. '''
    run_index: int | None = None
    ticks: int = 1000
    engine_request: EngineBuildRequest


def engine_factory():
    
    pass

def single_run_factory():
    pass

def batch_run_plans_factory():
    pass

