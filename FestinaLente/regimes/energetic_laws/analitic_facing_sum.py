
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class EnergeticSummary:
    tick: int
    population: int
    mean_reserve: float
    mean_repr_buffer: float
    mean_world_stock: float
    starvation_rate: float
    birth_count: int
    death_count: int
    world_balance_ratio: float

def summarize_energy_state(tick, agents, world, births, deaths) -> EnergeticSummary:
    live = [a for a in agents if a.alive]
    pop = len(live)
    mean_res = np.mean([a.reserve_energy for a in live]) if live else 0.0
    mean_repr = np.mean([a.repr_buffer_energy for a in live]) if live else 0.0
    mean_stock = float(world.stock_field.mean())
    starvation_rate = (
        sum(1 for a in live if a.reserve_energy <= 0.0) / pop if pop > 0 else 0.0
    )
    balance_ratio = float(world.inflow_field.sum() / max(world.harvest_field.sum(), 1e-9))

    return EnergeticSummary(
        tick=tick,
        population=pop,
        mean_reserve=mean_res,
        mean_repr_buffer=mean_repr,
        mean_world_stock=mean_stock,
        starvation_rate=starvation_rate,
        birth_count=births,
        death_count=deaths,
        world_balance_ratio=balance_ratio,
    )
