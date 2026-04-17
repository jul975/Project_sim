"""
Presentation selection/composition

"""


from collections.abc import Callable

from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.app.execution.presenters.experiment_output import print_summarize_analytics
from FestinaLente.app.execution.presenters.plotting.plot_run import plot_batch_metrics, plot_single_run_metrics, plot_world_view_samples, plot_world_view_summary
from FestinaLente.app.execution.presenters.animation.dynamic_new import animate_run
from FestinaLente.app.execution.workflows.compile_workflow import PresentationPlan

Presenter = Callable[[AnalyticsBundle], None]


def _present_console_summary(output: AnalyticsBundle) -> None:
    print_summarize_analytics(
        batch_analysis=output.batch_analysis,
        regime_class=output.regime_class,
        summary=output.regime_summary,
    )


def _get_first_run_metrics(output: AnalyticsBundle):
    for run_id, run in output.batch_analysis.all_runs.items():
        if run.metrics is not None:
            return int(run_id), run.metrics
    raise ValueError("No run metrics available for presentation.")


def _present_batch_plots(output: AnalyticsBundle) -> None:
    plot_batch_metrics(output.batch_analysis)


def _present_dev_plots(output: AnalyticsBundle) -> None:
    run_id, metrics = _get_first_run_metrics(output)
    plot_single_run_metrics(metrics, run_id=run_id)


def _present_world_view_plots(output: AnalyticsBundle) -> None:
    _, metrics = _get_first_run_metrics(output)
    plot_world_view_summary(metrics)
    plot_world_view_samples(metrics)


def _present_animation(output: AnalyticsBundle) -> None:
    # Get the first run's artifacts for animation
    for run_id, run_artifacts in output.batch_analysis.all_runs.items():
        animate_run(run_artifacts)
        break  # Only animate the first run


def _build_presenters(plan: PresentationPlan) -> tuple[Presenter, ...]:
    presenters: list[Presenter] = [_present_console_summary]

    if plan.plotting:
        presenters.append(_present_batch_plots)
    if plan.dev_plotting:
        presenters.append(_present_dev_plots)
    if plan.world_view:
        presenters.append(_present_world_view_plots)
    if plan.animate_run:
        presenters.append(_present_animation)

    return tuple(presenters)


def present_output(presentation_plan: PresentationPlan, output: AnalyticsBundle) -> None:
    for presenter in _build_presenters(presentation_plan):
        presenter(output)



if __name__ == "__main__":
    pass