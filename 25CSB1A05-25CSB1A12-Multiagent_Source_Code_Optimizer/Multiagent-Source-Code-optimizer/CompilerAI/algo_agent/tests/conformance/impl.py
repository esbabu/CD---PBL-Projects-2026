import os
import sys


def add(a: int, b: int) -> int:
    return a + b


def reverse_list(xs: list[int]) -> list[int]:
    return list(reversed(xs))


def raise_on_negative(x: int) -> int:
    if x < 0:
        raise ValueError("negative")
    return x


def mutates_argument(xs: list[int]) -> int:
    xs.append(99)
    return len(xs)


def prints_text(s: str) -> str:
    print(s)
    return s


def infinite_loop(x: int) -> int:
    while True:
        x += 1


def crashes_hard(x: int) -> int:
    os._exit(139)


def returns_special_values(x: int):
    return [float("nan"), -0.0, None, 10 ** 30]
