


from .rng_utils import set_int64, set_uint8, serialize_rng_state, serialize_array, serialize_spawn_key, serialize_rule_environment



"""
State Schema v1:
    basic first layout of state. 
    should be used to set up get_state_bytes() for "canonical serialization"
    this should feed the buffer feeding the get_hash() function.

State Schema v1
---------------
tick: int64
agent_count: uint64
agent:
    id: int64
    position: int64
    energy: int64
    alive: uint8
    
"""

""" canonical serialization of state. """
""" Right now:  
        - S(t) = 
                {
                world state: tick, agent_count
                + 
                n_agents * (agent state: id, position, energy, alive)
                }
"""

SCHEMA_VERSION = 2



def get_state_bytes(engine) -> bytes:
    if SCHEMA_VERSION == 1:
        return _schema_v1(engine)
    elif SCHEMA_VERSION == 2:
        return _schema_v2(engine)
    else:
        raise NotImplementedError(f"Schema version {SCHEMA_VERSION} not implemented")



"""
SCHEMA_VERSION = 2

Engine:
  tick
  next_agent_id
  max_age

World:
  world_size
  max_harvest
  resource_regen_rate
  resources[]
  fertility[]
  rng_world_state

Agents (sorted by id):
  id
  position
  energy
  age
  alive
  agent_spawn_count
  agent_entropy
  agent_spawn_key
  move_rng_state
  repro_rng_state
  energy_rng_state


"""

def _schema_v2(engine) -> bytes:
    # tick, agent_count, agent: id, position, energy, alive
    buffer = bytearray()

    # schema version => 
    buffer += set_int64(2)
    # change_condition
    buffer += set_uint8(int(engine.world.change_condition))

    # Engine  
    buffer += set_int64(engine.world.tick)
    buffer += set_int64(len(engine.agents))
    buffer += set_int64(engine.next_agent_id)
    buffer += set_int64(engine.max_age)

    # rule environment
    buffer += serialize_rule_environment(engine)

    # World
    buffer += set_int64(engine.world.world_size)
    buffer += set_int64(engine.world.max_harvest)
    buffer += set_int64(engine.world.resource_regen_rate)

    # resource and fertility array's
    buffer += serialize_array(engine.world.resources)
    buffer += serialize_array(engine.world.fertility)
    

    # rng_world
    buffer += serialize_rng_state(engine.world.rng_world)



    # Agents
    for agent_id, agent in sorted(engine.agents.items()):

        buffer += set_int64(agent.id)
        # position can be negative so use signed=True
        buffer += set_int64(agent.position, signed=True)
        buffer += set_int64(agent.energy_level)
        buffer += set_int64(agent.age)
        buffer += set_uint8(int(agent.alive))
        buffer += set_int64(agent.agent_spawn_count)
        buffer += set_int64(agent.agent_entropy)
        buffer += serialize_spawn_key(agent.agent_spawn_key)
        buffer += serialize_rng_state(agent.move_rng)
        buffer += serialize_rng_state(agent.repro_rng)
        buffer += serialize_rng_state(agent.energy_rng)



    return bytes(buffer)



























def _schema_v1(engine) -> bytes:
    # tick, agent_count, agent: id, position, energy, alive
    buffer = bytearray()

    # schema version => 
    buffer += set_int64(1)

    # world state  
    buffer += set_int64(engine.world.tick)
    buffer += set_int64(len(engine.agents))
    # agent state


# NOTE : SUGGESTION BY CHATGPT => NOT IMPLEMENTED RN TO SEE IF AND WHERE NOT IMPLEMENTING, CREATES
#                                 FUTURE DEVIATIONS.
#                           
#                                 EXPECTING A TUPLE ALLOCATION ERROR.

#                                 => for agent in (self.agents[k] for k in sorted(self.agents)):

    for agent_id, agent in sorted(engine.agents.items()):
        buffer += set_int64(agent.id)
        # position can be negative so use signed=True
        buffer += set_int64(agent.position, signed=True)
        buffer += set_int64(agent.energy_level)
        buffer += set_uint8(int(agent.alive))


    return bytes(buffer)