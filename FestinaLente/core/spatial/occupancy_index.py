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
    """OccupancyIndex: spatial lookup structure mapping positions to ordered agent lists.
    
    **Part of the State Freezing pattern** — see DETERMINISM.md "World / OccupancyIndex / 
    TransitionContext Contract".
    
    **Built once at start of movement phase, frozen for rest of tick.**
    
    Responsibilities:
    - Store agents by position (x, y) → [agent_0, agent_1, ...]
    - Maintain insertion order within each cell for deterministic harvest distribution
    - Provide iteration over occupied cells
    
    Local ordering contract:
    - Agents within a cell are stored in a list (encounter order)
    - Cells are iterated in order of first occupancy during movement
    - Harvest remainder is allocated to first r agents in local list
    
    See DETERMINISM.md "Explicit Local Ordering Guarantee" for full specification.
    """
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
        """Build occupancy index from agent dict and return dead agent IDs.
        
        **Determinism-critical**: Iterates agents.values() which preserves insertion order 
        (Python 3.7+ dict guarantee). This ensures encounter order is consistent across runs.
        
        See DETERMINISM.md "Explicit Local Ordering Guarantee" for the three-layer ordering
        contract and why re-sorting would break determinism.
        """
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
