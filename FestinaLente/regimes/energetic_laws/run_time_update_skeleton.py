
import numpy as np

def update_world_stock(stock_field, inflow_field, harvest_field, capacity_field):
    next_stock = stock_field + inflow_field - harvest_field
    return np.clip(next_stock, 0.0, capacity_field)

def update_agent_energy(agent, uptake_energy, compiled_E, temperature_K=None):
    eta = compiled_E.eta_base
    if temperature_K is not None and compiled_E.temperature_ref_K is not None:
        eta *= thermal_modifier(
            T=temperature_K,
            T_ref=compiled_E.temperature_ref_K,
            E_a=compiled_E.activation_energy_assim,
        )

    assimilation = eta * uptake_energy

    mobilized = mobilization_rule(agent.reserve_energy, agent.structure_mass)

    soma_flux = compiled_E.kappa * mobilized
    repr_flux = (1.0 - compiled_E.kappa) * mobilized

    maint = maintenance_rule(
        structure_mass=agent.structure_mass,
        coeff=compiled_E.maintenance_coeff,
        exponent=compiled_E.mass_scaling_exponent,
        temperature_K=temperature_K,
        T_ref=compiled_E.temperature_ref_K,
        E_a=compiled_E.activation_energy_maint,
    )

    growth_flux = max(0.0, soma_flux - maint)

    agent.reserve_energy = agent.reserve_energy + assimilation - mobilized
    agent.repr_buffer_energy += repr_flux
    agent.structure_mass += growth_transform(growth_flux)

    if death_trigger(agent, compiled_E.death_mode):
        agent.alive = False
