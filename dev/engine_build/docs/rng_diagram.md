```SS_root
├─ SS_world  ──> G_world  (fertility/resources/regime events)
└─ SS_agents
   ├─ SS_0 ──> spawn(3) ──> (SS_0^m, SS_0^r, SS_0^e)
   │            |           |        |        |
   │            v           v        v        v
   │           G_0^m       G_0^r    G_0^e   (energy init only)
   │
   ├─ SS_1 ──> spawn(3) ──> (G_1^m, G_1^r, G_1^e)
   │
   └─ ...


---

```Agent i lineage:
SS_i
├─ child 0: SS_child(i,0)  (spawn_key = parent_spawn_key + (0,))
├─ child 1: SS_child(i,1)  (spawn_key = parent_spawn_key + (1,))
└─ child 2: SS_child(i,2)  ...

Each child SeedSequence then spawns its own substreams:
SS_child(i,k) -> spawn(3) -> (G_child^m, G_child^r, G_child^e)