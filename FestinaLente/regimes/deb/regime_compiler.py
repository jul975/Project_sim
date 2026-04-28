
from FestinaLente.regimes.deb.domain_dataclasses import EnergeticLawSpec
from FestinaLente.regimes.deb.universal_laws.theta_E import CompiledEnergetics


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
    )

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
