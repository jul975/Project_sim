from dataclasses import dataclass

from engine_build.app.service_models.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.runner.batch_runner import BatchRunner
from engine_build.analytics.pipelines.analyze_batch import analyze_batch, AnalysisContext
from engine_build.analytics.summaries.regime_summary import summarise_regime
from engine_build.analytics.classification.regime_classification import classify_regime


@dataclass(frozen=True)
class ValidationCase:
    regime_name: str
    batch_results: object
    batch_analysis: object
    summary: object
    classified_regime: object


def run_validation_case(
    regime_name: str,
    *,
    ticks: int | None = None,
    runs: int | None = None,
    seed: int = DEFAULT_MASTER_SEED,
) -> ValidationCase:
    ticks = VALIDATION_DEFAULTS["ticks"] if ticks is None else ticks
    runs = VALIDATION_DEFAULTS["runs"] if runs is None else runs

    regime_spec = get_regime_spec(regime_name)
    regime_config = compile_regime(regime_spec)

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=runs,
        batch_id=seed,
    )

    batch_results = runner.run_batch(ticks=ticks)

    batch_analysis = analyze_batch(
        batch_results,
        AnalysisContext(regime_label=regime_name),
    )

    summary = summarise_regime(batch_analysis)
    classified = classify_regime(summary)

    return ValidationCase(
        regime_name=regime_name,
        batch_results=batch_results,
        batch_analysis=batch_analysis,
        summary=summary,
        classified_regime=classified,
    )


if __name__ == "__main__":
    pass