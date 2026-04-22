# release/v0.3 branch-native energetic semantics

from FestinaLente.regimes.spec import RegimeSpec
from FestinaLente.regimes.compiler import compile_regime


def extract_theta_E_spec(regime_spec: RegimeSpec) -> dict:
    """
    Declarative energetic specification.
    This is the semantic / ratio layer.
    """
    return {
        "E_max": regime_spec.max_energy,
        "R_max": regime_spec.max_resource_level,
        "alpha": regime_spec.energy_spec.alpha,
        "beta": regime_spec.energy_spec.beta,
        "gamma": regime_spec.energy_spec.gamma,
        "harvest_fraction": regime_spec.energy_spec.harvest_fraction,
        "initial_energy_low_ratio": regime_spec.energy_spec.initial_energy_low_ratio,
        "initial_energy_high_ratio": regime_spec.energy_spec.initial_energy_high_ratio,
        "regen_fraction": regime_spec.resources_spec.regen_fraction,
    }


def compile_theta_E(regime_spec: RegimeSpec) -> dict:
    """
    Engine-facing energetic specification.
    This is the actual runtime energetic bundle.
    """
    compiled = compile_regime(regime_spec)

    return {
        "max_energy": compiled.energy_params.max_energy,
        "energy_init_range": compiled.energy_params.energy_init_range,
        "max_harvest": compiled.energy_params.max_harvest,
        "movement_cost": compiled.energy_params.movement_cost,
        "reproduction_threshold": compiled.energy_params.reproduction_threshold,
        "reproduction_cost": compiled.energy_params.reproduction_cost,
        "max_resource_level": compiled.resource_params.max_resource_level,
        "regen_rate": compiled.resource_params.regen_rate,
    }



# -----------------------------
# ABSTRACT SPECIFICATIONS
# -----------------------------

@dataclass(frozen=True)
class EnergeticLawSpec:
    body_size_ref: float
    reserve_init_fraction: float
    repr_buffer_init_fraction: float
    assimilation_efficiency_base: float
    soma_allocation_kappa: float
    maintenance_coeff: float
    mass_scaling_exponent: float
    temperature_ref_K: float | None = None
    activation_energy_maint: float | None = None
    activation_energy_assim: float | None = None
    movement_mode: str = "fixed_cost"
    reproduction_mode: str = "buffer_threshold"
    death_mode: str = "reserve_failure"

@dataclass(frozen=True)
class WorldLawSpec:
    world_width: int
    world_height: int
    capacity_anchor: float
    patch_correlation: float
    patch_contrast: float
    patch_floor: float
    initial_fill_ratio: float
    world_balance_phi: float
    inflow_mode: str = "fertility_weighted"

# -----------------------------
# COMPILED RUNTIME STRUCTURES
# -----------------------------

@dataclass(frozen=True)
class CompiledEnergetics:
    reserve_init: float
    repr_buffer_init: float
    eta_base: float
    kappa: float
    maintenance_coeff: float
    mass_scaling_exponent: float
    temperature_ref_K: float | None
    activation_energy_maint: float | None
    activation_energy_assim: float | None
    movement_mode: str
    reproduction_mode: str
    death_mode: str

@dataclass(frozen=True)
class CompiledWorldEnergetics:
    world_width: int
    world_height: int
    capacity_field: np.ndarray
    initial_stock_field: np.ndarray
    inflow_field: np.ndarray

# -----------------------------
# COMPILERS
# -----------------------------

def compile_energetic_law(theta_E: EnergeticLawSpec) -> CompiledEnergetics:
    reserve_init = theta_E.reserve_init_fraction * theta_E.body_size_ref
    repr_buffer_init = theta_E.repr_buffer_init_fraction * theta_E.body_size_ref
    return CompiledEnergetics(
        reserve_init=reserve_init,
        repr_buffer_init=repr_buffer_init,
        eta_base=theta_E.assimilation_efficiency_base,
        kappa=theta_E.soma_allocation_kappa,
        maintenance_coeff=theta_E.maintenance_coeff,
        mass_scaling_exponent=theta_E.mass_scaling_exponent,
        temperature_ref_K=theta_E.temperature_ref_K,
        activation_energy_maint=theta_E.activation_energy_maint,
        activation_energy_assim=theta_E.activation_energy_assim,
        movement_mode=theta_E.movement_mode,
        reproduction_mode=theta_E.reproduction_mode,
        death_mode=theta_E.death_mode,
    )

def compile_world_law(theta_W: WorldLawSpec, demand_ref_per_tick: float) -> CompiledWorldEnergetics:
    fertility_norm = generate_patch_field(
        width=theta_W.world_width,
        height=theta_W.world_height,
        correlation=theta_W.patch_correlation,
        contrast=theta_W.patch_contrast,
        floor=theta_W.patch_floor,
    )  # values in [0, 1]

    capacity_field = theta_W.capacity_anchor * fertility_norm
    initial_stock_field = theta_W.initial_fill_ratio * capacity_field

    total_inflow = theta_W.world_balance_phi * demand_ref_per_tick

    if theta_W.inflow_mode == "uniform":
        weights = np.full_like(capacity_field, 1.0 / capacity_field.size)
    else:
        raw = fertility_norm.copy()
        weights = raw / raw.sum()

    inflow_field = total_inflow * weights

    return CompiledWorldEnergetics(
        world_width=theta_W.world_width,
        world_height=theta_W.world_height,
        capacity_field=capacity_field,
        initial_stock_field=initial_stock_field,
        inflow_field=inflow_field,
    )