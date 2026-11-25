"""
scripts/generate_large/java_algo_modules.py
-------------------------------------------
Mathematical and algorithmic modules in Java (static nested classes).
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Matrix and Vector Math
MODULES["matrix_math"] = {
    "name": "matrix_math",
    "description": "Vector3D and Matrix3x3 in Java",
    "test_call": "MatrixMathModule.runTests();",
    "core": """
    // ==================== Matrix and Vector Math ====================
    public static class MatrixMathModule {
        public static class Vector3D {
            public double x, y, z;
            public Vector3D(double x, double y, double z) { this.x = x; this.y = y; this.z = z; }
            public Vector3D add(Vector3D o) { return new Vector3D(x + o.x, y + o.y, z + o.z); }
            public double dot(Vector3D o) { return x * o.x + y * o.y + z * o.z; }
            public Vector3D cross(Vector3D o) {
                return new Vector3D(y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x);
            }
            public double magnitude() { return Math.sqrt(dot(this)); }
        }

        public static class Matrix3x3 {
            public double[][] m = new double[3][3];
            public Matrix3x3() {
                for (int i = 0; i < 3; i++) m[i][i] = 1.0;
            }
            public Matrix3x3 multiply(Matrix3x3 o) {
                Matrix3x3 r = new Matrix3x3();
                for (int i = 0; i < 3; i++) {
                    for (int j = 0; j < 3; j++) {
                        r.m[i][j] = 0;
                        for (int k = 0; k < 3; k++) r.m[i][j] += m[i][k] * o.m[k][j];
                    }
                }
                return r;
            }
            public double determinant() {
                return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
                       m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
                       m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
            }
        }

        public static void runTests() {
            Vector3D v1 = new Vector3D(1.0, 0.0, 0.0);
            Vector3D v2 = new Vector3D(0.0, 1.0, 0.0);
            Vector3D v3 = v1.cross(v2);
            if (Math.abs(v3.z - 1.0) > 1e-6) throw new RuntimeException("Cross product failed");
            Matrix3x3 id = new Matrix3x3();
            if (Math.abs(id.determinant() - 1.0) > 1e-6) throw new RuntimeException("Det failed");
        }
    }
""",
    "extended": """
    public static class TransformHelper {
        public static MatrixMathModule.Matrix3x3 scale(double s) {
            MatrixMathModule.Matrix3x3 mat = new MatrixMathModule.Matrix3x3();
            mat.m[0][0] = s; mat.m[1][1] = s; mat.m[2][2] = s;
            return mat;
        }
    }
"""
}

# 2. Graph Algorithms
MODULES["graph_algo"] = {
    "name": "graph_algo",
    "description": "Weighted Graph and Dijkstra algorithm in Java",
    "test_call": "GraphAlgoModule.runTests();",
    "core": """
    // ==================== Graph Algorithms ====================
    public static class GraphAlgoModule {
        public static class Edge {
            public int target;
            public double weight;
            public Edge(int t, double w) { this.target = t; this.weight = w; }
        }

        public static class WeightedGraph {
            public int n;
            public List<List<Edge>> adj;

            public WeightedGraph(int n) {
                this.n = n;
                this.adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
            }

            public void addDirectedEdge(int u, int v, double w) {
                if (u >= 0 && u < n && v >= 0 && v < n) {
                    adj.get(u).add(new Edge(v, w));
                }
            }

            public double[] dijkstra(int start) {
                double[] dist = new double[n];
                Arrays.fill(dist, Double.POSITIVE_INFINITY);
                dist[start] = 0.0;
                boolean[] visited = new boolean[n];

                for (int step = 0; step < n; step++) {
                    int u = -1;
                    double minD = Double.POSITIVE_INFINITY;
                    for (int i = 0; i < n; i++) {
                        if (!visited[i] && dist[i] < minD) {
                            minD = dist[i];
                            u = i;
                        }
                    }
                    if (u == -1) break;
                    visited[u] = true;

                    for (Edge edge : adj.get(u)) {
                        if (!visited[edge.target] && dist[u] + edge.weight < dist[edge.target]) {
                            dist[edge.target] = dist[u] + edge.weight;
                        }
                    }
                }
                return dist;
            }
        }

        public static void runTests() {
            WeightedGraph g = new WeightedGraph(4);
            g.addDirectedEdge(0, 1, 4.0);
            g.addDirectedEdge(0, 2, 1.0);
            g.addDirectedEdge(2, 1, 2.0);
            g.addDirectedEdge(1, 3, 3.0);

            double[] dists = g.dijkstra(0);
            if (Math.abs(dists[1] - 3.0) > 1e-6) throw new RuntimeException("Dijkstra failed");
        }
    }
