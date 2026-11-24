class ArrayTools:
    scale: int = 1

    @staticmethod
    def has_dup(items: list[int]) -> bool:
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j]:
                    return True
        return False

    @classmethod
    def scaled_sum(cls, items: list[int]) -> int:
        total = 0
        for x in items:
            total += x * cls.scale
        return total
