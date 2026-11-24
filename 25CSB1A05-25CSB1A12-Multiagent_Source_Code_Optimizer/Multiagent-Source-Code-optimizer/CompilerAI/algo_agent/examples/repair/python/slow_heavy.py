def count_pairs_mod(n: int) -> int:
    limit = max(0, min(n, 350))
    total = 0
    for i in range(limit):
        for j in range(limit):
            if (i * j) % 7 == 1:
                total += 1
    return total
