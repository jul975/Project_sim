

from engine_build.core.seed_seq_utils import get_seed_seq_dict
from dataclasses import asdict, dataclass
from engine_build.regimes.compiled import CompiledRegime, PopulationParams, ReproductionParams
from engine_build.core.seed_seq_utils import reconstruct_seed_seq
from engine_build.core.rng_utils import reconstruct_rng


from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from engine_build.core.engineP4 import Engine
    from engine_build.core.agent import Agent

    from engine_build.core.world import World

# NOTE: frozen dataclass do not make internal dicts immutable!!! => gonna need nested dataclasses

@dataclass(frozen=True)
class AgentSnapshot:
    id : int
    agent_spawn_count : int
    position : tuple[int, int]
    energy_level : int
    alive : bool

    age : int

    agent_seed : dict

    move_rng : dict
    repro_rng : dict
    energy_rng : dict


@dataclass(frozen=True)
class WorldSnapshot:
    tick : int
    change_condition : bool

    world_width : int
    world_height : int

    rng_world : dict

    resources : np.ndarray
    fertility : np.ndarray
    max_harvest : int
    resource_regen_rate : int


@dataclass(frozen=True)
class EngineSnapshot:
    master_ss : dict
    next_agent_id : int
    config : dict
    reproduction_probability : float
    
    max_age : int
    max_agent_count : int
    
    world : WorldSnapshot
    agents : dict[int, AgentSnapshot]


def snapshots_equal(a: EngineSnapshot, b: EngineSnapshot) -> bool:
    """ compares two engine snapshots. """
    if a.master_ss != b.master_ss:
        return False
    if a.next_agent_id != b.next_agent_id:
        return False
    if a.config != b.config:
        return False
    if a.max_age != b.max_age:
        return False
    if a.max_agent_count != b.max_agent_count:
        return False
    if a.world.tick != b.world.tick:
        return False
    if a.world.change_condition != b.world.change_condition:
        return False
    if not np.array_equal(a.world.resources, b.world.resources):
        return False
    if not np.array_equal(a.world.fertility, b.world.fertility):
        return False
    if a.agents.keys() != b.agents.keys():
        return False
    return True
    

def _get_agent_snapshot(agent : "Agent") -> AgentSnapshot:
    """ returns agent snapshot. """
    
    return AgentSnapshot(
        id = agent.id,
        agent_spawn_count = agent.agent_spawn_count,
        position = agent.position,
        energy_level = agent.energy_level,
        alive = agent.alive,

        age = agent.age,
        

        agent_seed = get_seed_seq_dict(agent.agent_seed),

        move_rng = agent.move_rng.bit_generator.state,
        repro_rng = agent.repro_rng.bit_generator.state,
        energy_rng = agent.energy_rng.bit_generator.state
    )
    


def _get_world_snapshot(world : "World") -> WorldSnapshot:
    # NOTE: copy arrays to avoid reference issues.
    """ returns world snapshot. """
    return WorldSnapshot(
        tick = world.tick,
        change_condition = world.change_condition,
        world_width = world.world_width,
        world_height = world.world_height,

        rng_world = world.rng_world.bit_generator.state,

        resources = world.resources.copy(),
        fertility = world.fertility.copy(),

        max_harvest = world.max_harvest,
        resource_regen_rate = world.resource_regen_rate
    )



def engine_to_snapshot(engine : "Engine") -> EngineSnapshot:
    """ returns engine snapshot. """
    # NOTE check agent sorting logic for robustness, efficiency and edge cases.
    
    master_ss = get_seed_seq_dict(engine.master_ss)
    next_agent_id = engine.next_agent_id
    config = asdict(engine.config)

    reproduction_probability = engine.reproduction_probability

    max_age = engine.max_age
    max_agent_count = engine.max_agent_count

    agents = {agent_id : _get_agent_snapshot(agent) for agent_id, agent in sorted(engine.agents.items())}
    world = _get_world_snapshot(engine.world)
    

    return EngineSnapshot(
        master_ss = master_ss,
        next_agent_id = next_agent_id,
        config = config,
        reproduction_probability = reproduction_probability,
        max_age = max_age,
        max_agent_count = max_agent_count,
        world = world,
        agents = agents
    )




def _agent_from_snapshot(agent_cls, agent_snapshot: AgentSnapshot, engine: "Engine") -> "Agent":
    agent_clone: "Agent" = object.__new__(agent_cls)

    agent_clone.engine = engine
    agent_clone.id = agent_snapshot.id
    agent_clone.age = agent_snapshot.age
    agent_clone.position = agent_snapshot.position
    agent_clone.alive = agent_snapshot.alive
    agent_clone.energy_level = agent_snapshot.energy_level

    # restore future child cursor
    agent_clone.agent_spawn_count = agent_snapshot.agent_spawn_count

    # restore exact agent identity seed
    agent_clone.agent_seed = reconstruct_seed_seq(agent_snapshot.agent_seed)

    # cache seed identity fields from the reconstructed seed
    agent_clone.agent_entropy = agent_clone.agent_seed.entropy
    agent_clone.agent_spawn_key = tuple(agent_clone.agent_seed.spawn_key)
    agent_clone.pool_size = agent_clone.agent_seed.pool_size

    assert isinstance(agent_snapshot.move_rng, dict)
    assert isinstance(agent_snapshot.repro_rng, dict)
    assert isinstance(agent_snapshot.energy_rng, dict)

    agent_clone.move_rng = reconstruct_rng(agent_snapshot.move_rng)
    agent_clone.repro_rng = reconstruct_rng(agent_snapshot.repro_rng)
    agent_clone.energy_rng = reconstruct_rng(agent_snapshot.energy_rng)

    agent_clone._assert_invariants()
    return agent_clone
    

