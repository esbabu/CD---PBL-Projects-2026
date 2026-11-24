def running_totals(nums: list[int]):
    acc = 0
    for x in nums:
        acc += x
        yield acc
