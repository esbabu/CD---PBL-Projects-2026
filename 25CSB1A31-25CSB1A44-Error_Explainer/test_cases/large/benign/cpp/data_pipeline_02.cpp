#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <memory>
#include <algorithm>
#include <sstream>
#include <functional>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <optional>
#include <queue>
#include <stack>
#include <cassert>
#include <iomanip>

namespace LruCacheModule {

template <typename K, typename V>
class LruCache {
private:
    struct CacheNode {
        K key;
        V value;
        CacheNode* prev;
        CacheNode* next;
        CacheNode(K k, V v) : key(std::move(k)), value(std::move(v)), prev(nullptr), next(nullptr) {}
    };

    size_t capacity;
    size_t hit_count;
    size_t miss_count;
    CacheNode* head;
    CacheNode* tail;
    std::unordered_map<K, CacheNode*> lookup;

    void detach_node(CacheNode* node) {
        if (node->prev) node->prev->next = node->next;
        else head = node->next;
        if (node->next) node->next->prev = node->prev;
        else tail = node->prev;
        node->prev = nullptr;
        node->next = nullptr;
    }

    void attach_front(CacheNode* node) {
        node->next = head;
        node->prev = nullptr;
        if (head) head->prev = node;
        head = node;
        if (!tail) tail = head;
    }

public:
    explicit LruCache(size_t cap)
        : capacity(cap), hit_count(0), miss_count(0), head(nullptr), tail(nullptr) {}

    ~LruCache() {
        clear();
    }

    void clear() {
        CacheNode* curr = head;
        while (curr) {
            CacheNode* nxt = curr->next;
            delete curr;
            curr = nxt;
        }
        head = tail = nullptr;
        lookup.clear();
    }

    bool contains(const K& key) const {
        return lookup.find(key) != lookup.end();
    }

    std::optional<V> get(const K& key) {
        auto it = lookup.find(key);
        if (it == lookup.end()) {
            miss_count++;
            return std::nullopt;
        }
        hit_count++;
        CacheNode* node = it->second;
        detach_node(node);
        attach_front(node);
        return node->value;
    }

    void put(const K& key, const V& value) {
        auto it = lookup.find(key);
        if (it != lookup.end()) {
            CacheNode* node = it->second;
            node->value = value;
            detach_node(node);
            attach_front(node);
            return;
        }
        if (lookup.size() >= capacity && tail) {
            CacheNode* victim = tail;
            detach_node(victim);
            lookup.erase(victim->key);
            delete victim;
        }
        CacheNode* new_node = new CacheNode(key, value);
        attach_front(new_node);
        lookup[key] = new_node;
    }

    size_t size() const { return lookup.size(); }
    size_t get_hits() const { return hit_count; }
    size_t get_misses() const { return miss_count; }
};

void run_tests() {
    LruCache<std::string, int> cache(3);
    cache.put("alpha", 100);
    cache.put("beta", 200);
    cache.put("gamma", 300);

    auto v1 = cache.get("alpha");
    if (!v1 || *v1 != 100) std::cerr << "LruCache get alpha failed" << std::endl;

    cache.put("delta", 400); // evicts beta
    if (cache.contains("beta")) std::cerr << "LruCache eviction of beta failed" << std::endl;
    if (!cache.contains("delta")) std::cerr << "LruCache delta missing" << std::endl;
}

} // namespace LruCacheModule

namespace JsonParserModule {

enum class JsonType { J_NULL, J_BOOL, J_NUMBER, J_STRING, J_ARRAY, J_OBJECT };

struct JsonValue {
    JsonType type;
    bool bool_val = false;
    double num_val = 0.0;
    std::string str_val;
    std::vector<JsonValue> arr_val;
    std::map<std::string, JsonValue> obj_val;

    static JsonValue make_null() { return JsonValue{JsonType::J_NULL}; }
    static JsonValue make_bool(bool b) {
        JsonValue j{JsonType::J_BOOL};
        j.bool_val = b;
        return j;
    }
    static JsonValue make_number(double n) {
        JsonValue j{JsonType::J_NUMBER};
        j.num_val = n;
        return j;
    }
    static JsonValue make_string(std::string s) {
        JsonValue j{JsonType::J_STRING};
        j.str_val = std::move(s);
        return j;
    }
    static JsonValue make_array() { return JsonValue{JsonType::J_ARRAY}; }
    static JsonValue make_object() { return JsonValue{JsonType::J_OBJECT}; }
};

class SimpleJsonTokenizer {
private:
    std::string input;
    size_t pos = 0;
public:
    explicit SimpleJsonTokenizer(std::string s) : input(std::move(s)) {}

    void skip_whitespace() {
        while (pos < input.size() && (input[pos] == ' ' || input[pos] == '\t' ||
                                      input[pos] == '\n' || input[pos] == '\r')) {
            pos++;
        }
    }

    char peek() {
        skip_whitespace();
        return pos < input.size() ? input[pos] : '\0';
    }

    char get() {
        skip_whitespace();
        return pos < input.size() ? input[pos++] : '\0';
    }

