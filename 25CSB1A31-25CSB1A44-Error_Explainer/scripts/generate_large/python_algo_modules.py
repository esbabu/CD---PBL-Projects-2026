"""
scripts/generate_large/python_algo_modules.py
---------------------------------------------
Mathematical and algorithmic modules in clean Python 3.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Matrix and Vector Math
MODULES["matrix_math"] = {
    "name": "matrix_math",
    "description": "3D Vector and 3x3 Matrix math in Python 3",
    "test_call": "test_matrix_math()",
    "core": """
# ==================== Matrix and Vector Math ====================
@dataclasses.dataclass
class Vector3D:
    x: float
    y: float
    z: float

    def __add__(self, o: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - o.x, self.y - o.y, self.z - o.z)

    def dot(self, o: 'Vector3D') -> float:
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o: 'Vector3D') -> 'Vector3D':
        return Vector3D(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x
        )

    def magnitude(self) -> float:
        return math.sqrt(self.dot(self))


class Matrix3x3:
    def __init__(self, data: Optional[List[List[float]]] = None):
        if data:
            self.m = data
        else:
            self.m = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]

    def multiply(self, o: 'Matrix3x3') -> 'Matrix3x3':
        res = [[0.0] * 3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    res[i][j] += self.m[i][k] * o.m[k][j]
        return Matrix3x3(res)

    def determinant(self) -> float:
        m = self.m
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )


def test_matrix_math() -> None:
    v1 = Vector3D(1.0, 0.0, 0.0)
    v2 = Vector3D(0.0, 1.0, 0.0)
    v3 = v1.cross(v2)
    assert abs(v3.z - 1.0) < 1e-6
    id_mat = Matrix3x3()
    assert abs(id_mat.determinant() - 1.0) < 1e-6
""",
    "extended": """
class MatrixTransform:
    @staticmethod
    def scale(sx: float, sy: float, sz: float) -> Matrix3x3:
        return Matrix3x3([
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, sz]
        ])
"""
}

# 2. Graph Algorithms
MODULES["graph_algo"] = {
    "name": "graph_algo",
    "description": "Weighted Graph and Dijkstra shortest path in Python 3",
    "test_call": "test_graph_algo()",
    "core": """
# ==================== Graph Algorithms ====================
@dataclasses.dataclass
class Edge:
    target: int
    weight: float


class WeightedGraph:
    def __init__(self, num_vertices: int):
        self.n = num_vertices
        self.adj: List[List[Edge]] = [[] for _ in range(num_vertices)]

    def add_directed_edge(self, u: int, v: int, w: float) -> None:
        if 0 <= u < self.n and 0 <= v < self.n:
            self.adj[u].append(Edge(v, w))

    def dijkstra(self, start: int) -> List[float]:
        dist = [float('inf')] * self.n
        dist[start] = 0.0
        visited = [False] * self.n

        for _ in range(self.n):
            u = -1
            min_d = float('inf')
            for i in range(self.n):
                if not visited[i] and dist[i] < min_d:
                    min_d = dist[i]
                    u = i
            if u == -1:
                break
            visited[u] = True

            for edge in self.adj[u]:
                if not visited[edge.target] and dist[u] + edge.weight < dist[edge.target]:
                    dist[edge.target] = dist[u] + edge.weight
        return dist


def test_graph_algo() -> None:
    g = WeightedGraph(4)
    g.add_directed_edge(0, 1, 4.0)
    g.add_directed_edge(0, 2, 1.0)
    g.add_directed_edge(2, 1, 2.0)
    g.add_directed_edge(1, 3, 3.0)

    dists = g.dijkstra(0)
    assert abs(dists[1] - 3.0) < 1e-6
""",
    "extended": """
class GraphBFS:
    @staticmethod
    def traverse(g: WeightedGraph, start: int) -> List[int]:
        visited = [False] * g.n
        order: List[int] = []
        queue = collections.deque([start])
        visited[start] = True

        while queue:
            u = queue.popleft()
            order.append(u)
            for edge in g.adj[u]:
                if not visited[edge.target]:
                    visited[edge.target] = True
                    queue.append(edge.target)
        return order
"""
}

# 3. Priority Queue
MODULES["priority_queue"] = {
    "name": "priority_queue",
    "description": "Binary min-heap implementation in Python 3",
    "test_call": "test_priority_queue()",
    "core": """
# ==================== Priority Queue ====================
class MinHeap:
    def __init__(self):
        self.data: List[int] = []

    def push(self, val: int) -> None:
        self.data.append(val)
        self._sift_up(len(self.data) - 1)

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self.data[idx] < self.data[parent]:
                self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
                idx = parent
            else:
                break

    def pop(self) -> Optional[int]:
        if not self.data:
            return None
        root = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return root

    def _sift_down(self, idx: int) -> None:
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < n and self.data[left] < self.data[smallest]:
                smallest = left
            if right < n and self.data[right] < self.data[smallest]:
                smallest = right
            if smallest != idx:
                self.data[idx], self.data[smallest] = self.data[smallest], self.data[idx]
                idx = smallest
            else:
                break


