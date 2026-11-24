from collections import Counter


def dedupe_rank(words, top):
    return [w for w, _ in Counter(words).most_common(top)]