




# helpers 
def set_int64(x, signed=False):
    # position can be negative so use signed=True
    return int(x).to_bytes(8, 'big', signed=signed)

def set_uint8(x):
    return int(x).to_bytes(1, 'big', signed=False)





if __name__ == "__main__":
    pass