def test_priority_queue() -> None:
    pq = MinHeap()
    pq.push(40)
    pq.push(10)
    pq.push(30)
    assert pq.pop() == 10
    assert pq.pop() == 30
""",
    "extended": """
class HeapSorter:
    @staticmethod
    def sort(items: List[int]) -> List[int]:
        h = MinHeap()
        for x in items:
            h.push(x)
        res: List[int] = []
        while True:
            val = h.pop()
            if val is None:
                break
            res.append(val)
        return res
"""
}

# 4. Bloom Filter
MODULES["bloom_filter"] = {
    "name": "bloom_filter",
    "description": "Bit-array bloom filter in Python 3",
    "test_call": "test_bloom_filter()",
    "core": """
# ==================== Bloom Filter ====================
class BloomFilter:
    def __init__(self, num_bits: int = 512, num_hashes: int = 3):
        self.num_bits = num_bits
        self.num_hashes = num_hashes
        self.bits = [False] * num_bits

    def _hash(self, item: str, seed: int) -> int:
        h = seed
        for c in item.encode('utf-8'):
            h ^= c
            h = (h * 0x5bd1e995) & 0xFFFFFFFF
            h ^= h >> 15
        return h

    def add(self, item: str) -> None:
        for i in range(self.num_hashes):
            h = self._hash(item, i * 0x9e3779b9)
            self.bits[h % self.num_bits] = True

    def might_contain(self, item: str) -> bool:
        for i in range(self.num_hashes):
            h = self._hash(item, i * 0x9e3779b9)
            if not self.bits[h % self.num_bits]:
                return False
        return True


def test_bloom_filter() -> None:
    bf = BloomFilter()
    bf.add("test_key_1")
    bf.add("test_key_2")
    assert bf.might_contain("test_key_1")
    assert bf.might_contain("test_key_2")
""",
    "extended": """
class BloomMetrics:
    @staticmethod
    def density(bf: BloomFilter) -> float:
        set_bits = sum(1 for b in bf.bits if b)
        return set_bits / bf.num_bits
"""
}

# 5. Time Series Metrics
MODULES["time_series"] = {
    "name": "time_series",
    "description": "Ring buffer time series in Python 3",
    "test_call": "test_time_series()",
    "core": """
# ==================== Time Series Metrics ====================
class TimeSeriesMetrics:
    def __init__(self, capacity: int = 32):
        self.capacity = capacity
        self.buffer: List[float] = []

    def record(self, val: float) -> None:
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(val)

    def mean(self) -> float:
        return sum(self.buffer) / len(self.buffer) if self.buffer else 0.0

    def standard_deviation(self) -> float:
        if len(self.buffer) < 2:
            return 0.0
        m = self.mean()
        variance = sum((x - m) ** 2 for x in self.buffer) / (len(self.buffer) - 1)
        return math.sqrt(variance)


def test_time_series() -> None:
    ts = TimeSeriesMetrics(10)
    for i in range(1, 6):
        ts.record(float(i * 10))
    assert abs(ts.mean() - 30.0) < 1e-4
""",
    "extended": """
class PercentileCalculator:
    @staticmethod
    def calc(series: TimeSeriesMetrics, pct: float) -> float:
        if not series.buffer:
            return 0.0
        s = sorted(series.buffer)
        idx = int(pct * (len(s) - 1))
        return s[idx]
"""
}

# 6. Geo Spatial
MODULES["geo_spatial"] = {
    "name": "geo_spatial",
    "description": "Haversine distance and 2D bounding box in Python 3",
    "test_call": "test_geo_spatial()",
    "core": """
# ==================== Geo Spatial ====================
@dataclasses.dataclass
class GeoPoint:
    lat: float
    lon: float


class GeoSpatial:
    @staticmethod
    def haversine_km(p1: GeoPoint, p2: GeoPoint) -> float:
        R = 6371.0
        d_lat = math.radians(p2.lat - p1.lat)
        d_lon = math.radians(p2.lon - p1.lon)
        lat1 = math.radians(p1.lat)
        lat2 = math.radians(p2.lat)

        a = math.sin(d_lat / 2)**2 + math.sin(d_lon / 2)**2 * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def in_bbox(pt: GeoPoint, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> bool:
        return min_lat <= pt.lat <= max_lat and min_lon <= pt.lon <= max_lon


def test_geo_spatial() -> None:
    london = GeoPoint(51.5074, -0.1278)
    paris = GeoPoint(48.8566, 2.3522)
    d = GeoSpatial.haversine_km(london, paris)
    assert 330.0 < d < 360.0
""",
    "extended": """
class GeoMidpoint:
    @staticmethod
    def compute(p1: GeoPoint, p2: GeoPoint) -> GeoPoint:
        return GeoPoint((p1.lat + p2.lat) / 2.0, (p1.lon + p2.lon) / 2.0)
"""
}
