def sum_down(n: int) -> int:
    if n <= 0:
        return 0
    return n + sum_down(n - 1)
