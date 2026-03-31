from enum import Enum
from engine_build.analytics.summaries.regime_summary import RegimeSummary


class RegimeClass(str, Enum):
    EXTINCTION = "extinction"
    COLLAPSE = "collapse"
    FRAGILE = "fragile"
    STABLE = "stable"
    ABUNDANT = "abundant"
    SATURATED = "saturated"
    OSCILLATORY = "oscillatory"   # reserved
    UNCLASSIFIED = "unclassified"





def classify_regime(summary: RegimeSummary) -> RegimeClass:
    pop_ratio = summary.mean_population_over_runs / summary.max_agent_count
    bdr = summary.birth_death_ratio
    time_cv = summary.mean_time_cv_over_runs

    stable_like = (
        time_cv <= 0.10
        and 0.95 <= bdr <= 1.05
    )

    # 1) FAILURE STATES
    if summary.extinction_rate >= 0.95:
        return RegimeClass.EXTINCTION

    if summary.extinction_rate >= 0.50:
        return RegimeClass.COLLAPSE

    # severe low-pop persistence without full extinction
    if summary.low_population_rate >= 0.80 and bdr < 0.95:
        return RegimeClass.COLLAPSE

    # 2) BOUNDARY STATE
    if summary.cap_hit_rate >= 0.20 or summary.near_cap_rate >= 0.30:
        return RegimeClass.SATURATED

    # 3) SURVIVING BUT STRESSED
    if summary.low_population_rate >= 0.20:
        return RegimeClass.FRAGILE

    # 4) INTERIOR REGIMES
    if stable_like and pop_ratio >= 0.20:
        return RegimeClass.ABUNDANT

    if stable_like:
        return RegimeClass.STABLE

    return RegimeClass.UNCLASSIFIED