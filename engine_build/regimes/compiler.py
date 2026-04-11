"""Compile declarative regime specifications into engine-facing parameters.

This module is the single ecological math boundary for converting
``RegimeSpec`` inputs into the concrete ``CompiledRegime`` values consumed by
the engine.
"""

from __future__ import annotations

from math import sqrt

from .compiled import (
    CompiledRegime,
    EnergyParams,
    LandscapeParams,
    PopulationParams,
    ReproductionParams,
    ResourceParams,
    SpatialWeights,
    WorldParams,
)
from .spec import RegimeSpec


def _compile_energy_system(regime_spec: RegimeSpec) -> EnergyParams:
    """Compile energy-system parameters from ratios and anchor values.

    Args:
        regime_spec: Declarative regime specification containing energy ratios
            and anchor values.

    Returns:
        Compiled energy parameters ready for engine initialization.
    """

    # Round to avoid downward bias and clamp to keep derived values valid.
    e_max = regime_spec.max_energy
    r_max = regime_spec.max_resource_level
    energy_spec = regime_spec.energy_spec

    h_max = max(1, int(round(energy_spec.harvest_fraction * r_max)))
    h_max = min(h_max, e_max)

    c_m = max(1, int(round(energy_spec.alpha * h_max)))
    c_m = min(c_m, h_max)
    c_m = min(c_m, e_max)

    theta = max(1, int(round(energy_spec.gamma * c_m)))
    theta = max(theta, c_m)
    theta = min(theta, e_max)

    c_r = max(1, int(round(energy_spec.beta * theta)))
    c_r = min(c_r, theta)

    low = max(1, int(round(energy_spec.initial_energy_low_ratio * e_max)))
    high = max(low, int(round(energy_spec.initial_energy_high_ratio * e_max)))

    return EnergyParams(
        max_energy=e_max,
        energy_init_range=(low, high),
        max_harvest=h_max,
        movement_cost=c_m,
        reproduction_threshold=theta,
        reproduction_cost=c_r,
    )


def _compile_reproduction_system(regime_spec: RegimeSpec) -> ReproductionParams:
    """Compile reproduction parameters from the declarative specification.

    Args:
        regime_spec: Declarative regime specification.

    Returns:
        Compiled reproduction parameters.
    """

    return ReproductionParams(
        probability=regime_spec.reproduction_spec.probability,
        probability_change_condition=(
            regime_spec.reproduction_spec.probability_change_condition
        ),
    )


def _compile_resource_system(regime_spec: RegimeSpec) -> ResourceParams:
    """Compile resource regrowth parameters from the declarative specification.

    Args:
        regime_spec: Declarative regime specification.

    Returns:
        Compiled resource parameters.
    """

    regen_rate = max(
        1,
        int(
            round(
                regime_spec.resources_spec.regen_fraction
                * regime_spec.max_resource_level
            )
        ),
    )

    return ResourceParams(
        max_resource_level=regime_spec.max_resource_level,
        regen_rate=regen_rate,
    )


def _compile_landscape_system(regime_spec: RegimeSpec) -> LandscapeParams:
    """Compile landscape-generation parameters from the declarative spec.

    Args:
        regime_spec: Declarative regime specification.

    Returns:
        Compiled landscape parameters.
    """

    return LandscapeParams(
        correlation=regime_spec.landscape_spec.correlation,
        contrast=regime_spec.landscape_spec.contrast,
        floor=regime_spec.landscape_spec.floor,
    )


def _compile_population_system(regime_spec: RegimeSpec) -> PopulationParams:
    """Compile population constraints from the declarative specification.

    Args:
        regime_spec: Declarative regime specification.

    Returns:
        Compiled population parameters.
    """

    return PopulationParams(
        max_agent_count=regime_spec.population_spec.max_agent_count,
        initial_agent_count=regime_spec.population_spec.initial_agent_count,
        max_age=regime_spec.population_spec.max_age,
    )


def _compile_world_system(world_area: int) -> WorldParams:
    """Compile world dimensions from the world-area anchor.

    Args:
        world_area: Total world area anchor.

    Returns:
        Compiled world dimensions derived from the square root of
        ``world_area``.
    """

    side = int(round(sqrt(world_area)))
    return WorldParams(world_width=side, world_height=side)


def compile_regime(regime_spec: RegimeSpec) -> CompiledRegime:
    """Compile a full declarative regime into engine-facing parameters.

    Args:
        regime_spec: Human-authored regime specification to compile.

    Returns:
        Fully compiled regime ready for engine initialization.

    Notes:
        This function is the intended public entry point for ecological
        compilation. Derived integer parameters should be introduced here
        rather than scattered across engine subsystems.
    """

    energy_params = _compile_energy_system(regime_spec)
    resource_params = _compile_resource_system(regime_spec)
    reproduction_params = _compile_reproduction_system(regime_spec)
    landscape_params = _compile_landscape_system(regime_spec)
    population_params = _compile_population_system(regime_spec)
    world_params = _compile_world_system(regime_spec.world_size)
    spatial_weights = SpatialWeights()

    return CompiledRegime(
        energy_params=energy_params,
        resource_params=resource_params,
        reproduction_params=reproduction_params,
        population_params=population_params,
        world_params=world_params,
        landscape_params=landscape_params,
        spatial_weights=spatial_weights
    )


def validate_regime(regime: CompiledRegime) -> None:
    """Print heuristic warnings for a compiled regime configuration.

    Args:
        regime: Compiled regime to inspect for coarse ecological warning signs.
    """

    energy = regime.energy_params
    resources = regime.resource_params

    if resources.regen_rate <= energy.movement_cost:
        print("Warning: regeneration <= movement cost -> extinction likely")

    if energy.reproduction_threshold >= energy.max_energy:
        print("Warning: reproduction unreachable")

    if energy.max_harvest <= energy.movement_cost:
        print("Warning: agents barely sustain movement")
