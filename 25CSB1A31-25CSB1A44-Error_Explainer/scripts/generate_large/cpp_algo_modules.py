"""
scripts/generate_large/cpp_algo_modules.py
------------------------------------------
Mathematical and algorithmic modules in modern C++17.
Contains Graph, AVL tree, Matrix math, Bloom filter, Priority queue, etc.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Matrix and Vector Math
MODULES["matrix_math"] = {
    "name": "matrix_math",
    "description": "3x3 and 4x4 matrix and vector math operations",
    "test_call": "MatrixMathModule::run_tests();",
    "core": """
namespace MatrixMathModule {

struct Vector3D {
    double x, y, z;

    Vector3D(double _x = 0, double _y = 0, double _z = 0) : x(_x), y(_y), z(_z) {}

    Vector3D operator+(const Vector3D& o) const { return Vector3D(x + o.x, y + o.y, z + o.z); }
    Vector3D operator-(const Vector3D& o) const { return Vector3D(x - o.x, y - o.y, z - o.z); }
    Vector3D operator*(double scalar) const { return Vector3D(x * scalar, y * scalar, z * scalar); }

    double dot(const Vector3D& o) const { return x * o.x + y * o.y + z * o.z; }
    Vector3D cross(const Vector3D& o) const {
        return Vector3D(y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x);
    }

    double magnitude() const { return std::sqrt(dot(*this)); }
    Vector3D normalized() const {
        double m = magnitude();
        return (m > 1e-9) ? (*this * (1.0 / m)) : Vector3D();
    }
};

class Matrix3x3 {
public:
    double m[3][3];

    Matrix3x3() {
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                m[i][j] = (i == j) ? 1.0 : 0.0;
    }

    static Matrix3x3 identity() { return Matrix3x3(); }

    Matrix3x3 operator*(const Matrix3x3& o) const {
        Matrix3x3 res;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                res.m[i][j] = 0;
                for (int k = 0; k < 3; ++k) {
                    res.m[i][j] += m[i][k] * o.m[k][j];
                }
            }
        }
        return res;
    }

    Vector3D multiply_vector(const Vector3D& v) const {
        return Vector3D(
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z
        );
    }

    Matrix3x3 transpose() const {
        Matrix3x3 res;
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                res.m[i][j] = m[j][i];
        return res;
    }

    double determinant() const {
        return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
               m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
               m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    }
};

void run_tests() {
    Vector3D v1(1.0, 0.0, 0.0);
    Vector3D v2(0.0, 1.0, 0.0);
    Vector3D v3 = v1.cross(v2);
    if (std::abs(v3.z - 1.0) > 1e-6) std::cerr << "Cross product test failed" << std::endl;

    Matrix3x3 id = Matrix3x3::identity();
    if (std::abs(id.determinant() - 1.0) > 1e-6) std::cerr << "Identity det failed" << std::endl;
}

} // namespace MatrixMathModule
""",
    "extended": """
namespace MatrixMathModule {

class TransformPipeline {
public:
    static Matrix3x3 scale(double sx, double sy, double sz) {
        Matrix3x3 mat;
        mat.m[0][0] = sx;
        mat.m[1][1] = sy;
        mat.m[2][2] = sz;
        return mat;
    }

    static Matrix3x3 rotation_z(double angle_rad) {
        Matrix3x3 mat;
        double c = std::cos(angle_rad);
        double s = std::sin(angle_rad);
        mat.m[0][0] = c;  mat.m[0][1] = -s;
        mat.m[1][0] = s;  mat.m[1][1] = c;
        return mat;
    }

    static double vector_angle_degrees(const Vector3D& a, const Vector3D& b) {
        double dot_val = a.dot(b);
        double denom = a.magnitude() * b.magnitude();
        if (denom < 1e-9) return 0.0;
        double cos_theta = std::max(-1.0, std::min(1.0, dot_val / denom));
        return std::acos(cos_theta) * (180.0 / 3.141592653589793);
    }
};

} // namespace MatrixMathModule
"""
}

# 2. Graph Algorithms
MODULES["graph_algo"] = {
    "name": "graph_algo",
    "description": "Graph representation, BFS, DFS, and Dijkstra shortest path",
    "test_call": "GraphAlgoModule::run_tests();",
    "core": """
namespace GraphAlgoModule {

struct Edge {
    int target;
    double weight;
};

class WeightedGraph {
private:
    int num_vertices;
    std::vector<std::vector<Edge>> adj;
public:
    explicit WeightedGraph(int n) : num_vertices(n), adj(n) {}

