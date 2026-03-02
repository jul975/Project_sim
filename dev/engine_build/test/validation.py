
from engine_build.runner.regime_runner import RegimeBatchResults
from engine_build.execution.default import DEFAULT_MASTER_SEED, VALIDATION_DEFAULTS
import numpy as np

from engine_build.regimes.registry import get_regime_config
from engine_build.runner.regime_runner import BatchRunner


def run_validation_mode(args):
        """ main entry point """

        regime_config = get_regime_config(args.regime)
        ticks, n_runs = VALIDATION_DEFAULTS["ticks"], VALIDATION_DEFAULTS["runs"]
        
        runner = BatchRunner(
            regime_config = regime_config,
            ticks = ticks,
            n_runs = n_runs
            
        )

        results : RegimeBatchResults = runner.run_regime_batch()
        parse_by_regime(args.regime, results)


def parse_by_regime(regime : str, results : RegimeBatchResults) -> None:
    if regime == "stable":
        validate_stable_regime(results)
    else:
        raise ValueError(f"Unknown regime: {regime}")
    """elif regime == "extinction":
        validate_extinction_regime(results)
    elif regime == "saturated":
        validate_saturated_regime(results)
    else:
        raise ValueError(f"Unknown regime: {regime}")"""



def validate_stable_regime(result: RegimeBatchResults) -> None:
    agg = result.aggregate_fingerprint

    assert agg["extinction_rate"] < 0.1, f"Extinction rate too high. | extinction_rate = {agg['extinction_rate']}"
    assert agg["cap_hit_rate"] < 0.2, f"Cap hit rate too high. | cap_hit_rate = {agg['cap_hit_rate']}"
    

    # assert 10 < agg["mean_population"] < 50
    # assert agg["std_population"] < 5

    print("Stable regime validation passed.")


"""def run_validation(regime : str , ticks : np.int64 , n_runs : int = 5) -> str:
    results = run_main(regime, ticks, n_runs)
    return validate_stable_regime(results)"""