import numpy as np

transfer = np.matrix([[0, 1, 0], [0.5, 0, 0.5], [1, 0, 0]])
pai = transfer ** 100
print(pai)