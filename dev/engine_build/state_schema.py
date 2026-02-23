


from .rng_utils import set_int64, set_uint8


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

SCHEMA_VERSION = 1



def get_state_bytes(engine) -> bytes:
    if SCHEMA_VERSION == 1:
        return schema_v1(engine)
    else:
        raise NotImplementedError(f"Schema version {SCHEMA_VERSION} not implemented")



"""
SCHEMA_VERSION = 2

Engine:
  tick
  next_agent_id

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
  alive
  agent_spawn_count
  agent_entropy
  agent_spawn_key
  move_rng_state
  repro_rng_state
  energy_rng_state


"""

def schema_v2(engine) -> bytes:
    # tick, agent_count, agent: id, position, energy, alive
    buffer = bytearray()

    # schema version => 
    buffer += set_int64(SCHEMA_VERSION)

    # Engine  
    buffer += set_int64(engine.world.tick)
    buffer += set_int64(len(engine.agents))

    # World






    

























def schema_v1(engine) -> bytes:
    # tick, agent_count, agent: id, position, energy, alive
    buffer = bytearray()

    # schema version => 
    buffer += set_int64(SCHEMA_VERSION)

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