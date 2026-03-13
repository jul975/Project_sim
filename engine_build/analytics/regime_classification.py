from enum import Enum


class RegimeClass(str, Enum):
    COLLAPSE = "collapse"
    FRAGILE = "fragile"
    STABLE = "stable"
    ABUNDANT = "abundant"
    SATURATED = "saturated"
    OSCILLATORY = "oscillatory"   # reserved
    UNCLASSIFIED = "unclassified"




