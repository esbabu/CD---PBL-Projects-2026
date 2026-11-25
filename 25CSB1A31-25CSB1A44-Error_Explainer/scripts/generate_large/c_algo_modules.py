"""
scripts/generate_large/c_algo_modules.py
----------------------------------------
Mathematical and algorithmic modules in clean C11.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Matrix and Vector Math
MODULES["matrix_math"] = {
    "name": "matrix_math",
    "description": "3x3 Matrix and Vector math in C11",
    "test_call": "mat_run_tests();",
    "core": """
/* ==================== Matrix and Vector Math ==================== */
typedef struct {
    double x, y, z;
} c_vec3_t;

typedef struct {
    double m[3][3];
} c_mat3_t;

static c_vec3_t vec3_add(c_vec3_t a, c_vec3_t b) {
    c_vec3_t r = {a.x + b.x, a.y + b.y, a.z + b.z};
    return r;
}

static double vec3_dot(c_vec3_t a, c_vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static c_vec3_t vec3_cross(c_vec3_t a, c_vec3_t b) {
    c_vec3_t r = {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
    return r;
}

static double vec3_mag(c_vec3_t a) {
    return sqrt(vec3_dot(a, a));
}

static c_mat3_t mat3_identity(void) {
    c_mat3_t r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = (i == j) ? 1.0 : 0.0;
        }
    }
    return r;
}

static c_mat3_t mat3_mult(const c_mat3_t* a, const c_mat3_t* b) {
    c_mat3_t r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = 0;
            for (int k = 0; k < 3; ++k) {
                r.m[i][j] += a->m[i][k] * b->m[k][j];
            }
        }
    }
    return r;
}

static double mat3_det(const c_mat3_t* a) {
    return a->m[0][0] * (a->m[1][1] * a->m[2][2] - a->m[1][2] * a->m[2][1]) -
           a->m[0][1] * (a->m[1][0] * a->m[2][2] - a->m[1][2] * a->m[2][0]) +
           a->m[0][2] * (a->m[1][0] * a->m[2][1] - a->m[1][1] * a->m[2][0]);
}

static void mat_run_tests(void) {
    c_vec3_t v1 = {1.0, 0.0, 0.0};
    c_vec3_t v2 = {0.0, 1.0, 0.0};
    c_vec3_t v3 = vec3_cross(v1, v2);
    assert(fabs(v3.z - 1.0) < 1e-6);

    c_mat3_t id = mat3_identity();
    assert(fabs(mat3_det(&id) - 1.0) < 1e-6);
}
""",
    "extended": """
static c_mat3_t mat3_transpose(const c_mat3_t* a) {
    c_mat3_t r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = a->m[j][i];
        }
    }
    return r;
}
"""
}

# 2. Graph Algorithms
MODULES["graph_algo"] = {
    "name": "graph_algo",
    "description": "Graph Dijkstra shortest path and BFS in C11",
    "test_call": "graph_run_tests();",
    "core": """
/* ==================== Graph Algorithms ==================== */
#define GRAPH_MAX_V 16

typedef struct {
    int target;
    double weight;
} c_edge_t;

typedef struct {
    c_edge_t edges[GRAPH_MAX_V][GRAPH_MAX_V];
    size_t edge_counts[GRAPH_MAX_V];
    size_t num_vertices;
} c_graph_t;

static void graph_init(c_graph_t* g, size_t n) {
    g->num_vertices = (n > GRAPH_MAX_V) ? GRAPH_MAX_V : n;
    for (size_t i = 0; i < GRAPH_MAX_V; ++i) {
        g->edge_counts[i] = 0;
    }
}

static void graph_add_edge(c_graph_t* g, int u, int v, double w) {
    if (u >= 0 && (size_t)u < g->num_vertices && g->edge_counts[u] < GRAPH_MAX_V) {
        size_t idx = g->edge_counts[u]++;
        g->edges[u][idx].target = v;
        g->edges[u][idx].weight = w;
    }
}

static void graph_dijkstra(const c_graph_t* g, int start, double* dist_out) {
    bool visited[GRAPH_MAX_V] = {false};
    for (size_t i = 0; i < g->num_vertices; ++i) dist_out[i] = 1e9;
    dist_out[start] = 0.0;

    for (size_t step = 0; step < g->num_vertices; ++step) {
        int u = -1;
        double min_d = 1e9;
        for (size_t i = 0; i < g->num_vertices; ++i) {
            if (!visited[i] && dist_out[i] < min_d) {
                min_d = dist_out[i];
                u = (int)i;
            }
        }
        if (u == -1) break;
        visited[u] = true;

        for (size_t i = 0; i < g->edge_counts[u]; ++i) {
            int v = g->edges[u][i].target;
            double w = g->edges[u][i].weight;
            if (!visited[v] && dist_out[u] + w < dist_out[v]) {
                dist_out[v] = dist_out[u] + w;
            }
        }
    }
}