def _world_from_snapshot(world_cls, world_snapshot : WorldSnapshot) -> "World":
    """ create world from snapshot. """

    assert isinstance(world_snapshot, WorldSnapshot), type(world_snapshot)


    clone_world : "World" = object.__new__(world_cls)

    


    clone_world.tick = world_snapshot.tick
    clone_world.rng_world = reconstruct_rng(world_snapshot.rng_world)
    
    clone_world.change_condition = world_snapshot.change_condition

    
    # these are array!! so need to avoid copy by reference.
    clone_world.resources = world_snapshot.resources.copy()
    clone_world.fertility = world_snapshot.fertility.copy()

    clone_world.resource_regen_rate = world_snapshot.resource_regen_rate
    clone_world.max_harvest = world_snapshot.max_harvest

    # derive
    clone_world.world_width = world_snapshot.world_width
    clone_world.world_height = world_snapshot.world_height


    clone_world.world_size = clone_world.world_width * clone_world.world_height

    assert clone_world.world_width > 0
    assert clone_world.world_height > 0
    assert clone_world.world_size > 0
    assert clone_world.resources.shape == (clone_world.world_height, clone_world.world_width)
    assert clone_world.fertility.shape == (clone_world.world_height, clone_world.world_width)


    clone_world._assert_invariants()

    return clone_world



def engine_from_snapshot(engine_cls, snapshot : EngineSnapshot) -> "Engine":
        from engine_build.core.world import World
        from engine_build.core.agent import Agent

        
        """ create engine from snapshot. """
        
        assert isinstance(snapshot, EngineSnapshot), type(snapshot)
        
        assert isinstance(snapshot.world, WorldSnapshot), type(snapshot.world)
        
        assert isinstance(snapshot.agents, dict), type(snapshot.agents)
        assert snapshot.next_agent_id >= 0
        assert snapshot.max_agent_count > 0
        assert snapshot.max_age > 0
        assert all(isinstance(agent, AgentSnapshot) for agent in snapshot.agents.values()), [type(agent) for agent in snapshot.agents.values()]
        
        # NOTE check next_agent_id assertion for correctness.
        assert isinstance(snapshot.next_agent_id, int)
        assert snapshot.next_agent_id > max(snapshot.agents, default=-1) 

        # shell 
        engine_clone : "Engine" = object.__new__(engine_cls)

        # config
        engine_clone.config = CompiledRegime.from_dict(snapshot.config) 
        engine_clone.energy_params = engine_clone.config.energy_params
        engine_clone.resource_params = engine_clone.config.resource_params

        engine_clone.landscape_params = engine_clone.config.landscape_params
        engine_clone.population_params = engine_clone.config.population_params
        engine_clone.world_params = engine_clone.config.world_params
        
        assert isinstance(engine_clone.config.population_params, PopulationParams)
        assert engine_clone.config.population_params.max_agent_count > 0
        assert engine_clone.config.population_params.max_age > 0
   
        
        engine_clone.reproduction_probability = snapshot.reproduction_probability
        # core Params 
        engine_clone.max_age = snapshot.max_age
        engine_clone.max_agent_count = snapshot.max_agent_count
        engine_clone.next_agent_id = snapshot.next_agent_id
        
        # rng 
        engine_clone.master_ss = reconstruct_seed_seq(snapshot.master_ss)

        # reconstruct world
        engine_clone.world = _world_from_snapshot(World, snapshot.world)

        # reconstruct agents
        assert len(snapshot.agents) <= snapshot.max_agent_count
        engine_clone.agents = {
            agent_id: _agent_from_snapshot(Agent, agent_snapshot, engine_clone)
            for agent_id, agent_snapshot in snapshot.agents.items()
            }
        
        
        # NOTE: TEMP
        engine_clone.collect_world_view = False


        # assert invariants
        engine_clone._assert_invariants()

        if __debug__:
            # NOTE: this is a very expensive operation, only do it in debug mode, or remove later on 
            #       Its meant as a test of the snapshot module itself, not the engine wrapper
            #       All reconstruction mistakes are caught IMMEDIATELY, 
            #       That's why its very powerful if used in the right context, 
            rebuild = engine_to_snapshot(engine_clone)
            assert snapshots_equal(snapshot, rebuild), "Snapshot not equal after rebuild."
    
        return engine_clone





