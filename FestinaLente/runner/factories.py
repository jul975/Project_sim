

"""
All object construction becomes centralized, deterministic, and explicit.

factories.py is responsible for constructing fully-configured runtime objects from specifications.

The factory functions are the only place where objects are constructed.

Composition layer

"""

from dataclasses import dataclass

from numpy.random import SeedSequence

from ..app.execution.workflows.compile_workflow import EngineTemplate
from ..runner.batch_runner import BatchRunner
from ..runner.seeds import generate_run_sequences


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.engine import Engine
    from .single_runner import SingleRunner



@dataclass(frozen=True)
class EngineBuildMap:
    ''' Immutable request for building a single engine instance, containing a seed and an engine template. 
    '''
    run_seed: SeedSequence
    engine_template: EngineTemplate


# @dataclass(frozen=True)
# class SingleRunPlan:
#     ''' Plan for executing a single run, containing the run index, tick count, and engine build request. '''
#     # run_index: int | None = None
#     # ticks: int = 1000
#     engine_request: EngineBuildMap


@dataclass(frozen=True)
class SingleRunPlans:
    """Collection of all generated SingleRunPlan obj's on BatchRunner level """
    batch_id: int
    single_run_plans: dict[int, EngineBuildMap]


def build_engine(engine_build_map : EngineBuildMap) -> "Engine":
    ''' gets EngineBuildMap Object => single-universal source of truth for engine setup'''
    return Engine(engine_build_map=engine_build_map)
    

def build_single_runner(engine_build_map : EngineBuildMap) -> "SingleRunner":
    """ gets EngineBuildMap obj and return ready to run single runner instance from engine_build_map"""
    return SingleRunner(engine_build_map=engine_build_map)









def build_single_run_plans(batch_id: int, n_runs : int , engine_template: EngineTemplate) -> SingleRunPlans:
    '''return dict of all run plans for a given batch id'''

    run_plans_dict : dict[int, EngineBuildMap]
    run_seeds_dic: dict[int, SeedSequence]= generate_run_sequences(batch_id, n_runs)

    for run_index, run_seed in run_seeds_dic.items():
        run_plans_dict[run_index] = EngineBuildMap(
            run_seed=run_seed,
            engine_template=engine_template
            )

    return SingleRunPlans(
        batch_id=batch_id,
        single_run_plans=run_plans_dict
    )

    
def build_batch_runner() -> BatchRunner:
    pass

