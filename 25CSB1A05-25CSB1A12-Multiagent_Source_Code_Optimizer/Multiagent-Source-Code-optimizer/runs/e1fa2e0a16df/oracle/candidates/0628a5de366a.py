from bisect import bisect_right


def two_sum(nums, target):
    pos = {}
    for idx, v in enumerate(nums):
        pos.setdefault(v, []).append(idx)
    for i, v in enumerate(nums):
        lst = pos.get(target - v)
        if lst:
            k = bisect_right(lst, i)
            if k < len(lst):
                return [i, lst[k]]
    return []