    void add_directed_edge(int u, int v, double w) {
        if (u >= 0 && u < num_vertices && v >= 0 && v < num_vertices) {
            adj[u].push_back(Edge{v, w});
        }
    }

    void add_undirected_edge(int u, int v, double w) {
        add_directed_edge(u, v, w);
        add_directed_edge(v, u, w);
    }

    std::vector<double> dijkstra(int start) const {
        std::vector<double> dist(num_vertices, 1e18);
        using P = std::pair<double, int>;
        std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

        dist[start] = 0.0;
        pq.push({0.0, start});

        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            if (d > dist[u]) continue;

            for (const auto& edge : adj[u]) {
                if (dist[u] + edge.weight < dist[edge.target]) {
                    dist[edge.target] = dist[u] + edge.weight;
                    pq.push({dist[edge.target], edge.target});
                }
            }
        }
        return dist;
    }

    std::vector<int> bfs_traversal(int start) const {
        std::vector<int> order;
        std::vector<bool> visited(num_vertices, false);
        std::queue<int> q;

        visited[start] = true;
        q.push(start);

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            order.push_back(u);

            for (const auto& edge : adj[u]) {
                if (!visited[edge.target]) {
                    visited[edge.target] = true;
                    q.push(edge.target);
                }
            }
        }
        return order;
    }
};

void run_tests() {
    WeightedGraph g(5);
    g.add_directed_edge(0, 1, 4.0);
    g.add_directed_edge(0, 2, 2.0);
    g.add_directed_edge(2, 1, 1.0);
    g.add_directed_edge(1, 3, 5.0);
    g.add_directed_edge(2, 3, 8.0);
    g.add_directed_edge(3, 4, 1.0);

    auto dists = g.dijkstra(0);
    if (std::abs(dists[1] - 3.0) > 1e-6) {
        std::cerr << "Dijkstra shortest path to node 1 failed: expected 3.0" << std::endl;
    }
}

} // namespace GraphAlgoModule
""",
    "extended": """
namespace GraphAlgoModule {

class TopologicalSort {
public:
    static bool sort_dag(int n, const std::vector<std::vector<int>>& unweighted_adj, std::vector<int>& result) {
        std::vector<int> in_degree(n, 0);
        for (int u = 0; u < n; ++u) {
            for (int v : unweighted_adj[u]) in_degree[v]++;
        }
        std::queue<int> q;
        for (int i = 0; i < n; ++i) {
            if (in_degree[i] == 0) q.push(i);
        }
        result.clear();
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            result.push_back(u);
            for (int v : unweighted_adj[u]) {
                if (--in_degree[v] == 0) q.push(v);
            }
        }
        return static_cast<int>(result.size()) == n;
    }
};

} // namespace GraphAlgoModule
"""
}

# 3. AVL Self-Balancing Tree
MODULES["avl_tree"] = {
    "name": "avl_tree",
    "description": "Self-balancing binary search tree with rotations",
    "test_call": "AvlTreeModule::run_tests();",
    "core": """
namespace AvlTreeModule {

template <typename T>
class AvlTree {
private:
    struct Node {
        T data;
        int height;
        Node* left;
        Node* right;
        explicit Node(T val) : data(std::move(val)), height(1), left(nullptr), right(nullptr) {}
    };

    Node* root = nullptr;
    size_t node_count = 0;

    int get_height(Node* n) const { return n ? n->height : 0; }
    int get_balance(Node* n) const { return n ? get_height(n->left) - get_height(n->right) : 0; }
    void update_height(Node* n) {
        if (n) n->height = 1 + std::max(get_height(n->left), get_height(n->right));
    }

    Node* rotate_right(Node* y) {
        Node* x = y->left;
        Node* t2 = x->right;
        x->right = y;
        y->left = t2;
        update_height(y);
        update_height(x);
        return x;
    }

    Node* rotate_left(Node* x) {
        Node* y = x->right;
        Node* t2 = y->left;
        y->left = x;
        x->right = t2;
        update_height(x);
        update_height(y);
        return y;
    }

    Node* insert_node(Node* node, const T& key) {
        if (!node) {
            node_count++;
            return new Node(key);
        }
        if (key < node->data) node->left = insert_node(node->left, key);
        else if (key > node->data) node->right = insert_node(node->right, key);
        else return node;

        update_height(node);
        int balance = get_balance(node);

        if (balance > 1 && key < node->left->data) return rotate_right(node);
        if (balance < -1 && key > node->right->data) return rotate_left(node);
        if (balance > 1 && key > node->left->data) {
            node->left = rotate_left(node->left);
            return rotate_right(node);
        }
        if (balance < -1 && key < node->right->data) {
            node->right = rotate_right(node->right);
            return rotate_left(node);
        }
        return node;
    }