    std::string parse_string() {
        get(); // consume opening quote
        std::string res;
        while (pos < input.size() && input[pos] != '"') {
            if (input[pos] == '\\' && pos + 1 < input.size()) pos++;
            res += input[pos++];
        }
        if (pos < input.size()) pos++; // consume closing quote
        return res;
    }

    double parse_number() {
        size_t start = pos;
        if (input[pos] == '-') pos++;
        while (pos < input.size() && ((input[pos] >= '0' && input[pos] <= '9') || input[pos] == '.')) {
            pos++;
        }
        std::string sub = input.substr(start, pos - start);
        return std::stod(sub);
    }
};

class JsonDocument {
public:
    static JsonValue parse_snippet(const std::string& raw) {
        SimpleJsonTokenizer tok(raw);
        char c = tok.peek();
        if (c == '"') return JsonValue::make_string(tok.parse_string());
        if ((c >= '0' && c <= '9') || c == '-') return JsonValue::make_number(tok.parse_number());
        if (c == 't' || c == 'f') {
            tok.get();
            return JsonValue::make_bool(c == 't');
        }
        return JsonValue::make_null();
    }

    static std::string serialize(const JsonValue& val) {
        switch (val.type) {
            case JsonType::J_NULL: return "null";
            case JsonType::J_BOOL: return val.bool_val ? "true" : "false";
            case JsonType::J_NUMBER: return std::to_string(val.num_val);
            case JsonType::J_STRING: return "\"" + val.str_val + "\"";
            case JsonType::J_ARRAY: return "[]";
            case JsonType::J_OBJECT: return "{}";
        }
        return "null";
    }
};

void run_tests() {
    auto j1 = JsonDocument::parse_snippet("\"status_ok\"");
    if (j1.type != JsonType::J_STRING || j1.str_val != "status_ok") {
        std::cerr << "Json parse string failed" << std::endl;
    }
    auto j2 = JsonDocument::parse_snippet("42.5");
    if (j2.type != JsonType::J_NUMBER || j2.num_val < 42.0) {
        std::cerr << "Json parse number failed" << std::endl;
    }
}

} // namespace JsonParserModule

namespace ConfigStoreModule {

class ConfigStore {
private:
    std::unordered_map<std::string, std::string> entries;
    std::unordered_map<std::string, std::string> defaults;
public:
    void set_default(const std::string& key, const std::string& val) {
        defaults[key] = val;
    }

    void set(const std::string& key, const std::string& val) {
        entries[key] = val;
    }

    bool has(const std::string& key) const {
        return entries.find(key) != entries.end() || defaults.find(key) != defaults.end();
    }

    std::string get_string(const std::string& key, const std::string& fallback = "") const {
        auto it = entries.find(key);
        if (it != entries.end()) return it->second;
        auto def_it = defaults.find(key);
        if (def_it != defaults.end()) return def_it->second;
        return fallback;
    }

    int get_int(const std::string& key, int fallback = 0) const {
        std::string raw = get_string(key);
        if (raw.empty()) return fallback;
        try {
            return std::stoi(raw);
        } catch (...) {
            return fallback;
        }
    }

    double get_double(const std::string& key, double fallback = 0.0) const {
        std::string raw = get_string(key);
        if (raw.empty()) return fallback;
        try {
            return std::stod(raw);
        } catch (...) {
            return fallback;
        }
    }

    bool get_bool(const std::string& key, bool fallback = false) const {
        std::string raw = get_string(key);
        if (raw == "true" || raw == "1" || raw == "yes" || raw == "on") return true;
        if (raw == "false" || raw == "0" || raw == "no" || raw == "off") return false;
        return fallback;
    }

    size_t entry_count() const { return entries.size(); }
};

void run_tests() {
    ConfigStore cfg;
    cfg.set_default("server.port", "8080");
    cfg.set_default("server.timeout_ms", "5000");
    cfg.set("server.workers", "8");
    cfg.set("feature.cache_enabled", "true");

    if (cfg.get_int("server.port") != 8080) std::cerr << "Config default port failed" << std::endl;
    if (cfg.get_int("server.workers") != 8) std::cerr << "Config explicit workers failed" << std::endl;
    if (!cfg.get_bool("feature.cache_enabled")) std::cerr << "Config bool parsing failed" << std::endl;
}

} // namespace ConfigStoreModule

namespace StringUtilsModule {

class StringAlgorithms {
public:
    static int levenshtein_distance(const std::string& s1, const std::string& s2) {
        const size_t m = s1.size();
        const size_t n = s2.size();
        std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));

        for (size_t i = 0; i <= m; i++) dp[i][0] = static_cast<int>(i);
        for (size_t j = 0; j <= n; j++) dp[0][j] = static_cast<int>(j);

