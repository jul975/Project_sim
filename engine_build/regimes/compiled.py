"""Compiled regime parameter bundles consumed by the engine.

This module defines the concrete parameters produced by the regime compiler.
``CompiledRegime`` is the engine-facing counterpart to the declarative
``RegimeSpec`` layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnergyParams:
    """Compiled energy-system parameters.

    Attributes:
        max_energy: Maximum agent energy cap.
        energy_init_range: Inclusive initial-energy range used for agent
            initialization.
        max_harvest: Maximum resource harvest per interaction.
        movement_cost: Energy cost paid on movement.
        reproduction_threshold: Minimum energy required to reproduce.
        reproduction_cost: Energy spent when reproduction succeeds.
    """

    max_energy: int
    energy_init_range: tuple[int, int]
    max_harvest: int
    movement_cost: int
    reproduction_threshold: int
    reproduction_cost: int


@dataclass(frozen=True)
class ReproductionParams:
    """Compiled reproduction parameters outside the energy budget.

    Attributes:
        probability: Base reproduction probability.
        probability_change_condition: Threshold or condition value used by the
            reproduction logic.
    """

    probability: float
    probability_change_condition: float


@dataclass(frozen=True)
class ResourceParams:
    """Compiled resource-system parameters.

    Attributes:
        max_resource_level: Maximum resource value per world cell.
        regen_rate: Deterministic per-tick regrowth amount.
    """

    max_resource_level: int
    regen_rate: int


@dataclass(frozen=True)
class LandscapeParams:
    """Compiled landscape-generation parameters.

    Attributes:
        correlation: Spatial correlation factor used to smooth the fertility
            field.
        contrast: Contrast multiplier applied to the smoothed fertility field.
        floor: Minimum fertility floor retained after scaling.

    Notes:
        ``correlation`` influences smoothing width, while ``contrast`` and
        ``floor`` shape the final fertility range.
    """

    correlation: float
    contrast: float
    floor: float


@dataclass(frozen=True)
class PopulationParams:
    """Compiled population constraints.

    Attributes:
        max_agent_count: Hard population capacity for the run.
        initial_agent_count: Number of agents created at initialization.
        max_age: Maximum age before deterministic death.
    """

    max_agent_count: int
    initial_agent_count: int
    max_age: int


@dataclass(frozen=True)
class WorldParams:
    """Compiled world dimensions.

    Attributes:
        world_width: Width of the toroidal world grid.
        world_height: Height of the toroidal world grid.
    """

    world_width: int
    world_height: int


@dataclass(frozen=True)
class CompiledRegime:
    """Concrete engine-facing parameter bundle derived from a ``RegimeSpec``.

    Attributes:
        energy_params: Compiled energy-system parameters.
        resource_params: Compiled resource-system parameters.
        reproduction_params: Compiled reproduction parameters.
        population_params: Compiled population constraints.
        world_params: Compiled world dimensions.
        landscape_params: Compiled fertility landscape parameters.
    """

    energy_params: EnergyParams
    resource_params: ResourceParams
    reproduction_params: ReproductionParams
    population_params: PopulationParams
    world_params: WorldParams
    landscape_params: LandscapeParams

    @classmethod
    def from_dict(cls, d: dict) -> "CompiledRegime":
        """Build a compiled regime from a nested dictionary representation.

        Args:
            d: Mapping whose nested subsystem dictionaries match the compiled
                dataclass field names.

        Returns:
            Fully materialized compiled regime instance.
        """

        outer = dict(d)

        ep = outer.get("energy_params")
        if isinstance(ep, dict):
            outer["energy_params"] = EnergyParams(**ep)

        rp = outer.get("resource_params")
        if isinstance(rp, dict):
            outer["resource_params"] = ResourceParams(**rp)

        rep = outer.get("reproduction_params")
        if isinstance(rep, dict):
            outer["reproduction_params"] = ReproductionParams(**rep)

        lp = outer.get("landscape_params")
        if isinstance(lp, dict):
            outer["landscape_params"] = LandscapeParams(**lp)

        pp = outer.get("population_params")
        if isinstance(pp, dict):
            outer["population_params"] = PopulationParams(**pp)

        wp = outer.get("world_params")
        if isinstance(wp, dict):
            outer["world_params"] = WorldParams(**wp)

        return cls(**outer)
