from dataclasses import dataclass

from FestinaLente.app.service_models.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
from FestinaLente.app.execution.workflows.compile_workflow import (
    AnalysisOptions,
    BatchPlan,
    EngineTemplate,
    ProcessingPlan,
)
from FestinaLente.regimes.registry import get_regime_spec
from FestinaLente.regimes.compiler import compile_regime
from FestinaLente.runner.batch_runner import BatchRunner
from FestinaLente.analytics.processing.process_batch import analyze_batch
from FestinaLente.analytics.interpretation.regime_summary import summarise_regime
from FestinaLente.analytics.interpretation.regime_classification import classify_regime


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

    engine_template = EngineTemplate(
        regime_config=regime_config,
        perf_flag=False,
        world_frame_flag=False,
        change_condition=False,
    )
    runner_plan = BatchPlan(
        engine_template=engine_template,
        batch_id=seed,
        n_runs=runs,
        ticks=ticks,
    )
    runner = BatchRunner(runner_plan)

    batch_results = runner.run_batch(ticks=ticks)

    batch_analysis = analyze_batch(
        processing_plan=ProcessingPlan(
            n_runs=runs,
            total_tics=ticks,
            regime_label=regime_name,
            compiled_regime=regime_config,
            options=AnalysisOptions(),
        ),
        batch_results=batch_results,
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
