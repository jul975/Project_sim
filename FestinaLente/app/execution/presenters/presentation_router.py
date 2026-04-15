"""
Presentation selection/composition

"""





from FestinaLente.analytics.contracts.results import AnalyticsBundle
from FestinaLente.app.execution.presenters.experiment_output import print_summarize_analytics


def present_output(output: AnalyticsBundle):
    print_summarize_analytics(batch_analysis=output.batch_analysis, regime_class=output.regime_class, summary=output.regime_summary)