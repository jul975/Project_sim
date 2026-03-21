
from engine_build.regimes.spec import RegimeSpec
from engine_build.analytics.batch_analytics import BatchAnalysis
from engine_build.analytics.regime_summery import RegimeSummary, RegimeClass
from engine_build.analytics.fingerprint import AggregatedFingerprint
import numpy as np


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
    batch_duration = batch_analysis.batch_metadata.batch_duration or 0.0
    unprofiled_total = max(batch_duration - profiled_total, 0.0)
    avg_run_duration = batch_duration / n_runs if n_runs > 0 else None

    _section("Performance Summary")
    _print_metric("batch_duration", _format_value(batch_analysis.batch_metadata.batch_duration, precision=2, suffix="s"))
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


def print_summarize_analytics(
    batch_analysis: BatchAnalysis,
    n_runs: int,
    ticks: int,
    regime_class: RegimeClass,
    summary: RegimeSummary,
) -> None:
    """Print a concise experiment report."""
    


    mean_final = summary.final_populations_mean
    std_final = batch_analysis.aggregate_fingerprint.std_mean_population_over_runs
    final_cv = _safe_ratio(float(std_final), float(mean_final))
    agg: AggregatedFingerprint = batch_analysis.aggregate_fingerprint

    _rule()
    _print_metric("mode", "EXPERIMENT")
    _print_metric("configured_regime", batch_analysis.regime_label or "n/a")
    _print_metric("classified_regime", regime_class.value)
    _print_metric("runs", str(n_runs))
    _print_metric("ticks", str(ticks))
    _print_metric("tail_start", str(batch_analysis.batch_metadata.tail_start))
    _print_metric("batch_duration", _format_value(batch_analysis.batch_metadata.batch_duration, precision=2, suffix="s"))

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

    _print_phase_summary(batch_analysis, n_runs)
    print("")
    _rule()