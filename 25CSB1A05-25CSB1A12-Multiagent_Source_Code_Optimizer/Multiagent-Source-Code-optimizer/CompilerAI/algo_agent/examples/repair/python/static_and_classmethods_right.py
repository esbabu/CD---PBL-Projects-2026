class ArrayTools:
    scale: int = 1

    @staticmethod
    def has_dup(items: list[int]) -> bool:
        return len(set(items)) < len(items)

    @classmethod
    def scaled_sum(cls, items: list[int]) -> int:
        return sum(items) * cls.scale
