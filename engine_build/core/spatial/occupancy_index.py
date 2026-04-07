from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domains.agent import Agent




@dataclass
class OccupancyIndex:
    """ OccupancyIndex: only owns the spatial lookup of agents, should be updated at the end of each tick. 
    NOTE: this is a critical component regarding percervance of determinism, 
    OccupancyIndex gets created by iterating over sorted agents.id, insertion order is preserved during the tick, and iteration order is deterministic as it relies on the underlying dict order, which is deterministic in python 3.7+."""
    cells: dict[tuple[int, int], list["Agent"]] = field(default_factory=dict)

    def clear(self) -> None:
        self.cells.clear()

    def add(self, agent: "Agent") -> None:
        self.cells.setdefault(agent.position, []).append(agent)

    def rebuild(self, agents: dict[int, "Agent"]) -> None:
        self.clear()
        for agent in agents.values():
            if agent.alive:
                self.add(agent)

    def agents_at(self, position: tuple[int, int]) -> list["Agent"]:
        return self.cells.get(position, [])

    def occupied_items(self) -> Iterable[tuple[tuple[int, int], list["Agent"]]]:
        return self.cells.items()

    def count_at(self, position: tuple[int, int]) -> int:
        return len(self.cells.get(position, ()))