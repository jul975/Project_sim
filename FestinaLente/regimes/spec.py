"""Human-authored regime specifications used as compiler inputs.

This module defines the declarative regime layer. ``RegimeSpec`` and its
sub-specifications describe ecological ratios, anchors, and controls without
storing derived engine parameters.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnergySpec:
    """Ratio-based controls for the energy system.

    Attributes:
        beta: Reproductive depletion ratio defined as
            ``reproduction_cost / reproduction_threshold``.
        gamma: Energy maturity ratio defined as
            ``reproduction_threshold / movement_cost``.
        harvest_fraction: Maximum harvest ratio defined as
            ``max_harvest / max_resource_level``.
        alpha: Metabolic pressure ratio defined as
            ``movement_cost / max_harvest``.
        initial_energy_low_ratio: Lower bound for initial energy relative to
            ``max_energy``.
        initial_energy_high_ratio: Upper bound for initial energy relative to
            ``max_energy``.
    """

    # beta = c_r / theta
    # gamma = theta / c_m
    # alpha = c_m / H_max
    # harvest_fraction = H_max / R_max
    beta: float
    gamma: float
    harvest_fraction: float

    alpha: float = 0.6
    initial_energy_low_ratio: float = 0.3
    initial_energy_high_ratio: float = 0.6


@dataclass(frozen=True)
class ReproductionSpec:
    """Probability-based controls for the reproduction system.

    Attributes:
        probability: Base reproduction probability.
        probability_change_condition: Threshold or condition value used by the
            reproduction logic to modulate probability.
    """

    probability: float = 0.25
    probability_change_condition: float = 0.5


@dataclass(frozen=True)
class ResourceSpec:
    """Ratio-based controls for world resource regrowth.

    Attributes:
        regen_fraction: Resource regrowth expressed relative to the maximum
            resource level.
    """

    regen_fraction: float


@dataclass(frozen=True)
class LandscapeSpec:
    """Controls for fertility-field generation across the world.

    Attributes:
        correlation: Spatial correlation factor used when smoothing the
            fertility landscape.
        contrast: Fertility contrast scaling applied to the smoothed field.
        floor: Minimum fertility floor retained after scaling.
    """

    correlation: float
    contrast: float
    floor: float


@dataclass(frozen=True)
class PopulationSpec:
    """Population-size and lifecycle limits for a regime.

    Attributes:
        max_agent_count: Hard population capacity for the run.
        initial_agent_count: Number of agents created at initialization.
        max_age: Maximum agent age before deterministic death.
    """

    max_agent_count: int
    initial_agent_count: int
    max_age: int


@dataclass(frozen=True)
class RegimeSpec:
    """Human-authored ecological specification for one named regime.

    Attributes:
        energy_spec: Ratio-based energy-system controls.
        resources_spec: Resource regrowth controls.
        landscape_spec: Fertility landscape controls.
        reproduction_spec: Reproduction probability controls.
        population_spec: Population capacity and lifecycle controls.
        max_energy: Anchor used to scale derived energy parameters.
        max_resource_level: Anchor used to scale resource and harvest values.
        world_size: Total world area anchor used during world compilation.

    Notes:
        ``RegimeSpec`` intentionally stores declarative controls and anchors
        only. Derived integer parameters belong in ``CompiledRegime``.
    """

    energy_spec: EnergySpec
    resources_spec: ResourceSpec
    landscape_spec: LandscapeSpec
    reproduction_spec: ReproductionSpec
    population_spec: PopulationSpec
    movement_spec: MovementSpec

    max_energy: int = 100
    max_resource_level: int = 80
    world_size: int = 400


@dataclass(frozen=True)
class MovementSpec:
    """Movement preference weights for the engine's movement system.

    Attributes:
        resource_weight: Weight applied to resource levels when scoring
            movement options.
        fertility_weight: Weight applied to fertility levels when scoring
            movement options.
        occupancy_weight: Weight applied to occupancy (agent presence) when
            scoring movement options.
    """

    movement_weight: float = 1.0
    interaction_weight: float = 1.0
    temperature: float = 1.0