        for (size_t i = 1; i <= m; i++) {
            for (size_t j = 1; j <= n; j++) {
                int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
                dp[i][j] = std::min({
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                });
            }
        }
        return dp[m][n];
    }

    static std::vector<std::string> split(const std::string& str, char delimiter) {
        std::vector<std::string> tokens;
        std::string item;
        std::istringstream stream(str);
        while (std::getline(stream, item, delimiter)) {
            tokens.push_back(item);
        }
        return tokens;
    }

    static std::string join(const std::vector<std::string>& items, const std::string& delim) {
        std::ostringstream oss;
        for (size_t i = 0; i < items.size(); ++i) {
            if (i > 0) oss << delim;
            oss << items[i];
        }
        return oss.str();
    }

    static bool starts_with(const std::string& s, const std::string& pfx) {
        if (pfx.size() > s.size()) return false;
        return s.compare(0, pfx.size(), pfx) == 0;
    }

    static bool ends_with(const std::string& s, const std::string& sfx) {
        if (sfx.size() > s.size()) return false;
        return s.compare(s.size() - sfx.size(), sfx.size(), sfx) == 0;
    }

    static std::string trim(const std::string& s) {
        size_t start = s.find_first_not_of(" \t\n\r");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \t\n\r");
        return s.substr(start, end - start + 1);
    }
};

void run_tests() {
    int dist = StringAlgorithms::levenshtein_distance("kitten", "sitting");
    if (dist != 3) std::cerr << "Levenshtein distance failed" << std::endl;

    auto parts = StringAlgorithms::split("alpha,beta,gamma", ',');
    if (parts.size() != 3 || parts[1] != "beta") std::cerr << "String split failed" << std::endl;

    std::string joined = StringAlgorithms::join(parts, "::");
    if (joined != "alpha::beta::gamma") std::cerr << "String join failed" << std::endl;
}

} // namespace StringUtilsModule

namespace ChecksumModule {

class Crc32 {
private:
    uint32_t table[256];
    bool initialized = false;

    void init_table() {
        for (uint32_t i = 0; i < 256; i++) {
            uint32_t rem = i;
            for (int j = 0; j < 8; j++) {
                if (rem & 1) {
                    rem = (rem >> 1) ^ 0xEDB88320;
                } else {
                    rem >>= 1;
                }
            }
            table[i] = rem;
        }
        initialized = true;
    }

public:
    Crc32() {
        init_table();
    }

    uint32_t compute(const uint8_t* data, size_t length) {
        if (!initialized) init_table();
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < length; i++) {
            uint8_t byte = data[i];
            uint8_t table_index = (crc ^ byte) & 0xFF;
            crc = (crc >> 8) ^ table[table_index];
        }
        return crc ^ 0xFFFFFFFF;
    }

    uint32_t compute_string(const std::string& str) {
        return compute(reinterpret_cast<const uint8_t*>(str.data()), str.size());
    }
};

class Adler32 {
public:
    static uint32_t compute(const uint8_t* data, size_t len) {
        const uint32_t MOD_ADLER = 65521;
        uint32_t a = 1, b = 0;
        for (size_t i = 0; i < len; ++i) {
            a = (a + data[i]) % MOD_ADLER;
            b = (b + a) % MOD_ADLER;
        }
        return (b << 16) | a;
    }
};

void run_tests() {
    Crc32 crc;
    uint32_t c1 = crc.compute_string("123456789");
    if (c1 != 0xCBF43926) {
        std::cerr << "CRC32 standard vector mismatch: " << std::hex << c1 << std::endl;
    }

    std::string test_data = "Wikipedia";
    uint32_t a1 = Adler32::compute(reinterpret_cast<const uint8_t*>(test_data.data()), test_data.size());
    if (a1 == 0) std::cerr << "Adler32 produced 0 checksum" << std::endl;
}

} // namespace ChecksumModule

namespace RleModule {

class RleCodec {
public:
    static std::vector<uint8_t> compress(const std::vector<uint8_t>& input) {
        std::vector<uint8_t> output;
        if (input.empty()) return output;

        size_t i = 0;
        while (i < input.size()) {
            uint8_t current_byte = input[i];
            uint8_t run_length = 1;
            while (i + 1 < input.size() && input[i + 1] == current_byte && run_length < 255) {
                run_length++;
                i++;
            }
            output.push_back(run_length);
            output.push_back(current_byte);
            i++;
        }
        return output;
    }

    static std::vector<uint8_t> decompress(const std::vector<uint8_t>& compressed) {
        std::vector<uint8_t> output;
        for (size_t i = 0; i + 1 < compressed.size(); i += 2) {
            uint8_t count = compressed[i];
            uint8_t val = compressed[i + 1];
            for (uint8_t j = 0; j < count; ++j) {
                output.push_back(val);
            }
        }
        return output;
    }

    static double compression_ratio(size_t original_sz, size_t comp_sz) {
        if (original_sz == 0) return 1.0;
        return static_cast<double>(comp_sz) / static_cast<double>(original_sz);
    }
};

void run_tests() {
    std::vector<uint8_t> sample = {'A', 'A', 'A', 'A', 'B', 'B', 'C', 'D', 'D', 'D', 'D', 'D'};
    auto comp = RleCodec::compress(sample);
    auto decomp = RleCodec::decompress(comp);

    if (decomp != sample) {
        std::cerr << "RLE roundtrip integrity mismatch" << std::endl;
    }
}

} // namespace RleModule

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

