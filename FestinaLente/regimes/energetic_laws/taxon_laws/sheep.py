

from dataclasses import dataclass


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
    - reproduction rate sanity check :	Ri = 0.004329 #/d"""
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