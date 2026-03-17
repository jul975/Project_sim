

# bridge, maps request to workflow

from engine_build.cli.requests import ExperimentRequest, ValidationRequest, FertilityRequest
from engine_build.experiments.run_experiment import run_experiment_mode
from engine_build.validation.run_validation import run_validation_mode

from engine_build.experiments.fertility_dist_plot import run_and_plot_population_dynamics



def dispatch(request) -> int:
    if isinstance(request, ExperimentRequest):
        return run_experiment_mode(request)
    if isinstance(request, ValidationRequest):
        return run_validation_mode(request)
    if isinstance(request, FertilityRequest):
        run_and_plot_population_dynamics()
        return 0
    raise TypeError(f"Unsupported request type: {type(request)!r}")