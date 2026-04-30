

'''
E = total reserve energy, J
V = structural volume, cm³
L = structural length = V^(1/3), cm
[E] = reserve density = E / V, J/cm³
r = specific growth rate, 1/day => daily relative increase in structural volume
v / L = reserve turnover/conductance rate, 1/day



'''

### guards
V_min = 1e-6  # cm^3, numerical floor

### species-level parameters

v = 0.02737  # cm/day, reserve turnover/conductance rate
#p_Am = 1500  # J/day/cm^2, maximum assimilation rate per
p_M = 2511  # J/day/cm^3, maintenance cost per structural volume
E_G = 7853  # J/cm^3, approximate derived Ovis value for energy density of structural volume
kappa = 0.7978  # allocation fraction to soma
k_J = 0.002  # 1/day, maturity maintenance rate coefficient



#######################################
# # State
# E_reserve  # J
# V          # cm^3 structural volume
# E_H        # J maturity
# E_R        # J reproduction buffer

# # Parameters
# v       # cm/day
# p_Am    # J/day/cm^2
# p_M     # J/day/cm^3
# E_G     # J/cm^3
# kappa   # allocation to soma
# k_J     # 1/day
# E_Hb    # maturity threshold at birth
# E_Hp    # maturity threshold at puberty
# dt      # days per tick



def mobilize(E_reserve: float, v: float, V: float,) -> float: 
    #  r: float
    ''' Mobilized reserve power -> J/day. 
    
    E_reserve = stored chemical energy
    v = how fast reserve can be conducted/mobilized relative to body geometry
    L = structural length scale
    p_C = daily usable mobilized energy
    
    '''
    V = max(V, V_min)  # numerical floor
    L = V ** (1 / 3)
    
    p_C  = E_reserve * v / L

    return p_C


def get_soma_branch(E_reserve: float, V: float, kappa: float, v: float) -> float:
    ''' Soma branch of mobilized energy. '''
    p_C = mobilize(E_reserve, v, V)
    p_soma = kappa * p_C
    return p_soma

def get_maturity_reproduction_branch(E_reserve: float, V: float, r: float, kappa: float, v: float) -> float:
    ''' Maturity/reproduction branch of mobilized energy. '''
    p_C = mobilize(E_reserve, v, V)
    p_repro = (1 - kappa) * p_C
    return p_repro

def get_structural_maintenance(mass_cm3: float, maintenance_coeff: float) -> float:
    ''' Maintenance cost. return J/day. 
    [p_M] = 2511 J / d / cm³
    p_S = [p_M] · V
    '''
    return maintenance_coeff * mass_cm3
   
    

def get_growth(p_soma: float, maintenance_cost: float, movement_cost_j ) -> float:
    ''' Structural growth rate. '''
    ''' p_soma - maintenance => structural growth'''
    p_G: float = max(p_soma - maintenance_cost - movement_cost_j, 0.0)  # J/day, energy available for growth after maintenance and movement costs
    # note: first version non negative growth/shrinkage

    
    dV = p_G / E_G # *dt
    return dV

def get_maturity_maintenance_cost(E_H: float, k_J: float) -> float:
    ''' Maturity maintenance cost. '''
    p_J = k_J * E_H
    return p_J

def get_maturity_growth(p_repro: float, maturity_maintenance_cost: float) -> float:
    ''' Maturity growth rate. '''
    p_H = p_repro - maturity_maintenance_cost
    return p_H

##################################


#####################

####################


####################





####################





####################



####################

def update_agent_state(
    state: EnergyState,
    params: EnergyParams,
    dt: float,
    movement_power: float = 0.0,
    E_H_puberty: float | None = None,
) -> EnergyState:
    """
    Advance reserve, structure, maturity, and reproduction buffer by one tick.

    dt is measured in days.
    """

    # 1. Mobilize reserve once
    p_C = mobilize_power_deb_lite(state, params)   # J/day
    mobilized_energy = min(state.E_reserve, p_C * dt)  # J

    # Convert the actually mobilized amount back to average power over dt
    p_C_effective = mobilized_energy / dt if dt > 0 else 0.0

    # 2. Remove mobilized reserve from reserve store
    E_reserve_new = state.E_reserve - mobilized_energy

    # 3. Split mobilized power
    p_soma, p_maturity_repro = split_mobilized_power(p_C_effective, params)

    # 4. Soma branch: maintenance + movement + growth
    p_S = somatic_maintenance_power(state, params)
    dV_dt, soma_deficit = structural_growth_rate_cm3_per_day(
        p_soma=p_soma,
        p_S=p_S,
        params=params,
        movement_power=movement_power,
    )
    V_new = state.V + dV_dt * dt

    # 5. Maturity/reproduction branch
    p_J = maturity_maintenance_power(state, params)
    p_H, maturity_deficit = maturation_power(p_maturity_repro, p_J)

    E_H_new = state.E_H
    E_R_new = state.E_R

    if E_H_puberty is None or state.E_H < E_H_puberty:
        E_H_new += p_H * dt
    else:
        E_R_new += p_H * dt

    return EnergyState(
        E_reserve=E_reserve_new,
        V=V_new,
        E_H=E_H_new,
        E_R=E_R_new,
    )