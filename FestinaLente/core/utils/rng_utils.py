
import numpy as np
import struct





# helpers 
def set_int64(x, signed=False) -> bytes:
    # position can be negative so use signed=True
    return int(x).to_bytes(8, 'big', signed=signed)

def set_int64_pair(x, y, signed=False) -> bytes:
    return set_int64(x, signed=signed) + set_int64(y, signed=signed)

def set_uint8(x) -> bytes:
    return int(x).to_bytes(1, 'big', signed=False)


def reconstruct_rng(bit_gen_state : dict) -> np.random.Generator:
    '''bit_generator.state => rng reconstruction.'''
    # bit_gent_state is a dictionary with the following keys: 
    # {'bit_generator': 'PCG64', 'state': {'state': 12345678901234567890, 'inc': 10987654321098765432}, 'has_uint32': 0, 'uinteger': 0}
    #
    # ==> need to break the logic down for understanding.
    #
    # PCG64 is the default bit generator for np.random.default_rng()
    # look to notes for further description of state.

    bit_generator = np.random.PCG64()
    bit_generator.state = bit_gen_state

    # return rng
    return np.random.default_rng(bit_generator)




def encode_string(s: str) -> bytes:
    b = s.encode("utf-8")
    return set_int64(len(b)) + b

def set_uint128(x: int) -> bytes:
    return int(x).to_bytes(16, 'big', signed=False)

def serialize_rng_state(rng):
    state = rng.bit_generator.state
    buf = bytearray()

    buf += encode_string(state["bit_generator"])
    buf += set_uint128(state["state"]["state"])
    buf += set_uint128(state["state"]["inc"])
    buf += set_int64(state["has_uint32"], signed=True)
    buf += set_int64(state["uinteger"], signed=False)

    return buf
    
    
    

def serialize_array(arr) -> bytes:
    arr = arr.astype(np.int64, copy=False)
    flat = arr.ravel(order="C")

    buf = bytearray()
    buf += set_int64(len(flat))
    buf += flat.tobytes(order="C")

    return buf

def serialize_spawn_key(spawn_key: tuple[int, ...]) -> bytes:
    """
    Canonical encoding of a SeedSequence spawn_key (tuple of ints).

    Layout:
        int64 L
        int64 spawn_key[0]
        ...
        int64 spawn_key[L-1]
    """
    buf = bytearray()
    buf += set_int64(len(spawn_key), signed=False)
    for k in spawn_key:
        buf += set_int64(k, signed=True)
    return bytes(buf)

def serialize_rule_environment(engine) -> bytes:
    """
    
    float64 reproduction_probability
    float64 reproduction_probability_change_condition
    int64 resource_regen_rate

    int64   movement_cost
    int64   reproduction_threshold
    int64   reproduction_cost

    int64   max_harvest
    int64   world_size
    """
    buf = bytearray()
    buf.extend(struct.pack("<d", engine.reproduction_probability))

    buf += set_int64(engine.resource_params.regen_rate)
    # energy params
    buf += set_int64(engine.energy_params.movement_cost)
    buf += set_int64(engine.energy_params.reproduction_threshold)
    buf += set_int64(engine.energy_params.reproduction_cost)




    buf += set_int64(engine.resource_params.max_resource_level)
    buf += set_int64(engine.world_params.world_width * engine.world_params.world_height)
    return buf
    


if __name__ == "__main__":
    pass