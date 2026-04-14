

"""
All object construction becomes centralized, deterministic, and explicit.

factories.py is responsible for constructing fully-configured runtime objects from specifications.

The factory functions are the only place where objects are constructed.

Composition layer

"""

from dataclasses import dataclass

from numpy.random import SeedSequence

from .seeds import generate_run_sequences


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...app.execution.workflows.compile_workflow import EngineTemplate
    from ..batch_runner import BatchRunner



@dataclass(frozen=True)
class EngineBuildMap:
    ''' Immutable request for building a single engine instance, containing a seed and an engine template. 
    '''
    run_seed: SeedSequence
    engine_template: "EngineTemplate"





@dataclass(frozen=True)
class SingleRunPlans:
    """Collection of all generated SingleRunPlan obj's on BatchRunner level """
    batch_id: int
    single_run_plans: dict[int, EngineBuildMap]







def build_single_run_plans(batch_id: int, n_runs : int , engine_template: "EngineTemplate") -> SingleRunPlans:
    '''return dict of all run plans for a given batch id'''

    run_plans_dict = {}
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

    
def build_batch_runner() -> "BatchRunner":
    pass
