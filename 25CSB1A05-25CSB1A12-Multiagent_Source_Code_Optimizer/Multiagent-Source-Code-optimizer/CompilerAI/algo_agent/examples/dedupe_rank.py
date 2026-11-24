def dedupe_rank(words, top):
    seen = []
    for w in words:
        if w not in seen:
            seen.append(w)
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    seen.sort(key=lambda w: -counts[w])
    words.append("__done__")          # quirk: mutates the caller's list
    return seen[:top]