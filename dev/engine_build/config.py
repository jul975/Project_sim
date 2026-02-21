from dataclasses import dataclass

@dataclass(frozen=True)
class SimulationConfig:
    # population
    max_agent_count: int = 200
    initial_agent_count: int = 10

    # space
    world_size: int = 30

    # agent spawn ranges 
    min_location: int = 0
    max_location: int = 30
    spawn_range: tuple[int, int] = (min_location, max_location)

    # energy dynamics
    move_cost: int = 1
    energy_init_min: int = 20
    energy_init_max: int = 40
    energy_init_range: tuple[int, int] = (energy_init_min, energy_init_max)

    # reproduction
    reproduction_probability: float = 0.5
    reproduction_probability_change_condition: float = 0.02 # NOTE: for testing
    reproduction_cost: int = 0
    reproduction_threshold: int = 0

    # resource (future phase)
    resource_regen_rate: int = 0
    resource_cap: int = 0
    harvest_max: int = 0