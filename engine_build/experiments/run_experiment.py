from engine_build.visualisation.plot_run import plot_metrics
from engine_build.visualisation.dev_plot import plot_development_metrics

from engine_build.analytics.batch_analytics import analyze_batch
from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.runner.regime_runner import Runner, BatchRunResults
from engine_build.execution.default import EXPERIMENT_DEFAULTS

from engine_build.regimes.registry import get_regime_spec
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.compiled import CompiledRegime

from engine_build.analytics.regime_summery import (
    summarise_regime,
    classify_regime,
    RegimeSummary,
    RegimeClass,
)
from engine_build.analytics.fingerprint import AggregatedFingerprint
import numpy as np


REPORT_WIDTH = 68


def _rule(char: str = "=") -> None:
    print(char * REPORT_WIDTH)


def _section(title: str) -> None:
    print("")
    print(f"{title}:")


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _format_value(value: float | None, precision: int = 3, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    return f"{value:.{precision}f}{suffix}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _print_metric(label: str, value: str) -> None:
    print(f"  {label:<30} {value}")


def _print_split_metric(label: str, seconds: float, ratio: float | None, ratio_label: str) -> None:
    time_value = _format_value(seconds, precision=3, suffix="s")
    percent_value = _format_percent(ratio)
    _print_metric(label, f"{time_value:>12}   {percent_value:>7} {ratio_label}")


def _print_phase_summary(batch_analysis: BatchAnalysis, n_runs: int) -> None:
    profile = batch_analysis.batch_phase_profile
    if profile is None:
        return

    profiled_total = (
        profile.movement
        + profile.interaction
        + profile.biology
        + profile.commit
    )
    batch_duration = batch_analysis.batch_duration or 0.0
    unprofiled_total = max(batch_duration - profiled_total, 0.0)
    avg_run_duration = batch_duration / n_runs if n_runs > 0 else None

    _section("Performance Summary")
    _print_metric("batch_duration", _format_value(batch_analysis.batch_duration, precision=2, suffix="s"))
    _print_metric("profiled_phase_total", _format_value(profiled_total, precision=3, suffix="s"))
    _print_metric("unprofiled_overhead", _format_value(unprofiled_total, precision=3, suffix="s"))
    _print_metric("avg_duration_per_run", _format_value(avg_run_duration, precision=3, suffix="s"))

    _section("Phase Timing")
    _print_split_metric("movement", profile.movement, _safe_ratio(profile.movement, profiled_total), "of profiled")
    _print_split_metric("interaction", profile.interaction, _safe_ratio(profile.interaction, profiled_total), "of profiled")
    _print_split_metric("biology", profile.biology, _safe_ratio(profile.biology, profiled_total), "of profiled")
    _print_split_metric("commit", profile.commit, _safe_ratio(profile.commit, profiled_total), "of profiled")

    _section("Phase Share Of Batch")
    _print_split_metric("movement", profile.movement, _safe_ratio(profile.movement, batch_duration), "of batch")
    _print_split_metric("interaction", profile.interaction, _safe_ratio(profile.interaction, batch_duration), "of batch")
    _print_split_metric("biology", profile.biology, _safe_ratio(profile.biology, batch_duration), "of batch")
    _print_split_metric("commit", profile.commit, _safe_ratio(profile.commit, batch_duration), "of batch")

    _section("Commit Breakdown")
    _print_split_metric("setup", profile.commit_setup, _safe_ratio(profile.commit_setup, profile.commit), "of commit")
    _print_split_metric("deaths", profile.commit_deaths, _safe_ratio(profile.commit_deaths, profile.commit), "of commit")
    _print_split_metric("births", profile.commit_births, _safe_ratio(profile.commit_births, profile.commit), "of commit")
    _print_split_metric(
        "resource_regrowth",
        profile.commit_resource_regrowth,
        _safe_ratio(profile.commit_resource_regrowth, profile.commit),
        "of commit",
    )


def summarize_analytics(
    batch_analysis: BatchAnalysis,
    n_runs: int,
    ticks: int,
    regime_class: RegimeClass,
    summary: RegimeSummary,
) -> None:
    """Print a concise experiment report."""
    del summary

    final_populations = []
    for _, run_results in batch_analysis.batch_metrics.items():
        final_populations.append(run_results.metrics.population[-1])

    final_populations = np.array(final_populations)
    mean_final = np.mean(final_populations)
    std_final = np.std(final_populations)
    final_cv = _safe_ratio(float(std_final), float(mean_final))
    agg: AggregatedFingerprint = batch_analysis.aggregate_fingerprint

    _rule()
    _print_metric("mode", "EXPERIMENT")
    _print_metric("configured_regime", batch_analysis.regime_label or "n/a")
    _print_metric("classified_regime", regime_class.value)
    _print_metric("runs", str(n_runs))
    _print_metric("ticks", str(ticks))
    _print_metric("tail_start", str(batch_analysis.tail_start))
    _print_metric("batch_duration", _format_value(batch_analysis.batch_duration, precision=2, suffix="s"))

    _section("End-State Summary")
    _print_metric("final_population_mean", _format_value(float(mean_final), precision=2))
    _print_metric("final_population_std", _format_value(float(std_final), precision=2))
    _print_metric("final_population_cv", _format_value(final_cv, precision=4))

    _section("Tail-Window Regime Summary")
    _print_metric("mean_population_over_runs", _format_value(agg.mean_population_over_runs))
    _print_metric("std_mean_population_over_runs", _format_value(agg.std_mean_population_over_runs))
    _print_metric("extinction_rate", _format_percent(agg.extinction_rate))
    _print_metric("cap_hit_rate", _format_percent(agg.cap_hit_rate))
    _print_metric("birth_death_ratio", _format_value(agg.birth_death_ratio))
    _print_metric("mean_time_cv_over_runs", _format_value(agg.mean_time_cv_over_runs))
    _print_metric("batch_near_cap_rate", _format_percent(agg.batch_near_cap_rate))
    _print_metric("batch_low_population_rate", _format_percent(agg.batch_near_low_population_rate))


    print("")
    _rule()


def run_experiment_mode(request) -> int:
    regime_spec = get_regime_spec(request.regime)
    regime_config : CompiledRegime = compile_regime(regime_spec)
    print("======================================================================")
    print("regime_spec: ", regime_spec)
    print("======================================================================")
    print("regime_config: ", regime_config)
    print("======================================================================")
    ticks = request.ticks if request.ticks is not None else EXPERIMENT_DEFAULTS["ticks"]
    n_runs = request.runs if request.runs is not None else EXPERIMENT_DEFAULTS["runs"]

    runner = Runner(
        regime_config=regime_config,
        n_runs=n_runs,
        batch_id=request.seed,
    )

    batch_results: BatchRunResults = runner.run_regime_batch(
        ticks=ticks,
        perf_flag=request.perf_flag,
    )

    batch_analysis: BatchAnalysis = analyze_batch(
        batch_results,
        regime_label=request.regime,
        perf_flag=request.perf_flag,
    )

    summary: RegimeSummary = summarise_regime(batch_analysis)
    regime_class: RegimeClass = classify_regime(summary)

    summarize_analytics(
        batch_analysis,
        ticks=ticks,
        n_runs=n_runs,
        regime_class=regime_class,
        summary=summary,
    )

    if request.plot:
        plot_metrics({i: ra.metrics for i, ra in batch_results.runs.items()})

    if request.plot_dev:
        plot_development_metrics(batch_results, runner.batch_id)

    return 0


if __name__ == "__main__":
    pass
