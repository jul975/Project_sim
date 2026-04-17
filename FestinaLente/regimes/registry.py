"""Registry of named human-authored regime specifications.

This module provides the canonical mapping from public regime names to their
declarative ``RegimeSpec`` definitions.
"""

from __future__ import annotations

from .spec import (
    EnergySpec,
    LandscapeSpec,
    PopulationSpec,
    RegimeSpec,
    ReproductionSpec,
    ResourceSpec,
    MovementSpec,
)


# NOTE: Population config may eventually move into a broader simulation-domain
# layer, but the public regime registry remains the canonical entry point.
REGIMES: dict[str, RegimeSpec] = {
    "stable": RegimeSpec(
        energy_spec=EnergySpec(beta=0.8, gamma=10, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
    "fragile": RegimeSpec(
        energy_spec=EnergySpec(beta=5, gamma=10, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
    "extinction": RegimeSpec(
        energy_spec=EnergySpec(beta=1.0, gamma=10, harvest_fraction=0.4),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.03),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
    "collapse": RegimeSpec(
        energy_spec=EnergySpec(beta=1.0, gamma=2.5, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.03),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
    "saturated": RegimeSpec(
        energy_spec=EnergySpec(beta=0.8, gamma=1, harvest_fraction=0.05),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
    "abundant": RegimeSpec(
        energy_spec=EnergySpec(beta=0.1, gamma=1, harvest_fraction=0.35),
        reproduction_spec=ReproductionSpec(
            probability=0.25,
            probability_change_condition=0.5,
        ),
        resources_spec=ResourceSpec(regen_fraction=0.12),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
        population_spec=PopulationSpec(
            max_agent_count=1000,
            initial_agent_count=10,
            max_age=100,
        ),
        movement_spec=MovementSpec(
                movement_weight=1.0,
                interaction_weight=1.0,
                temperature=1.0,
        )
    ),
}


def get_regime_spec(regime: str) -> RegimeSpec:
    """Return the declarative specification for a named regime.

    Args:
        regime: Public regime name such as ``stable`` or ``collapse``.

    Returns:
        The matching human-authored regime specification.

    Raises:
        ValueError: If the requested regime name is not registered.
    """

    try:
        return REGIMES[regime]
    except KeyError:
        raise ValueError(f"Unknown regime: {regime}")
