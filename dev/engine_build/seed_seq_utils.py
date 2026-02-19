import numpy as np

"""
If you clone mid-stream and do not restore n_children_spawned, then:

Future .spawn() calls will reuse old spawn keys.

That destroys lineage determinism.

So:

✔ entropy must be restored
✔ spawn_key must be restored
✔ n_children_spawned must be restored

But numpy does NOT expose a constructor parameter for n_children_spawned."""





def get_seed_seq_dict(seed_seq : np.random.SeedSequence) -> dict:
    return {
        "entropy" : seed_seq.entropy,
        "spawn_key" : seed_seq.spawn_key,
        "pool_size" : seed_seq.pool_size,
        
    }

def reconstruct_seed_seq(seed_seq_dict : dict, spawn_count : np.int64) -> np.random.SeedSequence:
    ''' manual n_children_spawned reconstruction, no native support found rn? 
        need to be cleared up. '''
    
    ss = np.random.SeedSequence(
                                entropy=seed_seq_dict["entropy"],

                                spawn_key=tuple(seed_seq_dict["spawn_key"]) + (spawn_count,),

                                pool_size=seed_seq_dict["pool_size"]
    )
    
    return ss