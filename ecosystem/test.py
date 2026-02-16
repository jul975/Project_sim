import numpy as np





rng = np.random.default_rng(123)
print(rng)
a = rng.integers(1, 10, 10)
b = rng.integers(0, 10, 10)

print(a)
print(b)
print(type(b))
for i in a:
    print(i)
    print(type(i))