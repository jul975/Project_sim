from __future__ import annotations

from FestinaLente.app.execution.workflows.compile_workflow import compile_workflow_plans
from FestinaLente.app.service_models.service_request_container import ServiceRequest
from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, EXPLORATION_DEFAULTS
from FestinaLente.regimes.compiled import CompiledRegime
from FestinaLente.regimes.compiler import compile_regime
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.spec import RegimeSpec
from FestinaLente.runner.batch_runner import BatchRunner
from FestinaLente.runner.utils.results import BatchRunResults, RunArtifacts
from FestinaLente.app.execution.presenters.animation.dynamic_new import animate_run


# NOTE: Service should own the workflow

# get request
# validate request
# build workflow context (compile regime, build runner, results handlers, presenters, etc.)
# run workflow
    # create single source of truth for all entry points (CLI, menu, API, etc.) to get workflow context from.
    # pass to runner
# process results runner (summarise, classify, print, plot, etc.)
# return exit code


def exploration_service_call(exploration_request: ServiceRequest) -> CompiledRegime:
    if exploration_request.service_request_meta.regime is None:
        raise ValueError("Exploration mode requires a regime.")
    
    # MODIFY TO RETURN ANIMATION 
    return compile_workflow_plans(exploration_request)



if __name__ == "__main__":
    pass