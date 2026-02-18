
import numpy as np




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



if __name__ == "__main__":
    pass