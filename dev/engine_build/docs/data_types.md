


## numpy.random.SeedSequence

    ### class numpy.random.SeedSequence(entropy=None, *, spawn_key=(), pool_size=4, n_children_spawned=0)

    SeedSequence mixes sources of entropy in a reproducible way to set the initial state for independent and very probably non-overlapping BitGenerators.

    Once the SeedSequence is instantiated, you can call the generate_state method to get an appropriately sized seed. Calling spawn(n) will create n SeedSequences that can be used to seed independent BitGenerators, i.e. for different threads.

    ### Parameters:
    
    - entropy:
                {None, int, sequence[int]}, optional
                
                The entropy for creating a SeedSequence. All integer values must be non-negative.

    - spawn_key:
                {(), sequence[int]}, optional
                                
                An additional source of entropy based on the position of this SeedSequence in the tree of such objects created with the SeedSequence.spawn method. Typically, only SeedSequence.spawn will set this, and users will not.

    - pool_size: 
                {int}, optional

                Size of the pooled entropy to store. Default is 4 to give a 128-bit entropy pool. 8 (for 256 bits) is another reasonable choice if working with larger PRNGs, but there is very little to be gained by selecting another value.

    - n_children_spawned:

                {int}, optional

                The number of children already spawned. Only pass this if reconstructing a SeedSequence from a serialized form.

Notes

Best practice for achieving reproducible bit streams is to use the default None for the initial entropy, and then use SeedSequence.entropy to log/pickle the entropy for reproducibility:

sq1 = np.random.SeedSequence()
sq1.entropy
243799254704924441050048792905230269161  # random
sq2 = np.random.SeedSequence(sq1.entropy)
np.all(sq1.generate_state(10) == sq2.generate_state(10))
True
Attributes
:
entropy
n_children_spawned
pool
pool_size
spawn_key
state
Methods

generate_state(n_words[, dtype])

Return the requested number of words for PRNG seeding.

spawn(n_children)

Spawn a number of child SeedSequence s by extending the spawn_key.
------------------------------
# NumPy RNG Data Types

## `numpy.random.SeedSequence` (DS)

```python
SeedSequence(
    entropy: None | int | Sequence[int] = None,
    *,
    spawn_key: tuple[int, ...] = (),
    pool_size: int = 4,
    n_children_spawned: int = 0,
)
```

Purpose:
- Mixes entropy deterministically.
- Produces independent child seed sequences with `spawn(n)`.
- Generates seed words for bit generators with `generate_state(...)`.

State structure (`seed_seq.state`):

```python
{
    "entropy": int | tuple[int, ...],
    "spawn_key": tuple[int, ...],
    "pool_size": int,
    "n_children_spawned": int,
}
```

Example:

```python
import numpy as np

seed_seq = np.random.SeedSequence(12345)
print(seed_seq.state)
# {
#   'entropy': 12345,
#   'spawn_key': (),
#   'pool_size': 4,
#   'n_children_spawned': 0
# }
```

---

## NumPy RNG (`numpy.random.Generator`) (DS)

```python
Generator(bit_generator: BitGenerator)
```

Most common constructor:

```python
rng = np.random.default_rng(seed_or_seedsequence)
```

Structure:
- `rng`: high-level random API (`random`, `integers`, `choice`, etc.).
- `rng.bit_generator`: low-level PRNG engine (`PCG64` by default).
- `rng.bit_generator.state`: serializable engine state dictionary.

Example state (default `PCG64`):

```python
{
    "bit_generator": "PCG64",
    "state": {
        "state": int,
        "inc": int
    },
    "has_uint32": int,   # 0 or 1
    "uinteger": int
}
```

Example:

```python
import numpy as np

seed_seq = np.random.SeedSequence(12345)
rng = np.random.default_rng(seed_seq)
print(type(rng))                 # numpy.random._generator.Generator
print(type(rng.bit_generator))   # numpy.random._pcg64.PCG64
print(rng.bit_generator.state)
```

