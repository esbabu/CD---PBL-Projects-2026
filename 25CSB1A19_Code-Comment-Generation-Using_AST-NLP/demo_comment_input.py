def add(a, b):
    return a + b


def process_numbers(values):
    total = 0
    for v in values:
        if v > 0:
            total += v
    return total
