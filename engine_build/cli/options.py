# engine_build/cli/options.py

REGIME_OPTIONS = [
    "fragile",
    "abundant",
    "stable",
    "saturated",
    "collapse",
    "extinction",
]

VALIDATION_SUITES = [
    "all",
    "test_regime_contracts",
    "test_regime_separation",
]

VERIFICATION_SUITES = [
    "all",
    "determinism",
    "invariants",
    "rng",
    "snapshots",
    "regime",
]