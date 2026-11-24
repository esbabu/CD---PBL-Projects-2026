async def async_unique_count(nums: list[int]) -> int:
    seen = []
    for x in nums:
        if x not in seen:
            seen.append(x)
    return len(seen)
