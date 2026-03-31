
from engine_build.app.execution.presenters.experiment_output import print_summarize_analytics
from engine_build.visualisation.plot_run import plot_batch_metrics, plot_single_run_metrics, plot_world_view_summary, plot_world_view_samples 

from engine_build.analytics.summaries.regime_summary import RegimeSummary
from engine_build.analytics.classification.regime_classification import RegimeClass


from engine_build.runner.results import BatchRunResults

from engine_build.analytics.contracts.batch_analysis import BatchAnalysis


from engine_build.regimes.spec import RegimeSpec




def print_experiment_spec(regime_spec : RegimeSpec) -> None:
    print("======================================================================")
    print("======================================================================")
    print("regime_spec: ")
    print(f"        energy_sec: ")
    print(f"                beta: {regime_spec.energy_spec.beta}")
    print(f"                gamma: {regime_spec.energy_spec.gamma}")
    print(f"                harvest_fraction: {regime_spec.energy_spec.harvest_fraction}")
    print(f"        reproduction_spec: ")
    print(f"                probability: {regime_spec.reproduction_spec.probability}")
    print(f"                probability_change_condition: {regime_spec.reproduction_spec.probability_change_condition}")
    print(f"        resources_spec: ")
    print(f"                regen_fraction: {regime_spec.resources_spec.regen_fraction}")
    print(f"        landscape_spec: ")
    print(f"                correlation: {regime_spec.landscape_spec.correlation}")
    print(f"                contrast: {regime_spec.landscape_spec.contrast}")
    print(f"                floor: {regime_spec.landscape_spec.floor}")
    print(f"        population_spec: ")
    print(f"                max_agent_count: {regime_spec.population_spec.max_agent_count}")
    print(f"                initial_agent_count: {regime_spec.population_spec.initial_agent_count}")
    print(f"                max_age: {regime_spec.population_spec.max_age}")

    print("======================================================================")
   
    print("======================================================================")




def present_experiment_results(batch_analysis : BatchAnalysis, ticks : int, n_runs : int, regime_class : RegimeClass, summary : RegimeSummary):

    print_summarize_analytics(
        batch_analysis,
        ticks=ticks,
        n_runs=n_runs,
        regime_class=regime_class,
        summary=summary,

    )

def present_plots(batch_results : BatchRunResults):
    plot_batch_metrics({i: ra.metrics for i, ra in batch_results.runs.items()})



def present_dev_plots(batch_results : BatchRunResults):
    
    first_metrics = batch_results.runs[0].metrics
    if first_metrics is None:
        raise ValueError("Missing metrics for run 0")

    plot_single_run_metrics(first_metrics, run_id=0)



def present_world_view_plots(batch_results : BatchRunResults):

    first_metrics = batch_results.runs[0].metrics
    plot_world_view_summary(first_metrics)
    plot_world_view_samples(first_metrics)



if __name__ == "__main__":
    pass