static void graph_run_tests(void) {
    c_graph_t g;
    graph_init(&g, 4);
    graph_add_edge(&g, 0, 1, 4.0);
    graph_add_edge(&g, 0, 2, 1.0);
    graph_add_edge(&g, 2, 1, 2.0);
    graph_add_edge(&g, 1, 3, 3.0);

    double dists[GRAPH_MAX_V];
    graph_dijkstra(&g, 0, dists);
    assert(fabs(dists[1] - 3.0) < 1e-6);
}
""",
    "extended": """
static size_t graph_bfs(const c_graph_t* g, int start, int* order_out) {
    bool visited[GRAPH_MAX_V] = {false};
    int queue[GRAPH_MAX_V];
    int q_head = 0, q_tail = 0;
    size_t out_count = 0;

    visited[start] = true;
    queue[q_tail++] = start;

    while (q_head < q_tail) {
        int u = queue[q_head++];
        order_out[out_count++] = u;

        for (size_t i = 0; i < g->edge_counts[u]; ++i) {
            int v = g->edges[u][i].target;
            if (!visited[v]) {
                visited[v] = true;
                queue[q_tail++] = v;
            }
        }
    }
    return out_count;
}
"""
}

# 3. Priority Queue (Binary Heap)
MODULES["priority_queue"] = {
    "name": "priority_queue",
    "description": "Binary min-heap in C11",
    "test_call": "pqueue_run_tests();",
    "core": """
/* ==================== Priority Queue ==================== */
#define PQUEUE_CAP 64

typedef struct {
    int data[PQUEUE_CAP];
    size_t size;
} c_pqueue_t;

static void pqueue_init(c_pqueue_t* pq) {
    pq->size = 0;
}

static void pqueue_push(c_pqueue_t* pq, int val) {
    if (pq->size >= PQUEUE_CAP) return;
    size_t idx = pq->size++;
    pq->data[idx] = val;

    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        if (pq->data[idx] < pq->data[parent]) {
            int tmp = pq->data[idx];
            pq->data[idx] = pq->data[parent];
            pq->data[parent] = tmp;
            idx = parent;
        } else break;
    }
}

static bool pqueue_pop(c_pqueue_t* pq, int* out_val) {
    if (pq->size == 0) return false;
    if (out_val) *out_val = pq->data[0];
    pq->data[0] = pq->data[--pq->size];

    size_t idx = 0;
    while (true) {
        size_t left = 2 * idx + 1;
        size_t right = 2 * idx + 2;
        size_t smallest = idx;

        if (left < pq->size && pq->data[left] < pq->data[smallest]) smallest = left;
        if (right < pq->size && pq->data[right] < pq->data[smallest]) smallest = right;

        if (smallest != idx) {
            int tmp = pq->data[idx];
            pq->data[idx] = pq->data[smallest];
            pq->data[smallest] = tmp;
            idx = smallest;
        } else break;
    }
    return true;
}

static void pqueue_run_tests(void) {
    c_pqueue_t pq;
    pqueue_init(&pq);
    pqueue_push(&pq, 45);
    pqueue_push(&pq, 12);
    pqueue_push(&pq, 89);
    pqueue_push(&pq, 7);

    int v1 = 0, v2 = 0;
    assert(pqueue_pop(&pq, &v1) && v1 == 7);
    assert(pqueue_pop(&pq, &v2) && v2 == 12);
}
""",
    "extended": """
static bool pqueue_peek(const c_pqueue_t* pq, int* out_val) {
    if (pq->size == 0) return false;
    if (out_val) *out_val = pq->data[0];
    return true;
}
"""
}

# 4. Bloom Filter
MODULES["bloom_filter"] = {
    "name": "bloom_filter",
    "description": "Bit array with multiple hash functions in C11",
    "test_call": "bloom_run_tests();",
    "core": """
/* ==================== Bloom Filter ==================== */
#define BLOOM_BITS 512

typedef struct {
    uint8_t bits[BLOOM_BITS / 8];
} c_bloom_t;

static void bloom_init(c_bloom_t* bf) {
    memset(bf->bits, 0, sizeof(bf->bits));
}

static uint32_t bloom_hash(const char* str, uint32_t seed) {
    uint32_t h = seed;
    while (*str) {
        h ^= (uint8_t)(*str);
        h *= 0x5bd1e995;
        h ^= h >> 15;
        str++;
    }
    return h;
}

static void bloom_add(c_bloom_t* bf, const char* str) {
    for (int i = 0; i < 3; ++i) {
        uint32_t h = bloom_hash(str, (uint32_t)(i * 0x9e3779b9));
        size_t bit_idx = h % BLOOM_BITS;
        bf->bits[bit_idx / 8] |= (uint8_t)(1 << (bit_idx % 8));
    }
}

