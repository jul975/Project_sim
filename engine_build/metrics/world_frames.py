
import numpy as np
from engine_build.core.engine import Engine


class WorldFrames:

    def __init__(self, capture_every: int = 10):
        self.capture_every = capture_every

        self.resources = []
        self.density = []
        self.population = []
        self.ticks = []

        self.agent_positions = []
        self.run_agent_energies = []

    def capture(self, engine : Engine):

        world = engine.world
        height, width = world.resources.shape
        agent_energies = []
        

        density = np.zeros((height, width))

        for agent in engine.agents.values():
            x, y = agent.position
            density[y, x] += 1
            agent_energies.append(agent.energy_level)


        self.resources.append(world.resources.copy())
        self.density.append(density)
        self.population.append(len(engine.agents))
        self.ticks.append(world.tick)
        self.agent_positions.append([agent.position for agent in engine.agents.values()])
        self.run_agent_energies.append(agent_energies)
