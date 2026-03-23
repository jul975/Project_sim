# 3. Engine Layer

## Conceptual view

This is the **state-transition executor**.

It does not define ecology itself. It defines **when** and **in what order** ecological processes occur.

That is what makes it an engine rather than just a script.

A canonical schedule is:

1. regrow resources
2. prey act
3. predators act
4. resolve births and deaths
5. collect metrics / render

## Schematic view

```
Engine.step()
    1. World regrow
    2. Prey update
    3. Predator update
    4. Commit births / deaths
    5. Collect metrics
```

## Mathematical view

$$
F = \Pi \circ Q \circ P \circ G
$$

One possible decomposition is:

- $G$ = world growth / regrowth operator
- $P$ = prey transition operator
- $Q$ = predator transition operator
- $\Pi$ = projection / commit operator for births, deaths, and metrics

So:

$$
S_{t+1} = (\Pi \circ Q \circ P \circ G)(S_t)
$$

## Key invariant

Under fixed:

- seed
- config
- update order

The same initial state should produce the same trajectory.

---