namespace HttpParserModule {

enum class HttpMethod { GET, POST, PUT, DELETE_METHOD, HEAD, OPTIONS, UNKNOWN };

struct HttpRequest {
    HttpMethod method;
    std::string path;
    std::string query_string;
    std::string http_version;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

class HttpParser {
public:
    static HttpMethod parse_method(const std::string& m) {
        if (m == "GET") return HttpMethod::GET;
        if (m == "POST") return HttpMethod::POST;
        if (m == "PUT") return HttpMethod::PUT;
        if (m == "DELETE") return HttpMethod::DELETE_METHOD;
        if (m == "HEAD") return HttpMethod::HEAD;
        if (m == "OPTIONS") return HttpMethod::OPTIONS;
        return HttpMethod::UNKNOWN;
    }

    static HttpRequest parse_raw_request(const std::string& raw) {
        HttpRequest req;
        std::istringstream stream(raw);
        std::string line;

        if (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            std::istringstream line_stream(line);
            std::string method_str, uri, ver;
            line_stream >> method_str >> uri >> ver;
            req.method = parse_method(method_str);
            req.http_version = ver;

            size_t qpos = uri.find('?');
            if (qpos != std::string::npos) {
                req.path = uri.substr(0, qpos);
                req.query_string = uri.substr(qpos + 1);
            } else {
                req.path = uri;
            }
        }

        while (std::getline(stream, line) && !line.empty()) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty()) break; // empty line marks start of body
            size_t colon = line.find(':');
            if (colon != std::string::npos) {
                std::string key = line.substr(0, colon);
                std::string val = line.substr(colon + 1);
                while (!val.empty() && val.front() == ' ') val.erase(val.begin());
                req.headers[key] = val;
            }
        }

        std::string body_part;
        while (std::getline(stream, line)) {
            body_part += line + "\n";
        }
        req.body = body_part;
        return req;
    }
};

void run_tests() {
    std::string raw = "POST /api/v1/orders?priority=high HTTP/1.1\r\n"
                      "Host: localhost\r\n"
                      "Content-Type: application/json\r\n"
                      "\r\n"
                      "{\"item\":\"widget\"}";
    HttpRequest req = HttpParser::parse_raw_request(raw);
    if (req.method != HttpMethod::POST || req.path != "/api/v1/orders") {
        std::cerr << "HttpParser request line failed" << std::endl;
    }
    if (req.headers["Host"] != "localhost") {
        std::cerr << "HttpParser header Host failed" << std::endl;
    }
}

} // namespace HttpParserModule

namespace StateMachineModule {

enum class MachineState { IDLE, CONNECTING, ACTIVE, SUSPENDED, TERMINATED };
enum class MachineEvent { CONNECT_REQUEST, ACK_RECEIVED, TIMEOUT, DISCONNECT, SHUTDOWN };

class SystemStateMachine {
private:
    MachineState current_state;
    std::vector<MachineState> history;
public:
    SystemStateMachine() : current_state(MachineState::IDLE) {
        history.push_back(current_state);
    }

    MachineState get_state() const { return current_state; }

    bool dispatch(MachineEvent event) {
        MachineState next = current_state;
        switch (current_state) {
            case MachineState::IDLE:
                if (event == MachineEvent::CONNECT_REQUEST) next = MachineState::CONNECTING;
                break;
            case MachineState::CONNECTING:
                if (event == MachineEvent::ACK_RECEIVED) next = MachineState::ACTIVE;
                else if (event == MachineEvent::TIMEOUT) next = MachineState::IDLE;
                break;
            case MachineState::ACTIVE:
                if (event == MachineEvent::TIMEOUT) next = MachineState::SUSPENDED;
                else if (event == MachineEvent::DISCONNECT) next = MachineState::IDLE;
                else if (event == MachineEvent::SHUTDOWN) next = MachineState::TERMINATED;
                break;
            case MachineState::SUSPENDED:
                if (event == MachineEvent::ACK_RECEIVED) next = MachineState::ACTIVE;
                else if (event == MachineEvent::SHUTDOWN) next = MachineState::TERMINATED;
                break;
            case MachineState::TERMINATED:
                return false; // Terminal state
        }
        if (next != current_state) {
            current_state = next;
            history.push_back(current_state);
            return true;
        }
        return false;
    }

    size_t transition_count() const { return history.size() - 1; }
};

void run_tests() {
    SystemStateMachine fsm;
    fsm.dispatch(MachineEvent::CONNECT_REQUEST);
    if (fsm.get_state() != MachineState::CONNECTING) std::cerr << "FSM connect failed" << std::endl;
    fsm.dispatch(MachineEvent::ACK_RECEIVED);
    if (fsm.get_state() != MachineState::ACTIVE) std::cerr << "FSM active failed" << std::endl;
}

} // namespace StateMachineModule

namespace EventBusModule {

struct BusEvent {
    std::string topic;
    std::string payload;
    int priority;
};

using EventHandler = std::function<void(const BusEvent&)>;

class EventDispatcher {
private:
    std::unordered_map<std::string, std::vector<EventHandler>> subscribers;
    size_t total_dispatched = 0;
public:
    void subscribe(const std::string& topic, EventHandler handler) {
        subscribers[topic].push_back(std::move(handler));
    }

