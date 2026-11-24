import sys


class Tracer:
    __slots__ = ("fn", "edges", "prev")

    def __init__(self, filename):
        self.fn = filename
        self.edges = set()
        self.prev = {}

    def _global(self, frame, event, arg):
        if frame.f_code.co_filename == self.fn:
            self.prev[id(frame)] = -1
            return self._local
        return None                       # other files: no per-line tracing, near-zero overhead

    def _local(self, frame, event, arg):
        k = id(frame)
        if event == "line":
            ln = frame.f_lineno
            self.edges.add((self.prev.get(k, -1), ln))
            self.prev[k] = ln
        elif event == "return":
            self.edges.add((self.prev.get(k, -1), -2))
            self.prev.pop(k, None)
        return self._local

    def start(self):
        sys.settrace(self._global)

    def stop(self):
        sys.settrace(None)

    def result(self):
        return sorted(f"{a}>{b}" for a, b in self.edges)