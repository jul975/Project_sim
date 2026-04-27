"""
Sheep specific values from amp
"""


from dataclasses import dataclass

"""
V controls L
L and v control mobilization
mobilization controls available energy flow
κ controls allocation
allocation controls growth/maturation/reproduction
"""




@dataclass(frozen=True)
class SheepEnergeticSpec:
    """Model concept	AmP anchor
    - birth mass : 	Wwb = 5.4 kg
    - adult female mass : 	Wwi = 86 kg
    - female puberty time: 	tp = 548 d
    - weaning / nutritional independence :	tx = 135 d
    - somatic allocation fraction :	kap = 0.7978
    - growth efficiency : 	kap_G = 0.7994
    - reproduction efficiency: 	kap_R = 0.95
    - maturity maintenance : 	k_J = 0.002 1/d
    - somatic maintenance :	p_M = 2511 J/d/cm³
    - energy conductance : 0.02737 cm/d
    - reproduction rate sanity check :	Ri = 0.004329 #/d"""
    assimilation_efficiency = 0.45
    v_conductance = 0.02737
    wwb = 5.4
    wwi = 86.0
    tp = 548
    tx = 135
    kap = 0.7978
    kap_G = 0.7994
    Kap_R = 0.95
    k_J = 0.002 #1/d
    p_M = 2511 #J/d/cm³
    Ri = 0.004329 #/d


@dataclass(frozen=True)
class SheepEmpiricalAnchors:
    assimilation_efficiency : float = 0.45
    v_conductance: float  = 0.02737

    birth_wet_mass_kg: float = 5.4
    adult_female_wet_mass_kg: float = 86.0
    weaning_age_days: float = 135.0
    female_puberty_age_days: float = 548.0
    max_lifespan_days: float = 8322.0
    max_reproduction_rate_per_day: float = 0.004329

    kappa: float = 0.7978
    growth_efficiency: float = 0.7994
    reproduction_efficiency: float = 0.95
    maturity_maintenance_rate_per_day: float = 0.002

    somatic_maintenance_J_per_day_per_cm3: float = 2511.0