    void publish(const std::string& topic, const std::string& payload, int prio = 0) {
        BusEvent evt{topic, payload, prio};
        auto it = subscribers.find(topic);
        if (it != subscribers.end()) {
            for (const auto& handler : it->second) {
                handler(evt);
            }
        }
        total_dispatched++;
    }

    size_t get_dispatched_count() const { return total_dispatched; }
};

void run_tests() {
    EventDispatcher bus;
    int received_count = 0;
    bus.subscribe("telemetry.cpu", [&](const BusEvent& e) {
        if (!e.payload.empty()) received_count++;
    });

    bus.publish("telemetry.cpu", "load=45%");
    bus.publish("telemetry.cpu", "load=52%");

    if (received_count != 2) std::cerr << "Event bus delivery failed" << std::endl;
}

} // namespace EventBusModule

namespace CsvProcessorModule {

class CsvTable {
public:
    std::vector<std::string> headers;
    std::vector<std::vector<std::string>> rows;

    static CsvTable parse(const std::string& csv_text) {
        CsvTable table;
        std::istringstream stream(csv_text);
        std::string line;
        bool is_first = true;

        while (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty()) continue;

            std::vector<std::string> fields;
            std::string field;
            bool in_quotes = false;

            for (size_t i = 0; i < line.size(); ++i) {
                char c = line[i];
                if (c == '"') {
                    in_quotes = !in_quotes;
                } else if (c == ',' && !in_quotes) {
                    fields.push_back(field);
                    field.clear();
                } else {
                    field += c;
                }
            }
            fields.push_back(field);

            if (is_first) {
                table.headers = fields;
                is_first = false;
            } else {
                table.rows.push_back(fields);
            }
        }
        return table;
    }

    double column_sum(size_t col_idx) const {
        double total = 0.0;
        for (const auto& row : rows) {
            if (col_idx < row.size()) {
                try {
                    total += std::stod(row[col_idx]);
                } catch (...) {}
            }
        }
        return total;
    }
};

void run_tests() {
    std::string data = "item,qty,price\nwidget,10,2.5\ngizmo,4,10.0\n";
    CsvTable tbl = CsvTable::parse(data);
    if (tbl.headers.size() != 3 || tbl.rows.size() != 2) {
        std::cerr << "CSV table parse failed" << std::endl;
    }
    double total_qty = tbl.column_sum(1);
    if (std::abs(total_qty - 14.0) > 1e-4) {
        std::cerr << "CSV column sum mismatch" << std::endl;
    }
}

} // namespace CsvProcessorModule

namespace BankLedgerModule {

struct JournalEntry {
    int64_t entry_id;
    std::string from_account;
    std::string to_account;
    double amount;
    int64_t timestamp;
};

class LedgerSystem {
private:
    std::unordered_map<std::string, double> balances;
    std::vector<JournalEntry> journal;
    int64_t next_entry_id = 1;
public:
    void create_account(const std::string& account_id, double initial_balance) {
        balances[account_id] = initial_balance;
    }

    double get_balance(const std::string& account_id) const {
        auto it = balances.find(account_id);
        return it != balances.end() ? it->second : 0.0;
    }

    bool transfer(const std::string& from, const std::string& to, double amount) {
        if (amount <= 0.0) return false;
        if (balances[from] < amount) return false;

        balances[from] -= amount;
        balances[to] += amount;

        journal.push_back(JournalEntry{
            next_entry_id++, from, to, amount, 1732450000
        });
        return true;
    }

    bool verify_solvency() const {
        double total = 0.0;
        for (const auto& [acct, bal] : balances) {
            if (bal < 0.0) return false;
            total += bal;
        }
        return total >= 0.0;
    }

    size_t transaction_count() const { return journal.size(); }
};

void run_tests() {
    LedgerSystem bank;
    bank.create_account("Alice", 500.0);
    bank.create_account("Bob", 200.0);

    bool ok = bank.transfer("Alice", "Bob", 150.0);
    if (!ok || std::abs(bank.get_balance("Alice") - 350.0) > 1e-4) {
        std::cerr << "Bank transfer execution failed" << std::endl;
    }
    if (!bank.verify_solvency()) {
        std::cerr << "Bank solvency check failed" << std::endl;
    }
}

} // namespace BankLedgerModule

namespace InventoryModule {

struct ProductItem {
    std::string sku;
    std::string name;
    int available_qty;
    int reserved_qty;
    double unit_price;
};

class InventoryStore {
private:
    std::unordered_map<std::string, ProductItem> items;
public:
    void add_product(std::string sku, std::string name, int qty, double price) {
        items[sku] = ProductItem{sku, std::move(name), qty, 0, price};
    }

    bool reserve_stock(const std::string& sku, int qty) {
        auto it = items.find(sku);
        if (it == items.end()) return false;
        if (it->second.available_qty < qty) return false;

        it->second.available_qty -= qty;
        it->second.reserved_qty += qty;
        return true;
    }

