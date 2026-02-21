from dataclasses import dataclass

@dataclass(frozen=True)
class SimulationConfig:
    # population
    max_agent_count: int = 200
    initial_agent_count: int = 10

    # space
    world_size: int = 30

    # energy dynamics
    move_cost: int = 1
    energy_init_min: int = 20
    energy_init_max: int = 40

    # reproduction
    reproduction_probability: float = 0.01
    reproduction_probability_change_condition: float = 0.02 # NOTE: for testing
    reproduction_cost: int = 0
    reproduction_threshold: int = 0

    # resource (future phase)
    resource_regen_rate: int = 0
    resource_cap: int = 0
    harvest_max: int = 0