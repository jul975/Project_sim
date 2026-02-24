from dataclasses import dataclass

@dataclass(frozen=True)
class SimulationConfig:
    
    
    # population
    max_agent_count: int = 1000
    initial_agent_count: int = 10

    # world config
    world_size: int = 200
    
    """
    Number of discrete spatial cells.

    Valid positions satisfy:
        0 <= position < world_size

    The upper bound is EXCLUSIVE.

    Toroidal wrapping is implemented via modulo:
        position = position % world_size
    """

    
    

    # energy dynamics
    move_cost: int = 1
    energy_init_range: tuple[int, int] = (30, 60)

    # reproduction
    reproduction_probability: float = 0.01
    reproduction_probability_change_condition: float = 0.02 # NOTE: for testing
    reproduction_cost: int = 0
    reproduction_threshold: int = 0

    # resource (future phase)
    resource_regen_rate: int = 2

    max_harvest: int = 1
    max_resource_level: int = 80

    
    