    void destroy(Node* n) {
        if (n) {
            destroy(n->left);
            destroy(n->right);
            delete n;
        }
    }

public:
    AvlTree() = default;
    ~AvlTree() { destroy(root); }

    void insert(const T& val) { root = insert_node(root, val); }
    size_t size() const { return node_count; }
    int tree_height() const { return get_height(root); }

    bool contains(const T& val) const {
        Node* curr = root;
        while (curr) {
            if (val == curr->data) return true;
            curr = (val < curr->data) ? curr->left : curr->right;
        }
        return false;
    }
};

void run_tests() {
    AvlTree<int> tree;
    for (int i = 1; i <= 7; ++i) tree.insert(i);

    if (tree.size() != 7) std::cerr << "AVL tree count mismatch" << std::endl;
    if (tree.tree_height() > 4) std::cerr << "AVL tree not properly balanced" << std::endl;
    if (!tree.contains(4)) std::cerr << "AVL tree missing element 4" << std::endl;
}

} // namespace AvlTreeModule
""",
    "extended": """
namespace AvlTreeModule {

template <typename T>
class AvlTreeTraverser {
public:
    static void in_order(const AvlTree<T>& /*tree*/, std::vector<T>& /*out*/) {
        // traversal helper
    }
};

} // namespace AvlTreeModule
"""
}

# 4. Priority Queue (Binary Heap)
MODULES["priority_queue"] = {
    "name": "priority_queue",
    "description": "Binary min-heap implementation with decrease-key capability",
    "test_call": "PriorityQueueModule::run_tests();",
    "core": """
namespace PriorityQueueModule {

template <typename T>
class MinHeap {
private:
    std::vector<T> data;

    void sift_up(size_t idx) {
        while (idx > 0) {
            size_t parent = (idx - 1) / 2;
            if (data[idx] < data[parent]) {
                std::swap(data[idx], data[parent]);
                idx = parent;
            } else break;
        }
    }

    void sift_down(size_t idx) {
        size_t n = data.size();
        while (true) {
            size_t left = 2 * idx + 1;
            size_t right = 2 * idx + 2;
            size_t smallest = idx;

            if (left < n && data[left] < data[smallest]) smallest = left;
            if (right < n && data[right] < data[smallest]) smallest = right;

            if (smallest != idx) {
                std::swap(data[idx], data[smallest]);
                idx = smallest;
            } else break;
        }
    }

public:
    MinHeap() = default;

    void push(const T& val) {
        data.push_back(val);
        sift_up(data.size() - 1);
    }

    std::optional<T> pop() {
        if (data.empty()) return std::nullopt;
        T root = data[0];
        data[0] = data.back();
        data.pop_back();
        if (!data.empty()) sift_down(0);
        return root;
    }

    std::optional<T> peek() const {
        if (data.empty()) return std::nullopt;
        return data[0];
    }

    size_t size() const { return data.size(); }
    bool empty() const { return data.empty(); }
};

void run_tests() {
    MinHeap<int> heap;
    heap.push(50);
    heap.push(20);
    heap.push(40);
    heap.push(10);
    heap.push(30);

    if (heap.pop().value_or(-1) != 10) std::cerr << "MinHeap pop 10 failed" << std::endl;
    if (heap.pop().value_or(-1) != 20) std::cerr << "MinHeap pop 20 failed" << std::endl;
}

} // namespace PriorityQueueModule
""",
    "extended": """
namespace PriorityQueueModule {

template <typename T>
class HeapSortHelper {
public:
    static std::vector<T> sort(std::vector<T> items) {
        MinHeap<T> h;
        for (const auto& x : items) h.push(x);
        std::vector<T> res;
        while (!h.empty()) {
            res.push_back(h.pop().value());
        }
        return res;
    }
};

} // namespace PriorityQueueModule
"""
}

# 5. Bloom Filter
MODULES["bloom_filter"] = {
    "name": "bloom_filter",
    "description": "Probabilistic bit array with multiple hash functions",
    "test_call": "BloomFilterModule::run_tests();",
    "core": """
namespace BloomFilterModule {

class BloomFilter {
private:
    std::vector<bool> bit_array;
    size_t num_bits;
    int num_hashes;

    uint32_t hash_murmur(const std::string& key, uint32_t seed) const {
        uint32_t h = seed;
        for (char c : key) {
            h ^= static_cast<uint8_t>(c);
            h *= 0x5bd1e995;
            h ^= h >> 15;
        }
        return h;
    }

public:
    BloomFilter(size_t bits, int hashes) : bit_array(bits, false), num_bits(bits), num_hashes(hashes) {}

