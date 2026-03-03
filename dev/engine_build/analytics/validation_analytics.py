
from engine_build.analytics.fingerprint import AggregatedFingerprint



# =============================================================================
# STABILITY METRIC: Coefficient of Variation (CV)
# =============================================================================
#
# A stable regime is defined by bounded fluctuations relative to its mean.
# This requires a *relative* measure of variance, not an absolute one.
#
# WHY NOT ABSOLUTE VARIANCE?
#   Absolute variance scales with population size, making it unsuitable for
#   comparison across differently-scaled systems:
#       std = 5  →  huge if μ = 10,  negligible if μ = 500
#
# FORMULA:
#   CV = σ / μ
#
#   Where:
#       σ  =  standard deviation of the tail population window
#       μ  =  mean population of the tail population window
#
# STABILITY CONDITION:
#   CV < ε      (ε = stability tolerance threshold)
#
# REFERENCE THRESHOLDS (ecological / dynamical systems):
#   CV < 0.1  →  highly stable
#   CV < 0.2  →  moderately stable
#   CV > 0.3  →  unstable / oscillatory
# =============================================================================


def compute_stability_cv(agg_fingerprint : AggregatedFingerprint) -> float:
    # temp note for extinction regime, need to think about it. 
    if agg_fingerprint.mean_population <= 0 or agg_fingerprint.std_population <= 0:
        return 0.0
    return agg_fingerprint.std_population / agg_fingerprint.mean_population



def reproductive_balance_tolance(agg_fingerprint : AggregatedFingerprint) -> float:
    """
    A stable regime is defined by a reproductive balance, such that births and deaths are roughly equal.
    This is not a necessary condition, but a sufficient one for stability.
    """
    pass