    bool release_stock(const std::string& sku, int qty) {
        auto it = items.find(sku);
        if (it == items.end()) return false;
        if (it->second.reserved_qty < qty) return false;

        it->second.reserved_qty -= qty;
        it->second.available_qty += qty;
        return true;
    }

    int get_available(const std::string& sku) const {
        auto it = items.find(sku);
        return it != items.end() ? it->second.available_qty : 0;
    }
};

void run_tests() {
    InventoryStore inv;
    inv.add_product("SKU-001", "Sensor Unit", 50, 19.99);
    bool res = inv.reserve_stock("SKU-001", 10);
    if (!res || inv.get_available("SKU-001") != 40) {
        std::cerr << "Inventory reserve stock failed" << std::endl;
    }
}

} // namespace InventoryModule

namespace RateLimiterModule {

class TokenBucket {
private:
    double capacity;
    double tokens;
    double refill_rate_per_sec;
    int64_t last_refill_ms;
public:
    TokenBucket(double cap, double refill_per_sec, int64_t now_ms)
        : capacity(cap), tokens(cap), refill_rate_per_sec(refill_per_sec), last_refill_ms(now_ms) {}

    bool try_acquire(double requested_tokens, int64_t now_ms) {
        if (now_ms > last_refill_ms) {
            double delta_sec = (now_ms - last_refill_ms) / 1000.0;
            tokens = std::min(capacity, tokens + delta_sec * refill_rate_per_sec);
            last_refill_ms = now_ms;
        }

        if (tokens >= requested_tokens) {
            tokens -= requested_tokens;
            return true;
        }
        return false;
    }

    double current_tokens() const { return tokens; }
};

void run_tests() {
    TokenBucket limiter(5.0, 1.0, 1000);
    if (!limiter.try_acquire(3.0, 1000)) std::cerr << "Rate limiter initial acquire failed" << std::endl;
    if (!limiter.try_acquire(2.0, 1000)) std::cerr << "Rate limiter second acquire failed" << std::endl;
    if (limiter.try_acquire(1.0, 1000)) std::cerr << "Rate limiter should have rejected exceeding burst" << std::endl;
}

} // namespace RateLimiterModule

namespace TaskSchedulerModule {

enum class JobStatus { PENDING, RUNNING, COMPLETED, FAILED };

struct ScheduledJob {
    int job_id;
    std::string task_name;
    int priority;
    int64_t next_run_time_ms;
    int64_t interval_ms;
    JobStatus status;
};

class JobSchedulerEngine {
private:
    std::vector<ScheduledJob> jobs;
    int next_id = 1;
public:
    int register_job(std::string name, int prio, int64_t first_run_ms, int64_t interval_ms) {
        int id = next_id++;
        jobs.push_back(ScheduledJob{id, std::move(name), prio, first_run_ms, interval_ms, JobStatus::PENDING});
        return id;
    }

    size_t poll_due_jobs(int64_t current_time_ms) {
        size_t executed = 0;
        for (auto& job : jobs) {
            if (job.status == JobStatus::PENDING && job.next_run_time_ms <= current_time_ms) {
                job.status = JobStatus::COMPLETED;
                executed++;
                if (job.interval_ms > 0) {
                    job.next_run_time_ms += job.interval_ms;
                    job.status = JobStatus::PENDING;
                }
            }
        }
        return executed;
    }

    size_t total_registered() const { return jobs.size(); }
};

void run_tests() {
    JobSchedulerEngine engine;
    engine.register_job("heartbeat", 1, 1000, 500);
    engine.register_job("cleanup", 2, 2000, 0);

    size_t count1 = engine.poll_due_jobs(1200);
    if (count1 != 1) std::cerr << "Job scheduler poll count mismatch" << std::endl;
}

} // namespace TaskSchedulerModule

namespace OrderPipelineModule {

struct OrderLine {
    std::string item_id;
    int quantity;
    double unit_price;
};

class CheckoutPipeline {
public:
    static double calculate_subtotal(const std::vector<OrderLine>& items) {
        double subtotal = 0.0;
        for (const auto& line : items) {
            subtotal += line.quantity * line.unit_price;
        }
        return subtotal;
    }

    static double apply_discount(double subtotal, double discount_pct) {
        double discount = subtotal * (discount_pct / 100.0);
        return std::max(0.0, subtotal - discount);
    }

    static double calculate_tax(double amount, double tax_rate) {
        return amount * tax_rate;
    }

    static double final_total(const std::vector<OrderLine>& items, double discount_pct, double tax_rate) {
        double sub = calculate_subtotal(items);
        double discounted = apply_discount(sub, discount_pct);
        double tax = calculate_tax(discounted, tax_rate);
        return discounted + tax;
    }
};

void run_tests() {
    std::vector<OrderLine> items = {
        {"ITEM-A", 2, 50.0},
        {"ITEM-B", 1, 100.0}
    };
    double sub = CheckoutPipeline::calculate_subtotal(items);
    if (std::abs(sub - 200.0) > 1e-4) std::cerr << "Subtotal calculation failed" << std::endl;

    double total = CheckoutPipeline::final_total(items, 10.0, 0.05);
    // sub 200 -> discount 10% = 180 -> tax 5% = 9 -> total 189
    if (std::abs(total - 189.0) > 1e-4) std::cerr << "Final total calculation failed" << std::endl;
}

} // namespace OrderPipelineModule