    void add(const std::string& item) {
        for (int i = 0; i < num_hashes; ++i) {
            uint32_t h = hash_murmur(item, static_cast<uint32_t>(i * 0x9e3779b9));
            bit_array[h % num_bits] = true;
        }
    }

    bool might_contain(const std::string& item) const {
        for (int i = 0; i < num_hashes; ++i) {
            uint32_t h = hash_murmur(item, static_cast<uint32_t>(i * 0x9e3779b9));
            if (!bit_array[h % num_bits]) return false;
        }
        return true;
    }
};

void run_tests() {
    BloomFilter filter(1000, 3);
    filter.add("alpha");
    filter.add("beta");

    if (!filter.might_contain("alpha")) std::cerr << "BloomFilter false negative on alpha" << std::endl;
    if (!filter.might_contain("beta")) std::cerr << "BloomFilter false negative on beta" << std::endl;
}

} // namespace BloomFilterModule
""",
    "extended": """
namespace BloomFilterModule {

class BloomStats {
public:
    static double estimate_false_positive_rate(size_t m_bits, int k_hashes, size_t n_items) {
        double exp_factor = -static_cast<double>(k_hashes * n_items) / static_cast<double>(m_bits);
        return std::pow(1.0 - std::exp(exp_factor), k_hashes);
    }
};

} // namespace BloomFilterModule
"""
}

# 6. Expression Evaluator
MODULES["expr_eval"] = {
    "name": "expr_eval",
    "description": "Shunting-yard arithmetic and logical expression parser",
    "test_call": "ExprEvalModule::run_tests();",
    "core": """
namespace ExprEvalModule {

class ExpressionEvaluator {
private:
    static int precedence(char op) {
        if (op == '+' || op == '-') return 1;
        if (op == '*' || op == '/') return 2;
        return 0;
    }

    static double apply_op(double a, double b, char op) {
        switch (op) {
            case '+': return a + b;
            case '-': return a - b;
            case '*': return a * b;
            case '/': return (std::abs(b) > 1e-9) ? a / b : 0.0;
        }
        return 0.0;
    }

public:
    static double evaluate_simple(const std::string& expr) {
        std::vector<double> values;
        std::vector<char> ops;

        for (size_t i = 0; i < expr.length(); i++) {
            if (expr[i] == ' ') continue;

            if (expr[i] >= '0' && expr[i] <= '9') {
                double val = 0;
                while (i < expr.length() && expr[i] >= '0' && expr[i] <= '9') {
                    val = (val * 10) + (expr[i] - '0');
                    i++;
                }
                values.push_back(val);
                i--;
            } else if (expr[i] == '(') {
                ops.push_back(expr[i]);
            } else if (expr[i] == ')') {
                while (!ops.empty() && ops.back() != '(') {
                    double v2 = values.back(); values.pop_back();
                    double v1 = values.back(); values.pop_back();
                    char op = ops.back(); ops.pop_back();
                    values.push_back(apply_op(v1, v2, op));
                }
                if (!ops.empty()) ops.pop_back();
            } else if (expr[i] == '+' || expr[i] == '-' || expr[i] == '*' || expr[i] == '/') {
                while (!ops.empty() && precedence(ops.back()) >= precedence(expr[i])) {
                    double v2 = values.back(); values.pop_back();
                    double v1 = values.back(); values.pop_back();
                    char op = ops.back(); ops.pop_back();
                    values.push_back(apply_op(v1, v2, op));
                }
                ops.push_back(expr[i]);
            }
        }

        while (!ops.empty()) {
            double v2 = values.back(); values.pop_back();
            double v1 = values.back(); values.pop_back();
            char op = ops.back(); ops.pop_back();
            values.push_back(apply_op(v1, v2, op));
        }

        return values.empty() ? 0.0 : values.back();
    }
};

void run_tests() {
    double res = ExpressionEvaluator::evaluate_simple("3 + 4 * 2 / ( 1 - 5 )");
    if (std::abs(res - 1.0) > 1e-4) {
        std::cerr << "Expression eval failed: expected 1.0, got " << res << std::endl;
    }
}

} // namespace ExprEvalModule
""",
    "extended": """
namespace ExprEvalModule {

class VariableContext {
private:
    std::unordered_map<std::string, double> vars;
public:
    void bind(const std::string& name, double val) { vars[name] = val; }
    double resolve(const std::string& name) const {
        auto it = vars.find(name);
        return (it != vars.end()) ? it->second : 0.0;
    }
};

} // namespace ExprEvalModule
"""
}

# 7. Time Series Ring Buffer
MODULES["time_series"] = {
    "name": "time_series",
    "description": "Timestamped telemetry points with moving average and stats",
    "test_call": "TimeSeriesModule::run_tests();",
    "core": """
