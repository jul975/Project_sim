

from FestinaLente.regimes.spec import LandscapeSpec, ResourceSpec


WORLD_REGISTRY = {
    "abundant": RegimeSpec(
        resources_spec=ResourceSpec(regen_fraction=0.1),
        landscape_spec=LandscapeSpec(correlation=0.055, contrast=1.0, floor=0.0),
    ),
}