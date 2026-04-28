# 27/04/26

# Implemented now:
# - reserve_J
# - structure_cm3
# - maturity_J
# - repro_buffer_J
# - κ allocation
# - somatic maintenance
# - maturity maintenance
# - growth
# - movement cost proportional to structure
# - maturity thresholds for movement/reproduction
# - grass → reserve assimilation


# Later:
# - fetal development
# - gestation delay
# - milk/lactation
# - male/female dimorphism
# - full temperature correction
# - aging hazard
# - exact wet/dry chemical mass conversion




##################################

# Grass provides external energy. 
# Sheep harvest grass and assimilate part of that energy into reserve. 
# Reserve is mobilized each tick. 
# A fixed κ fraction of mobilized energy pays somatic costs: maintenance, movement, and growth. 
# The remaining fraction pays maturity maintenance and either maturation or reproduction, depending on stage. 
# Structure determines body size and movement/maintenance costs. 
# Maturity determines unlocked capabilities.
# Reproduction occurs only after maturity reaches the adult threshold and the reproduction buffer is sufficiently filled.

"""
AmP sheep data
→ calibration targets

DEB theory
→ energy accounting structure

your simulator
→ simplified executable approximation



"""