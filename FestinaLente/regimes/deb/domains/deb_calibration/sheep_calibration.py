"""
maturity threshold calibration module for sheep agents in DEB regime.


run ideal reference sheep
track net maturation energy
record E_H at weaning day and puberty day
return maturity thresholds

during calibration only: 

if age_days < anchors.weaning_age_days:
    stage = NEW_BORN
elif age_days < anchors.female_puberty_age_days:
    stage = JUVENILE
else:
    stage = ADULT

Else:

stage = stage_from_maturity(state.maturity_J, compiled_params)

"""