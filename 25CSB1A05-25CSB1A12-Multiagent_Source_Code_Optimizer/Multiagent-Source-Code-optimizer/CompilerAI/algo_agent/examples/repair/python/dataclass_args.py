from dataclasses import dataclass


@dataclass
class Item:
    key: str
    value: int


def sum_matching(items: list[Item], target_key: str) -> int:
    total = 0
    for it in items:
        if it.key == target_key:
            total += it.value
    return total