static bool bloom_might_contain(const c_bloom_t* bf, const char* str) {
    for (int i = 0; i < 3; ++i) {
        uint32_t h = bloom_hash(str, (uint32_t)(i * 0x9e3779b9));
        size_t bit_idx = h % BLOOM_BITS;
        if (!(bf->bits[bit_idx / 8] & (1 << (bit_idx % 8)))) {
            return false;
        }
    }
    return true;
}

static void bloom_run_tests(void) {
    c_bloom_t bf;
    bloom_init(&bf);
    bloom_add(&bf, "session_token_123");
    bloom_add(&bf, "session_token_456");

    assert(bloom_might_contain(&bf, "session_token_123"));
    assert(bloom_might_contain(&bf, "session_token_456"));
}
""",
    "extended": """
static void bloom_clear(c_bloom_t* bf) {
    memset(bf->bits, 0, sizeof(bf->bits));
}
"""
}

# 5. Time Series Metrics
MODULES["time_series"] = {
    "name": "time_series",
    "description": "Ring buffer time series metrics in C11",
    "test_call": "ts_run_tests();",
    "core": """
/* ==================== Time Series Metrics ==================== */
#define TS_MAX_POINTS 32

typedef struct {
    double values[TS_MAX_POINTS];
    size_t count;
    size_t head;
} c_timeseries_t;

static void ts_init(c_timeseries_t* ts) {
    ts->count = 0;
    ts->head = 0;
}

static void ts_record(c_timeseries_t* ts, double val) {
    ts->values[ts->head] = val;
    ts->head = (ts->head + 1) % TS_MAX_POINTS;
    if (ts->count < TS_MAX_POINTS) ts->count++;
}

static double ts_mean(const c_timeseries_t* ts) {
    if (ts->count == 0) return 0.0;
    double sum = 0.0;
    for (size_t i = 0; i < ts->count; ++i) sum += ts->values[i];
    return sum / (double)ts->count;
}

static double ts_std_dev(const c_timeseries_t* ts) {
    if (ts->count < 2) return 0.0;
    double m = ts_mean(ts);
    double sum_sq = 0.0;
    for (size_t i = 0; i < ts->count; ++i) {
        double diff = ts->values[i] - m;
        sum_sq += diff * diff;
    }
    return sqrt(sum_sq / (double)(ts->count - 1));
}

static void ts_run_tests(void) {
    c_timeseries_t ts;
    ts_init(&ts);
    for (int i = 1; i <= 5; ++i) ts_record(&ts, (double)(i * 10));

    double m = ts_mean(&ts);
    assert(fabs(m - 30.0) < 1e-4);
}
""",
    "extended": """
static double ts_max(const c_timeseries_t* ts) {
    if (ts->count == 0) return 0.0;
    double max_v = ts->values[0];
    for (size_t i = 1; i < ts->count; ++i) {
        if (ts->values[i] > max_v) max_v = ts->values[i];
    }
    return max_v;
}
"""
}

# 6. Geo Spatial
MODULES["geo_spatial"] = {
    "name": "geo_spatial",
    "description": "Haversine distance and bounding box calculations in C11",
    "test_call": "geo_run_tests();",
    "core": """
/* ==================== Geo Spatial ==================== */
typedef struct {
    double lat;
    double lon;
} c_geo_point_t;

static double geo_haversine_km(c_geo_point_t p1, c_geo_point_t p2) {
    const double R = 6371.0;
    const double DEG2RAD = 3.141592653589793 / 180.0;

    double dLat = (p2.lat - p1.lat) * DEG2RAD;
    double dLon = (p2.lon - p1.lon) * DEG2RAD;
    double lat1 = p1.lat * DEG2RAD;
    double lat2 = p2.lat * DEG2RAD;

    double a = sin(dLat / 2.0) * sin(dLat / 2.0) +
               sin(dLon / 2.0) * sin(dLon / 2.0) * cos(lat1) * cos(lat2);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    return R * c;
}

static bool geo_in_bbox(c_geo_point_t pt, double min_lat, double max_lat, double min_lon, double max_lon) {
    return pt.lat >= min_lat && pt.lat <= max_lat && pt.lon >= min_lon && pt.lon <= max_lon;
}

static void geo_run_tests(void) {
    c_geo_point_t ny = {40.7128, -74.0060};
    c_geo_point_t bos = {42.3601, -71.0589};
    double d = geo_haversine_km(ny, bos);
    assert(d > 300.0 && d < 350.0);
}
""",
    "extended": """
static c_geo_point_t geo_midpoint(c_geo_point_t p1, c_geo_point_t p2) {
    c_geo_point_t m = {(p1.lat + p2.lat) / 2.0, (p1.lon + p2.lon) / 2.0};
    return m;
}
"""
}