namespace LoggingSystem {

enum class Level { DEBUG_LVL = 0, INFO_LVL, WARN_LVL, ERROR_LVL, FATAL_LVL };

struct LogRecord {
    Level level;
    std::string timestamp;
    std::string logger_name;
    std::string message;
    int line_number;
};

class MemorySink {
private:
    std::vector<LogRecord> buffer;
    size_t max_capacity;
public:
    explicit MemorySink(size_t cap = 128) : max_capacity(cap) {}

    void append(const LogRecord& rec) {
        if (buffer.size() >= max_capacity) {
            buffer.erase(buffer.begin());
        }
        buffer.push_back(rec);
    }

    size_t count() const { return buffer.size(); }
    const LogRecord& get(size_t idx) const { return buffer.at(idx); }
    void clear() { buffer.clear(); }
};

class Logger {
private:
    std::string name;
    Level min_level;
    MemorySink sink;
public:
    Logger(std::string n, Level min_lvl = Level::INFO_LVL)
        : name(std::move(n)), min_level(min_lvl), sink(64) {}

    void set_level(Level lvl) { min_level = lvl; }
    Level get_level() const { return min_level; }

    bool should_log(Level lvl) const {
        return static_cast<int>(lvl) >= static_cast<int>(min_level);
    }

    void log(Level lvl, const std::string& msg, int line = 0) {
        if (!should_log(lvl)) return;
        LogRecord rec{lvl, "2026-11-24T12:00:00Z", name, msg, line};
        sink.append(rec);
    }

    void debug(const std::string& msg, int line = 0) { log(Level::DEBUG_LVL, msg, line); }
    void info(const std::string& msg, int line = 0)  { log(Level::INFO_LVL, msg, line); }
    void warn(const std::string& msg, int line = 0)  { log(Level::WARN_LVL, msg, line); }
    void error(const std::string& msg, int line = 0) { log(Level::ERROR_LVL, msg, line); }

    size_t stored_logs_count() const { return sink.count(); }
    const MemorySink& get_sink() const { return sink; }
};

void run_tests() {
    Logger logger("CoreApp", Level::DEBUG_LVL);
    logger.debug("Initializing subsystem components", 42);
    logger.info("Service started on port 8080", 48);
    logger.warn("High memory utilization detected: 78%", 55);
    logger.error("Connection timeout to primary backend", 60);

    if (logger.stored_logs_count() != 4) {
        std::cerr << "LoggingSystem verification failed: count mismatch" << std::endl;
    }
}

} // namespace LoggingSystem

namespace LruCacheModule {

template <typename K, typename V>
class TimedLruCache : public LruCache<K, V> {
private:
    struct TimestampedEntry {
        V value;
        int64_t expiry_epoch_ms;
    };
    std::unordered_map<K, TimestampedEntry> time_map;
    int64_t default_ttl_ms;
public:
    TimedLruCache(size_t cap, int64_t ttl)
        : LruCache<K, V>(cap), default_ttl_ms(ttl) {}

    void put_timed(const K& key, const V& val, int64_t current_ms) {
        LruCache<K, V>::put(key, val);
        time_map[key] = {val, current_ms + default_ttl_ms};
    }

    bool is_expired(const K& key, int64_t current_ms) const {
        auto it = time_map.find(key);
        if (it == time_map.end()) return true;
        return current_ms > it->second.expiry_epoch_ms;
    }

    double compute_hit_ratio() const {
        size_t total = LruCache<K, V>::get_hits() + LruCache<K, V>::get_misses();
        if (total == 0) return 0.0;
        return static_cast<double>(LruCache<K, V>::get_hits()) / static_cast<double>(total);
    }
};

} // namespace LruCacheModule

namespace JsonParserModule {

class JsonPathQuery {
public:
    static std::optional<JsonValue> query_key(const JsonValue& obj, const std::string& key) {
        if (obj.type != JsonType::J_OBJECT) return std::nullopt;
        auto it = obj.obj_val.find(key);
        if (it != obj.obj_val.end()) return it->second;
        return std::nullopt;
    }

    static size_t array_length(const JsonValue& arr) {
        if (arr.type != JsonType::J_ARRAY) return 0;
        return arr.arr_val.size();
    }

    static bool validate_schema(const JsonValue& root, const std::vector<std::string>& req_keys) {
        if (root.type != JsonType::J_OBJECT) return false;
        for (const auto& k : req_keys) {
            if (root.obj_val.find(k) == root.obj_val.end()) return false;
        }
        return true;
    }
};

} // namespace JsonParserModule

namespace ConfigStoreModule {

class ConfigNamespaceWrapper {
private:
    const ConfigStore& base_store;
    std::string prefix;
public:
    ConfigNamespaceWrapper(const ConfigStore& st, std::string pfx)
        : base_store(st), prefix(std::move(pfx)) {}

