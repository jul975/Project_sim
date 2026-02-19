


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

