def process_records(items, mode="sum", *extra, multiplier=1, **opts):
    def helper(val):
        return val * multiplier

    filtered = [x for x in items if (y := helper(x)) > 0]
    match mode:
        case "sum":
            acc = 0
            for v in filtered:
                acc += v
            for e in extra:
                acc += e
            return acc
        case "unique":
            seen = []
            for v in filtered:
                if v not in seen:
                    seen.append(v)
            return len(seen)
        case _:
            return 0
