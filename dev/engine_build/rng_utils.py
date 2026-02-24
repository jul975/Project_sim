
import numpy as np
import struct





# helpers 
def set_int64(x, signed=False):
    # position can be negative so use signed=True
    return int(x).to_bytes(8, 'big', signed=signed)

def set_uint8(x):
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
    float64 move_cost
    float64 reproduction_probability
    float64 reproduction_probability_change_condition
    float64 resource_regen_rate
    int64   max_harvest
    int64   world_size
    """
    buf = bytearray()
    buf.extend(struct.pack("<d", engine.config.move_cost))
    buf.extend(struct.pack("<d", engine.config.reproduction_probability))
    buf.extend(struct.pack("<d", engine.config.reproduction_probability_change_condition))
    buf.extend(struct.pack("<d", engine.config.resource_regen_rate))
    buf += set_int64(engine.config.max_harvest)
    buf += set_int64(engine.config.world_size)
    return buf
    


if __name__ == "__main__":
    pass