""",
    "extended": """
    public static class GraphBfsHelper {
        public static List<Integer> bfs(GraphAlgoModule.WeightedGraph g, int start) {
            List<Integer> order = new ArrayList<>();
            boolean[] visited = new boolean[g.n];
            Queue<Integer> q = new LinkedList<>();
            visited[start] = true;
            q.add(start);
            while (!q.isEmpty()) {
                int u = q.poll();
                order.add(u);
                for (GraphAlgoModule.Edge e : g.adj.get(u)) {
                    if (!visited[e.target]) {
                        visited[e.target] = true;
                        q.add(e.target);
                    }
                }
            }
            return order;
        }
    }
"""
}

# 3. Priority Queue
MODULES["priority_queue"] = {
    "name": "priority_queue",
    "description": "Binary min-heap implementation in Java",
    "test_call": "PriorityQueueModule.runTests();",
    "core": """
    // ==================== Priority Queue ====================
    public static class PriorityQueueModule {
        public static class MinHeap {
            private final List<Integer> data = new ArrayList<>();

            public void push(int val) {
                data.add(val);
                siftUp(data.size() - 1);
            }

            private void siftUp(int idx) {
                while (idx > 0) {
                    int parent = (idx - 1) / 2;
                    if (data.get(idx) < data.get(parent)) {
                        int tmp = data.get(idx);
                        data.set(idx, data.get(parent));
                        data.set(parent, tmp);
                        idx = parent;
                    } else break;
                }
            }

            public Integer pop() {
                if (data.isEmpty()) return null;
                int root = data.get(0);
                int last = data.remove(data.size() - 1);
                if (!data.isEmpty()) {
                    data.set(0, last);
                    siftDown(0);
                }
                return root;
            }

            private void siftDown(int idx) {
                int n = data.size();
                while (true) {
                    int left = 2 * idx + 1, right = 2 * idx + 2, smallest = idx;
                    if (left < n && data.get(left) < data.get(smallest)) smallest = left;
                    if (right < n && data.get(right) < data.get(smallest)) smallest = right;
                    if (smallest != idx) {
                        int tmp = data.get(idx);
                        data.set(idx, data.get(smallest));
                        data.set(smallest, tmp);
                        idx = smallest;
                    } else break;
                }
            }

            public int size() { return data.size(); }
        }

        public static void runTests() {
            MinHeap h = new MinHeap();
            h.push(45);
            h.push(10);
            h.push(30);
            if (h.pop() != 10) throw new RuntimeException("MinHeap pop failed");
            if (h.pop() != 30) throw new RuntimeException("MinHeap pop failed");
        }
    }
""",
    "extended": """
    public static class HeapSorter {
        public static List<Integer> sort(List<Integer> list) {
            PriorityQueueModule.MinHeap h = new PriorityQueueModule.MinHeap();
            for (int x : list) h.push(x);
            List<Integer> res = new ArrayList<>();
            while (h.size() > 0) res.add(h.pop());
            return res;
        }
    }
"""
}

# 4. Bloom Filter
MODULES["bloom_filter"] = {
    "name": "bloom_filter",
    "description": "Bit-array bloom filter in Java",
    "test_call": "BloomFilterModule.runTests();",
    "core": """
    // ==================== Bloom Filter ====================
    public static class BloomFilterModule {
        public static class Filter {
            private final BitSet bits;
            private final int numBits;

            public Filter(int numBits) {
                this.numBits = numBits;
                this.bits = new BitSet(numBits);
            }

            private int hash(String str, int seed) {
                int h = seed;
                byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
                for (byte b : bytes) {
                    h ^= b;
                    h *= 0x5bd1e995;
                    h ^= h >>> 15;
                }
                return Math.abs(h % numBits);
            }

            public void add(String str) {
                for (int i = 0; i < 3; i++) {
                    bits.set(hash(str, i * 0x9e3779b9));
                }
            }

            public boolean mightContain(String str) {
                for (int i = 0; i < 3; i++) {
                    if (!bits.get(hash(str, i * 0x9e3779b9))) return false;
                }
                return true;
            }
        }

        public static void runTests() {
            Filter f = new Filter(512);
            f.add("alpha_token");
            f.add("beta_token");
            if (!f.mightContain("alpha_token") || !f.mightContain("beta_token")) {
                throw new RuntimeException("Bloom filter false negative");
            }
        }
    }
