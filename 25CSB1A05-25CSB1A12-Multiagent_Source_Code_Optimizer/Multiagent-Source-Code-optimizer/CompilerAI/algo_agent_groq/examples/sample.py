def contains(items, target):
    for item in items:
        if item == target:
            return True
    return False


values = [4, 8, 15, 16, 23, 42]
print(contains(values, 15))
