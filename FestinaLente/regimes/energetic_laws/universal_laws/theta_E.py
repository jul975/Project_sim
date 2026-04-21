





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