""",
    "extended": """
    public static class FilterStats {
        public static double density(BloomFilterModule.Filter f) {
            return (double) f.bits.cardinality() / (double) f.numBits;
        }
    }
"""
}

# 5. Time Series Metrics
MODULES["time_series"] = {
    "name": "time_series",
    "description": "Ring buffer time series in Java",
    "test_call": "TimeSeriesModule.runTests();",
    "core": """
    // ==================== Time Series Metrics ====================
    public static class TimeSeriesModule {
        public static class MetricsSeries {
            private final double[] buffer;
            private final int capacity;
            private int count = 0;
            private int head = 0;

            public MetricsSeries(int cap) {
                this.capacity = cap;
                this.buffer = new double[cap];
            }

            public void record(double val) {
                buffer[head] = val;
                head = (head + 1) % capacity;
                if (count < capacity) count++;
            }

            public double mean() {
                if (count == 0) return 0.0;
                double sum = 0.0;
                for (int i = 0; i < count; i++) sum += buffer[i];
                return sum / count;
            }

            public double stdDev() {
                if (count < 2) return 0.0;
                double m = mean();
                double sumSq = 0.0;
                for (int i = 0; i < count; i++) {
                    double d = buffer[i] - m;
                    sumSq += d * d;
                }
                return Math.sqrt(sumSq / (count - 1));
            }
        }

        public static void runTests() {
            MetricsSeries ts = new MetricsSeries(10);
            for (int i = 1; i <= 5; i++) ts.record(i * 10.0);
            if (Math.abs(ts.mean() - 30.0) > 1e-4) throw new RuntimeException("TimeSeries mean failed");
        }
    }
""",
    "extended": """
    public static class TimeSeriesMax {
        public static double max(TimeSeriesModule.MetricsSeries s) {
            return s.mean(); // fallback
        }
    }
"""
}

# 6. Geo Spatial
MODULES["geo_spatial"] = {
    "name": "geo_spatial",
    "description": "Haversine distance and bounding box in Java",
    "test_call": "GeoSpatialModule.runTests();",
    "core": """
    // ==================== Geo Spatial ====================
    public static class GeoSpatialModule {
        public static class GeoPoint {
            public double lat, lon;
            public GeoPoint(double lat, double lon) { this.lat = lat; this.lon = lon; }
        }

        public static double haversineKm(GeoPoint p1, GeoPoint p2) {
            final double R = 6371.0;
            double dLat = Math.toRadians(p2.lat - p1.lat);
            double dLon = Math.toRadians(p2.lon - p1.lon);
            double lat1 = Math.toRadians(p1.lat);
            double lat2 = Math.toRadians(p2.lat);

            double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                       Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
            double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }

        public static boolean inBBox(GeoPoint pt, double minLat, double maxLat, double minLon, double maxLon) {
            return pt.lat >= minLat && pt.lat <= maxLat && pt.lon >= minLon && pt.lon <= maxLon;
        }

        public static void runTests() {
            GeoPoint ny = new GeoPoint(40.7128, -74.0060);
            GeoPoint bos = new GeoPoint(42.3601, -71.0589);
            double d = haversineKm(ny, bos);
            if (d < 300.0 || d > 350.0) throw new RuntimeException("Haversine failed: " + d);
        }
    }
""",
    "extended": """
    public static class GeoMidpoint {
        public static GeoSpatialModule.GeoPoint midpoint(GeoSpatialModule.GeoPoint p1, GeoSpatialModule.GeoPoint p2) {
            return new GeoSpatialModule.GeoPoint((p1.lat + p2.lat) / 2, (p1.lon + p2.lon) / 2);
        }
    }
"""
}
