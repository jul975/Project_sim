from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from ..domains.agent import Agent



@dataclass
class Position:
    x: int
    y: int


@dataclass
class OccupancyIndex:
    """ OccupancyIndex: only owns the spatial lookup of agents, should be updated at the end of each tick. 
    NOTE: this is a critical component regarding percervance of determinism, 
    OccupancyIndex gets created by iterating over sorted agents.id, insertion order is preserved during the tick, and iteration order is deterministic as it relies on the underlying dict order, which is deterministic in python 3.7+."""
    cells: dict[Position, list["Agent"]] = field(default_factory=dict)

    def clear(self) -> None:
        self.cells.clear()

    def add(self, agent: "Agent") -> None:
        self.cells.setdefault(agent.position, []).append(agent)

    

    def rebuild(self, agents: dict[int, "Agent"]) -> None:
        self.clear()
        for agent in agents.values():
            if agent.alive:
                self.add(agent)

    def agents_at(self, position: Position) -> list["Agent"]:
        return self.cells.get(position, [])

    def occupied_items(self) -> Iterable[Position, list["Agent"]]:
        return self.cells.items()

    def count_at(self, position: Position) -> int:
        return len(self.cells.get(position, ()))
    
    @classmethod
    def build_from_agents(cls, agents: dict[int, "Agent"]) -> tuple["OccupancyIndex", list[int]]:
        """ build_from_agents(agents):
        builds an OccupancyIndex from a given dict of agents, and returns a DeathBucket of dead agents. 
        """
        # NOTE: insertion order of dict is preserved, need verification and formalization
            # need to assure deterministic order of agent processing, while avoiding overhead of sorting by id at each tick.
            # should be stable as is but still relying on dict order for determinism is a bit concerning/bug risk
            # idea, counter? (easy to overdo it) or just be careful and document
        index = cls()
        dead_agents_ids = []

        for agent in agents.values():
            if agent.alive:
                index.add(agent)
            else:
                dead_agents_ids.append(agent.id)
        
        return index, dead_agents_ids
    

if __name__ == "__main__":
    pass