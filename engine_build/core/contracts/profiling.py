

from dataclasses import dataclass


@dataclass(frozen=True)
class CommitProfile:

    setup : float = 0.0
    deaths : float = 0.0
    births : float = 0.0
    resource_regrowth : float = 0.0


# temp
@dataclass(frozen=True)
class StepProfile:
    movement: float = 0.0
    interaction: float = 0.0
    biology: float = 0.0
    commit: float = 0.0
