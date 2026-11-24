import numpy as np


def pairwise_sum(arr: list[float]) -> float:
    a = np.array(arr, dtype=float)
    total = 0.0
    for i in range(len(a)):
        total += float(a[i])
    return total
