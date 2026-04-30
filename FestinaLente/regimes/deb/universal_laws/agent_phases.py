from dataclasses import dataclass
from turtle import position




@dataclass(frozen=True)
class MobilizationResult:
    mobilized_energy_J: float

@dataclass
class BranchBudget:
    soma_budget_J: float
    maturity_repro_budget_J: float

@dataclass(frozen=True)
class MaintenanceResult:
    somatic_maintenance_paid_J: float
    maturity_maintenance_paid_J: float


############################# MOBILIZATION OF ENERGY RESERVE INTO USABLE POWER
def mobilization_phase(state, params : EnergyParams, dt : float) -> MobilizationResult:
    """Compute mobilized energy from reserve."""

    def structural_length_cm(V: float, V_min: float) -> float:

        """Return structural length L = V^(1/3), in cm."""
        V_safe = max(V, V_min)
        return V_safe ** (1.0 / 3.0)


    def mobilize_power_deb_lite(state: EnergyState, params: EnergyParams) -> float:
        """
        Mobilized reserve power p_C in J/day.

        DEB-lite version:
            p_C = E_reserve * v / L

        This does not yet include the full DEB growth correction term '- r'.
        """
        L = structural_length_cm(state.V, params.V_min)
        p_C = state.E_reserve * params.v / L
        return max(p_C, 0.0)

    p_C: float = mobilize_power_deb_lite(state, params)
    # correct for time step
    # return p_C in J/day, but we will use it for a dt time step, so multiply by dt to get energy available for this time step
    return p_C * dt


    

############################# BRANCH SPLIT OF MOBILIZED ENERGY INTO SOMA AND MATURITY/REPRODUCTION

def branch_split_phase(mobilized_energy, params : EnergyParams) -> BranchBudget:
    
    """
    Split mobilized reserve power into soma and maturity/reproduction branches.

    Returns:
        p_soma: J/day
        p_maturity_repro: J/day
    """
    p_C = mobilized_energy


    p_soma = params.kappa * p_C
    p_maturity_repro = (1.0 - params.kappa) * p_C
    return BranchBudget(soma_budget_J=p_soma, maturity_repro_budget_J=p_maturity_repro)


############################# PAY MAINTENANCE COSTS FIRST, THEN DETERMINE SURPLUS FOR GROWTH/MATURATION/REPRODUCTION


def maintenance_phase(state, params, dt, branch_budget: BranchBudget) -> MaintenanceResult:
    """Pay structural and maturity maintenance first."""
    def somatic_maintenance_power(state: EnergyState, params: EnergyParams) -> float:
        """
        Somatic maintenance power p_S in J/day.

        p_S = [p_M] * V
        """
        V_safe = max(state.V, params.V_min)
        return params.p_M * V_safe
    
    def maturity_maintenance_power(state: EnergyState, params: EnergyParams) -> float:
        """
        Maturity maintenance power p_J in J/day.

        p_J = k_J * E_H
        """
        return params.k_J * state.E_H

    p_S = somatic_maintenance_power(state, params)
    p_J = maturity_maintenance_power(state, params)

    branch_budget_after_somatic = max(branch_budget.soma_budget_J - p_S * dt, 0.0)
    branch_budget_after_maturity = max(branch_budget.maturity_repro_budget_J - p_J * dt, 0.0)

    branch_budget.soma_budget_J = branch_budget_after_somatic
    branch_budget.maturity_repro_budget_J = branch_budget_after_maturity

    return MaintenanceResult(somatic_maintenance_paid_J=p_S * dt, maturity_maintenance_paid_J=p_J * dt)


############################# MOVEMENT PHASE, (needs implementation placeholder for now)


def movement_phase(agent, soma_surplus, params, dt) -> MovementResult:
    """Determine energy-limited movement capacity and deduct actual movement cost."""
    ## needs implementation


    pass

############################# STRUCTURAL GROWTH PHASE

def growth_phase(state : EnergyState, soma_surplus_after_movement, params, dt) -> GrowthResult:
    """Convert remaining soma surplus into structural volume."""
    
    
    def structural_growth_rate_cm3_per_day(
    p_soma: float,
    
    params: EnergyParams,
    movement_power: float = 0.0,
) -> tuple[float, float]:
        """
        Convert surplus soma-branch power into structural growth rate.

        Returns:
            dV_dt: cm^3/day
            soma_deficit: J/day
        """
        p_G_raw = p_soma - movement_power

        if p_G_raw <= 0.0:
            soma_deficit = -p_G_raw
            return 0.0, soma_deficit

        dV_dt = p_G_raw / params.E_G
        return dV_dt, 0.0
    movement_power_j = 0.0 # placeholder prob terain movement cost 
    dV = structural_growth_rate_cm3_per_day(soma_surplus_after_movement, params, movement_power_j) * dt

    state.V += dV

    return dV

    



############################# MATURITY/REPRODUCTION PHASE


def maturity_reproduction_phase(state, maturity_surplus, params) -> MaturityResult:
    """Use remaining maturity branch for maturation or reproduction buffer."""


    def maturation_power(
        p_maturity_repro: float,
        
    ) -> tuple[float, float]:
        """
        Compute surplus power available for maturation.

        Returns:
            p_H: J/day, maturation power
            maturity_deficit: J/day
        """
        p_H_raw = p_maturity_repro 

        if p_H_raw <= 0.0:
            maturity_deficit = -p_H_raw
            return 0.0, maturity_deficit

        return p_H_raw, 0.0
#### NEW AGENT CLASS
from dataclasses import dataclass

@dataclass(frozen=True)
class EnergyParams:
    v: float = 0.02737          # cm / day
    p_M: float = 2511.0         # J / day / cm^3
    E_G: float = 7853.0         # J / cm^3
    kappa: float = 0.7978       # allocation fraction to soma
    k_J: float = 0.002          # 1 / day
    V_min: float = 1e-6         # cm^3 numerical floor


@dataclass
class EnergyState:
    E_reserve: float  # J
    V: float          # cm^3
    E_H: float        # J
    E_R: float        # J

