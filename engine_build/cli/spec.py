from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REGIME_OPTIONS: tuple[str, ...] = (
    "stable",
    "fragile",
    "abundant",
    "saturated",
    "collapse",
    "extinction",
)

VERIFICATION_SUITES: dict[str, tuple[str, ...]] = {
    "all": (str(PROJECT_ROOT / "tests" / "verification"),),
    "determinism": (
        str(PROJECT_ROOT / "tests" / "verification" / "test_determinism.py"),
    ),
    "invariants": (
        str(PROJECT_ROOT / "tests" / "verification" / "test_invariants.py"),
    ),
    "rng": (
        str(PROJECT_ROOT / "tests" / "verification" / "test_rng_isolation.py"),
    ),
    "snapshots": (
        str(PROJECT_ROOT / "tests" / "verification" / "test_snapshots.py"),
    ),
}

VALIDATION_SUITES: dict[str, tuple[str, ...]] = {
    "all": (str(PROJECT_ROOT / "tests" / "validation"),),
    "contracts": (
        str(PROJECT_ROOT / "tests" / "validation" / "test_regime_contracts.py"),
    ),
    "separation": (
        str(PROJECT_ROOT / "tests" / "validation" / "test_regime_separation.py"),
    ),
}

# Temporary backward-compatibility layer.
# Keep this until menu.py / options.py are cleaned up.
VALIDATION_SUITE_ALIASES: dict[str, str] = {
    "test_regime_contracts": "contracts",
    "test_regime_separation": "separation",
    "regime_contracts": "contracts",
}


def verification_suite_choices() -> tuple[str, ...]:
    return tuple(VERIFICATION_SUITES.keys())


def validation_suite_choices() -> tuple[str, ...]:
    return tuple(VALIDATION_SUITES.keys())


def resolve_validation_suite_name(name: str) -> str:
    return VALIDATION_SUITE_ALIASES.get(name, name)