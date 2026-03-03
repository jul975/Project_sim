
from engine_build.runner.regime_runner import RegimeBatchResults
from engine_build.execution.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
import numpy as np

from engine_build.regimes.registry import get_regime_config
from engine_build.runner.regime_runner import BatchRunner
from engine_build.analytics.fingerprint import AggregatedFingerprint
from dataclasses import fields



def validate_all_regimes(args):
    for regime in VALIDATORS:
        args.regime = regime
        run_validation_mode(args)



def run_validation_mode(args):
    regime_config = get_regime_config(args.regime)
    ticks, n_runs = VALIDATION_DEFAULTS["ticks"], VALIDATION_DEFAULTS["runs"]

    runner = BatchRunner(
        regime_config=regime_config,
        n_runs=n_runs,
        ticks=ticks,
        batch_id=DEFAULT_MASTER_SEED
    )

    try:
        results = runner.run_regime_batch()
        parse_by_regime(args.regime, results)

        print("================================================")
        print(f"[VALIDATION PASSED] regime= {args.regime}")
        print("================================================")

    except AssertionError as e:
        print("================================================")
        print(f"[VALIDATION FAILED] regime={args.regime}")
        print(f"Reason: {e}")
        print("================================================")
        raise

def parse_by_regime(regime : str, results : RegimeBatchResults) -> None:
    if regime not in VALIDATORS:
        raise ValueError(f"Unknown regime: {regime}")
    VALIDATORS[regime](results)



def validate_stable_regime(result: RegimeBatchResults) -> None:
    agg : AggregatedFingerprint = result.aggregate_fingerprint
    # cap = result.batch_metrics[0].max_agent_count
    # NOTE: look into -0 optimized mode run in python where asserts are ignored

    for f in fields(agg):
        value = getattr(agg, f.name)

        if not np.isfinite(value):
            raise AssertionError(
                f"Invalid value in aggregate fingerprint: "
                f"{f.name} = {value}"
            )

    if agg.mean_population_over_runs <= 0:
        raise AssertionError(f"Mean population is non-positive. | mean_population = {agg.mean_population_over_runs}")


    if agg.extinction_rate >= 0.1:
         raise AssertionError(f"Extinction rate too high. | extinction_rate = {agg.extinction_rate}")
    
    if agg.cap_hit_rate >= 0.2:
         raise AssertionError(f"Cap hit rate too high. | cap_hit_rate = {agg.cap_hit_rate}")    

    # NOTE: should go to 0.1, look at doc, right now 0.2 for dev speed.
    
    if agg.mean_time_cv_over_runs > 0.2:
        raise AssertionError(f"Coefficient of variation too high. | cv = {agg.mean_time_cv_over_runs}")
    
    """Use symmetric band:
Where τ ∈ [0.05, 0.15]
Interpretation:
τ = 0.05 → strict equilibrium
τ = 0.1 → moderate tolerance
τ > 0.2 → system drifting"""
    
    if abs(agg.birth_death_ratio - 1.0) > 0.1:
        raise AssertionError(f"Birth death ratio out of tolerance. | birth_death_ratio = {agg.birth_death_ratio}")
    



def validate_extinction_regime(result: RegimeBatchResults) -> None:
    agg = result.aggregate_fingerprint
    # guarding for empty dict
    cap = next(iter(result.batch_metrics.values())).max_agent_count

    for f in fields(agg):
        value = getattr(agg, f.name)

        if not np.isfinite(value):
            raise AssertionError(
                f"Invalid value in aggregate fingerprint: "
                f"{f.name} = {value}"
            )

    if agg.extinction_rate < 0.8 :
        raise AssertionError(
            f"Extinction regime failed: extinction_rate too low "
            f"({agg.extinction_rate})"
        )

    if agg.mean_population_over_runs > 0.1 * cap:
        raise AssertionError(
            f"Extinction regime failed: population not collapsed "
            f"({agg.mean_population_over_runs})"
        )
    
    for f in result.fingerprints_dict.values():
        if f.extinction_tick is None:
            raise AssertionError("Extinction regime failed: not all runs extinguished")
    

    if agg.cap_hit_rate > 0.1:
        raise AssertionError(
            f"Extinction regime hitting cap unexpectedly "
            f"({agg.cap_hit_rate})"
        )
    if agg.birth_death_ratio >= 1:
        raise AssertionError("Extinction regime not death-dominated")
    


def validate_saturated_regime(result: RegimeBatchResults) -> None:
    agg = result.aggregate_fingerprint
    cap = next(iter(result.batch_metrics.values())).max_agent_count

    for f in fields(agg):
        value = getattr(agg, f.name)

        if not np.isfinite(value):
            raise AssertionError(
                f"Invalid value in aggregate fingerprint: "
                f"{f.name} = {value}"
            )

    if agg.cap_hit_rate < 0.8:
        raise AssertionError(
            f"Saturation regime failed: cap_hit_rate too low "
            f"({agg.cap_hit_rate})"
        )

    if agg.mean_population_over_runs < 0.8 * cap:
        raise AssertionError(
            f"Saturation regime failed: population not near cap "
            f"({agg.mean_population_over_runs})"
        )

    if agg.mean_time_cv_over_runs > 0.2:
        raise AssertionError(f"Coefficient of variation too high, unstable regime | cv = {agg.mean_time_cv_over_runs}")


    if agg.extinction_rate > 0.05:
        raise AssertionError(
            f"Saturation regime showing extinction events "
            f"({agg.extinction_rate})"
        )
    if abs(agg.birth_death_ratio - 1.0) > 0.1:
        raise AssertionError("Saturated regime not balanced")

VALIDATORS = {
    "extinction": validate_extinction_regime,
    "stable": validate_stable_regime,
    "saturated": validate_saturated_regime,
}   