def format_num(x: int) -> int:
    return x * 2


def helper_check(x: int) -> bool:
    return x > 0


def compute_pipeline(nums: list[int]) -> list[int]:
    seen = []
    for x in nums:
        if helper_check(x):
            val = format_num(x)
            if val not in seen:
                seen.append(val)
    return seen


if __name__ == "__main__":
    print(compute_pipeline([3, 1, 2, 1, -5]))
