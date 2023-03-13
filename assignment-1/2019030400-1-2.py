import numpy as np

#A
m = np.arange(2, 27)
print(m)

#B
m = m.reshape(5, 5)
print(m)

#C
m[:, 0] = 0
print(m)

#D
m = m @ m
print(m)

#E
v = m[0]
result = v @ v
magnitude = np.sqrt(result)
print(magnitude)

