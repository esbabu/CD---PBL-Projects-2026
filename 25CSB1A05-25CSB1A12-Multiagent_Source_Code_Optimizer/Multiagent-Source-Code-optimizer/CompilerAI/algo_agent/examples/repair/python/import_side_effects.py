print("module loaded!")
CONFIG = {"factor": 2}


def transform(nums: list[int]) -> list[int]:
    out = []
    for x in nums:
        out.append(x * CONFIG["factor"])
    return out


if __name__ == "__main__":
    print(transform([1, 2, 3]))
