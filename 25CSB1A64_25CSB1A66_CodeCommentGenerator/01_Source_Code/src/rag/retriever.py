"""
BM25 retriever
===============
Okapi BM25 (k1 = 1.5, b = 0.75) over code-aware tokens. Identifiers are split on
underscores, dots and camelCase, so ``render_template_string`` matches a query
that mentions "template string", and ``setFeature`` matches "set feature".
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Sequence, Tuple

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*|\d+")
_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")
STOPWORDS = frozenset("""
a an and are as at be but by for from has have if in into is it its of on or that the this
to was were will with without not no do does use used using self return def import true false
none value data""".split())


def tokenize(text: str) -> List[str]:
    """Lower-case word and sub-word tokens; keeps CWE/rule ids whole (cwe-89 → cwe89)."""
    text = re.sub(r"\b(CWE|SEC)[-\s]?(\d+)", lambda m: f" {m.group(1)}{m.group(2)} ", text, flags=re.I)
    out: List[str] = []
    for word in _WORD.findall(text):
        low = word.lower()
        if low.startswith(("cwe", "sec")) and low[3:].isdigit():
            out.append(low)
            continue
        parts = [p.lower() for p in _CAMEL.findall(word)] or [low]
        for p in parts:
            if len(p) > 1 and p not in STOPWORDS:
                out.append(p)
        if len(parts) > 1 and low not in STOPWORDS:
            out.append(low)          # the whole identifier as well
    return out


class BM25:
    def __init__(self, documents: Sequence[Sequence[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf: List[Counter] = [Counter(d) for d in documents]
        self.lengths = [len(d) for d in documents]
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        df: Dict[str, int] = Counter()
        for tf in self.tf:
            df.update(tf.keys())
        n = len(documents)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: Iterable[str]) -> List[float]:
        q = Counter(query)
        out = []
        for tf, length in zip(self.tf, self.lengths):
            s = 0.0
            norm = self.k1 * (1 - self.b + self.b * length / self.avg) if self.avg else self.k1
            for term, qn in q.items():
                f = tf.get(term)
                if f:
                    s += self.idf[term] * f * (self.k1 + 1) / (f + norm) * (1 + math.log(qn))
            out.append(s)
        return out

    def top(self, query: Iterable[str], k: int) -> List[Tuple[int, float]]:
        ranked = sorted(enumerate(self.scores(query)), key=lambda p: (-p[1], p[0]))
        return [(i, s) for i, s in ranked[:k] if s > 0]
