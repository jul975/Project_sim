from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec


DEFAULT_MASTER_SEED = 20250302

EXPERIMENT_DEFAULTS = {
    "ticks": 1000,
    "runs": 10,
}

EXPLORATION_DEFAULTS = {
    "ticks": 1000,
}

VALIDATION_DEFAULTS = {
    "ticks": 1000,
    "runs": 10,
}

DEFAULT_REGIME = "stable"
DEFAULT_REGIME_CONFIG = compile_regime(regime_spec=get_regime_spec(DEFAULT_REGIME))



if __name__ == "__main__":
    pass