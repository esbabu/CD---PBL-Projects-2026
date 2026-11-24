# Known-wrong rewrite: drops the equal-dict dedupe quirk and returns copies/keys
from collections import Counter

def find_duplicates():
    counts = Counter(s["roll"] for s in students)
    dup_rolls = {r for r, count in counts.items() if count > 1}
    # Drops the value-equality dedupe quirk and doesn't preserve exact dict object identities
    return [s.copy() for s in students if s["roll"] in dup_rolls]
