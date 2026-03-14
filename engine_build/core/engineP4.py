import numpy as np
import hashlib

from .state_schema import get_state_bytes

from .snapshots import engine_to_snapshot, engine_from_snapshot

from .agent import Agent
from .world import World


from .step_results import CommitReport, StepReport, WorldView

from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiled import EnergyParams, ReproductionParams, ResourceParams, LandscapeParams, PopulationParams, WorldParams

from .transitions import TransitionContext, movement_phase, interaction_phase, biology_phase


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .snapshots import EngineSnapshot



class Engine:
    def __init__(self, seed_seq : np.random.SeedSequence , config : CompiledRegime ,change_condition=False) -> None:


        self.master_ss = seed_seq
        world_seed: np.random.SeedSequence = self.master_ss.spawn(1)[0]

        self.collect_world_view = False

        self.config : CompiledRegime = config
        
        self.energy_params : EnergyParams = self.config.energy_params  


        self.reproduction_probability : float = self.config.reproduction_params.probability if not change_condition else self.config.reproduction_params.probability_change_condition
        
        
        self.resource_params : ResourceParams = self.config.resource_params
        self.landscape_params : LandscapeParams = self.config.landscape_params
        self.population_params : PopulationParams = self.config.population_params
        self.world_params : WorldParams = self.config.world_params

        self.max_agent_count = self.population_params.max_agent_count
        self.next_agent_id = self.population_params.initial_agent_count
        self.max_age = self.population_params.max_age
        
        self.world = World( world_seed, self.config ,change_condition)
        
        self.agents : dict[int, Agent] = self.initialize_state(self.next_agent_id) 

        self._assert_invariants()


        
        
    def _assert_invariants(self) -> None:
        """Validate global engine state."""

        # population constraint
        assert len(self.agents) <= self.max_agent_count

        # ID allocation safety
        assert self.next_agent_id > max(self.agents, default=-1)

        # agent integrity
        for agent_id, agent in self.agents.items():

            # ID consistency
            assert agent_id == agent.id

            # spatial bounds
            x, y = agent.position
            assert 0 <= x < self.world_params.world_width
            assert 0 <= y < self.world_params.world_height

            # biological constraints
            assert agent.age >= 0
            assert agent.age <= self.max_age
            assert agent.energy_level >= 0 or not agent.alive

        # world compatibility
        assert self.world.world_width == self.world_params.world_width
        assert self.world.world_height == self.world_params.world_height

        # id allocation corruption
        assert all(agent.id < self.next_agent_id for agent in self.agents.values())



    def initialize_state(self, agent_count) -> dict[np.int64, Agent]:
        """ creates initial agent population. """
        agent_seeds = self.master_ss.spawn(agent_count)

        return {i : Agent(self, i, agent_seeds[i]) for i in range(agent_count)}
    


    # NOTE: temp 
    def check_initial_population_spread(self) -> None:
        """ checks initial population spread. => not wired yet, needs to check if it's necessary. """
        density = np.zeros((self.world_params.world_height, self.world_params.world_width))

        for agent in self.agents.values():
            x, y = agent.position
            density[y, x] += 1
    

    
    def create_new_agent(self, parent_agent : Agent) -> None:
        """ creates new agent from parent_agent. """
        

        child_seed = self.get_child_seed(parent_agent)
        
        self.agents[self.next_agent_id] = Agent( self , self.next_agent_id , child_seed)
        self.agents[self.next_agent_id].position = parent_agent.position
        self.next_agent_id += 1


    def get_child_seed(self, parent_agent : Agent) -> np.random.SeedSequence:
        """ gets child seed from parent_agent. """
        return parent_agent.reproduce()


    def get_agent_count(self) -> np.int64:
        """ returns current agent count. """
        return len(self.agents)

    def __eq__(self, other) -> bool:
        """ compares two engine objects. """
        if not isinstance(other, Engine):
            return NotImplemented
        
        return self.get_state_hash() == other.get_state_hash()


    def step(self) -> StepReport:
        """ restructuring step method in order to evaluate agents for death and birth together. 
            After evaluation, available capacity gets calculated to avoid undershoot of agent capacity."""
        
        
        context = TransitionContext()

        movement_report = movement_phase(self.agents, context)

        interaction_report = interaction_phase(context, self.world)

        biology_report = biology_phase(context)

        commit_report = self.commit_phase(context)

        if self.collect_world_view:
            world_view = self.build_world_view()
        else:
            world_view = None

        step_report = StepReport(
            tick = self.world.tick,
            movement_report = movement_report,
            interaction_report = interaction_report,
            biology_report = biology_report,
            commit_report = commit_report,
            world_view = world_view
        )

        ## end of current tick, go to the next tick
        self.world.tick += 1
        return step_report
                
        
        




    def commit_phase(self, context : TransitionContext) -> CommitReport:
        """ commits pending births and deaths to the engine. """
        pending_deaths_by_cause = context.pending_deaths_by_cause
        reproducing_agents = context.reproducing_agents


        deaths_this_tick = sum(death_bucket.count for death_bucket in pending_deaths_by_cause.values())
        effective_population = len(self.agents) - deaths_this_tick 
        available_capacity = self.max_agent_count - effective_population
        reproducers_to_commit = reproducing_agents[:available_capacity]

        # D
        for death_bucket in pending_deaths_by_cause.values():
            for agent_id in death_bucket.agents_ids:
                assert agent_id in self.agents
                del self.agents[agent_id]
                
        # B
        for parent_agent in reproducers_to_commit:
            self.create_new_agent(parent_agent)

        # world state update 
        self.world.regrow_resources()
        

        # NOTE: temp solution for positional metrics.
        
        """if __debug__:
            self._assert_invariants()"""

        return CommitReport(
            population = len(self.agents),
            births_count = len(reproducers_to_commit),
            deaths_count = deaths_this_tick,
        )



    def build_world_view(self) -> WorldView:
        """ builds world view. """

        sorted_agents = sorted(self.agents.values(), key=lambda agent: agent.id)



        positions = np.fromiter(
            (coord for agent in sorted_agents for coord in agent.position),
            dtype=np.int32,
            count=len(sorted_agents) * 2
        ).reshape(len(sorted_agents), 2)

        energies = np.fromiter(
            (agent.energy_level for agent in sorted_agents),
            dtype=np.int16,
            count=len(sorted_agents)
        )

        resources = self.world.resources.copy()

        return WorldView(
            positions=positions,
            energies=energies,
            resources=resources
        )
    


    def get_state_hash(self) -> str:
        """ returns state hash. """
        return hashlib.sha256(get_state_bytes(self)).hexdigest()
    


    def get_snapshot(self) -> "EngineSnapshot":
        """ returns engine snapshot. """
        return engine_to_snapshot(self)

    @classmethod
    def from_snapshot(cls : type["Engine"], snapshot : "EngineSnapshot") -> "Engine":
        """ create engine from snapshot. """
        return engine_from_snapshot(cls, snapshot)
        


if __name__ == "__main__":
    pass










