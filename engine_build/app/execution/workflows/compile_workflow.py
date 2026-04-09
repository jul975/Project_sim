





from __future__ import annotations
from dataclasses import dataclass


from engine_build.app.service_models.default import EXPERIMENT_DEFAULTS
from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.spec import RegimeSpec


'''
def build_and_run_batch(batch_request: ServiceRequest) -> tuple[BatchRunResults, AnalysisContext]:
    """ build batch, run batch and return batch results from context. """

# def sep function for building and retuning batch 
    regime_spec = get_regime_spec(batch_request.regime)
    regime_config = compile_regime(regime_spec)

    ticks = batch_request.ticks if batch_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = batch_request.runs if batch_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]
'''

@dataclass
class CompiledWorkflow:
    regime_spec: RegimeSpec
    regime_config: CompiledRegime
    ticks: int
    runs: int

@dataclass
class WorkflowRequest: 
    regime: str
    ticks: int | None = None
    runs: int | None = None


def compile_workflow(workflow_request: ServiceRequest) -> CompiledWorkflow:
    """ => single source of truth for runner"""

# def sep function for building and retuning batch 
    regime_spec = get_regime_spec(workflow_request.regime)
    regime_config = compile_regime(regime_spec)

    ticks = workflow_request.ticks if workflow_request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    runs = workflow_request.runs if workflow_request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    return CompiledWorkflow(
        regime_spec=regime_spec,
        regime_config=regime_config,
        ticks=ticks,
        runs=runs
    )