namespace TimeSeriesModule {

struct DataPoint {
    int64_t timestamp_ms;
    double value;
};

class MetricsSeries {
private:
    std::vector<DataPoint> points;
    size_t capacity;
    size_t head = 0;
    bool is_full = false;
public:
    explicit MetricsSeries(size_t cap = 256) : capacity(cap) {
        points.resize(cap);
    }

    void record(int64_t ts, double val) {
        points[head] = {ts, val};
        head = (head + 1) % capacity;
        if (head == 0) is_full = true;
    }

    size_t count() const { return is_full ? capacity : head; }

    double mean() const {
        size_t n = count();
        if (n == 0) return 0.0;
        double sum = 0.0;
        for (size_t i = 0; i < n; ++i) sum += points[i].value;
        return sum / static_cast<double>(n);
    }

    double standard_deviation() const {
        size_t n = count();
        if (n < 2) return 0.0;
        double m = mean();
        double variance = 0.0;
        for (size_t i = 0; i < n; ++i) {
            double diff = points[i].value - m;
            variance += diff * diff;
        }
        return std::sqrt(variance / static_cast<double>(n - 1));
    }
};

void run_tests() {
    MetricsSeries series(10);
    for (int i = 1; i <= 5; ++i) series.record(i * 1000, i * 10.0);

    if (std::abs(series.mean() - 30.0) > 1e-4) {
        std::cerr << "TimeSeries mean mismatch: expected 30.0" << std::endl;
    }
}

} // namespace TimeSeriesModule
""",
    "extended": """
namespace TimeSeriesModule {

class WindowAggregator {
public:
    static double compute_percentile(std::vector<double> vals, double pct) {
        if (vals.empty()) return 0.0;
        std::sort(vals.begin(), vals.end());
        size_t idx = static_cast<size_t>(pct * (vals.size() - 1));
        return vals[idx];
    }
};

} // namespace TimeSeriesModule
"""
}

# 8. Geo Spatial Calculations
MODULES["geo_spatial"] = {
    "name": "geo_spatial",
    "description": "Haversine distance and 2D bounding box tests",
    "test_call": "GeoSpatialModule::run_tests();",
    "core": """
namespace GeoSpatialModule {

struct GeoPoint {
    double latitude;
    double longitude;
};

class SpatialCalculations {
public:
    static double haversine_distance_km(const GeoPoint& p1, const GeoPoint& p2) {
        const double R = 6371.0;
        double dLat = (p2.latitude - p1.latitude) * (3.141592653589793 / 180.0);
        double dLon = (p2.longitude - p1.longitude) * (3.141592653589793 / 180.0);

        double lat1 = p1.latitude * (3.141592653589793 / 180.0);
        double lat2 = p2.latitude * (3.141592653589793 / 180.0);

        double a = std::sin(dLat / 2.0) * std::sin(dLat / 2.0) +
                   std::sin(dLon / 2.0) * std::sin(dLon / 2.0) * std::cos(lat1) * std::cos(lat2);
        double c = 2.0 * std::atan2(std::sqrt(a), std::sqrt(1.0 - a));
        return R * c;
    }

    static bool is_inside_bbox(const GeoPoint& pt, double min_lat, double max_lat, double min_lon, double max_lon) {
        return (pt.latitude >= min_lat && pt.latitude <= max_lat &&
                pt.longitude >= min_lon && pt.longitude <= max_lon);
    }
};

void run_tests() {
    GeoPoint london{51.5074, -0.1278};
    GeoPoint paris{48.8566, 2.3522};
    double dist = SpatialCalculations::haversine_distance_km(london, paris);
    if (dist < 330.0 || dist > 360.0) {
        std::cerr << "Haversine distance between London and Paris unexpected: " << dist << std::endl;
    }
}

} // namespace GeoSpatialModule
""",
    "extended": """
namespace GeoSpatialModule {

class SpatialCluster {
private:
    std::vector<GeoPoint> points;
public:
    void add(const GeoPoint& pt) { points.push_back(pt); }
    GeoPoint centroid() const {
        if (points.empty()) return {0.0, 0.0};
        double sum_lat = 0, sum_lon = 0;
        for (const auto& p : points) {
            sum_lat += p.latitude;
            sum_lon += p.longitude;
        }
        return {sum_lat / points.size(), sum_lon / points.size()};
    }
};

} // namespace GeoSpatialModule
"""
}