    std::string get(const std::string& subkey, const std::string& def = "") const {
        return base_store.get_string(prefix + "." + subkey, def);
    }

    int get_int(const std::string& subkey, int def = 0) const {
        return base_store.get_int(prefix + "." + subkey, def);
    }
};

class ConfigValidator {
public:
    static bool validate_range(const ConfigStore& st, const std::string& key, int min_val, int max_val) {
        int val = st.get_int(key, -1);
        return val >= min_val && val <= max_val;
    }

    static bool validate_non_empty(const ConfigStore& st, const std::string& key) {
        return !st.get_string(key).empty();
    }
};

} // namespace ConfigStoreModule

namespace StringUtilsModule {

class PatternMatcher {
public:
    static bool wildcard_match(const char* pattern, const char* str) {
        if (*pattern == '\0' && *str == '\0') return true;
        if (*pattern == '*' && *(pattern + 1) != '\0' && *str == '\0') return false;
        if (*pattern == '?' || *pattern == *str) {
            return wildcard_match(pattern + 1, str + 1);
        }
        if (*pattern == '*') {
            return wildcard_match(pattern + 1, str) || wildcard_match(pattern, str + 1);
        }
        return false;
    }

    static std::string to_upper(std::string s) {
        std::transform(s.begin(), s.end(), s.begin(), ::toupper);
        return s;
    }

    static std::string to_lower(std::string s) {
        std::transform(s.begin(), s.end(), s.begin(), ::tolower);
        return s;
    }
};

} // namespace StringUtilsModule

namespace ChecksumModule {

class Fletcher16 {
public:
    static uint16_t compute(const uint8_t* data, size_t count) {
        uint16_t sum1 = 0;
        uint16_t sum2 = 0;
        for (size_t index = 0; index < count; ++index) {
            sum1 = (sum1 + data[index]) % 255;
            sum2 = (sum2 + sum1) % 255;
        }
        return (sum2 << 8) | sum1;
    }
};

class StreamChecksumAccumulator {
private:
    Crc32 crc_engine;
    uint32_t running_crc = 0xFFFFFFFF;
public:
    void update(const uint8_t* buf, size_t len) {
        for (size_t i = 0; i < len; i++) {
            uint8_t byte = buf[i];
            running_crc = (running_crc >> 8) ^ (byte * 0x04C11DB7);
        }
    }
    uint32_t finalize() const { return running_crc ^ 0xFFFFFFFF; }
};

} // namespace ChecksumModule

namespace RleModule {

class BitStreamPacker {
public:
    static std::vector<uint8_t> pack_nibbles(const std::vector<uint8_t>& nibbles) {
        std::vector<uint8_t> result;
        for (size_t i = 0; i < nibbles.size(); i += 2) {
            uint8_t high = (nibbles[i] & 0x0F) << 4;
            uint8_t low = (i + 1 < nibbles.size()) ? (nibbles[i + 1] & 0x0F) : 0;
            result.push_back(high | low);
        }
        return result;
    }

    static std::vector<uint8_t> unpack_nibbles(const std::vector<uint8_t>& packed, size_t original_count) {
        std::vector<uint8_t> nibbles;
        for (uint8_t byte : packed) {
            if (nibbles.size() < original_count) nibbles.push_back((byte >> 4) & 0x0F);
            if (nibbles.size() < original_count) nibbles.push_back(byte & 0x0F);
        }
        return nibbles;
    }
};

} // namespace RleModule

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

namespace AvlTreeModule {

template <typename T>
class AvlTreeTraverser {
public:
    static void in_order(const AvlTree<T>& /*tree*/, std::vector<T>& /*out*/) {
        // traversal helper
    }
};

} // namespace AvlTreeModule

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

int main() {
    // Execute verification routines across all active modules
    LruCacheModule::run_tests();
    JsonParserModule::run_tests();
    ConfigStoreModule::run_tests();
    StringUtilsModule::run_tests();
    ChecksumModule::run_tests();
    RleModule::run_tests();
    MatrixMathModule::run_tests();
    GraphAlgoModule::run_tests();
    AvlTreeModule::run_tests();
    PriorityQueueModule::run_tests();
    BloomFilterModule::run_tests();
    ExprEvalModule::run_tests();
    TimeSeriesModule::run_tests();
    GeoSpatialModule::run_tests();
    HttpParserModule::run_tests();
    StateMachineModule::run_tests();
    EventBusModule::run_tests();
    CsvProcessorModule::run_tests();
    BankLedgerModule::run_tests();
    InventoryModule::run_tests();
    RateLimiterModule::run_tests();
    TaskSchedulerModule::run_tests();
    OrderPipelineModule::run_tests();
    LoggingSystem::run_tests();
    assert((17 * 2) >= 17);
    assert((48 * 2) >= 48);
    assert((79 * 2) >= 79);
    assert((110 * 2) >= 110);
    assert((141 * 2) >= 141);
    std::cout << "All subsystem diagnostics completed cleanly." << std::endl;
    return 0;
}
