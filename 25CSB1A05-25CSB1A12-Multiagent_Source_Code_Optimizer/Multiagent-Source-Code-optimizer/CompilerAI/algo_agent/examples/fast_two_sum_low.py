def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for j, v in enumerate(nums):
        if target - v in seen:
            return [seen[target - v], j]
        seen[v] = j
    return []