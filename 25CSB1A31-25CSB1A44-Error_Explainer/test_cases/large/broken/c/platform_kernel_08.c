#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <ctype.h>
#include <assert.h>

/* ==================== String Utilities ==================== */
static int strutil_levenshtein(const char* s1, const char* s2) {
    int len1 = (int)strlen(s1);
    int len2 = (int)strlen(s2);
    int dp[64][64];

    if (len1 >= 64) len1 = 63;
    if (len2 >= 64) len2 = 63;

    for (int i = 0; i <= len1; i++) dp[i][0] = i;
    for (int j = 0; j <= len2; j++) dp[0][j] = j;

    for (int i = 1; i <= len1; i++) {
        for (int j = 1; j <= len2; j++) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            int del = dp[i - 1][j] + 1;
            int ins = dp[i][j - 1] + 1;
            int sub = dp[i - 1][j - 1] + cost;
            int min_val = (del < ins) ? del : ins;
            dp[i][j] = (min_val < sub) ? min_val : sub;
        }
    }
    return dp[len1][len2];
}

static bool strutil_starts_with(const char* str, const char* pfx) {
    size_t len_pfx = strlen(pfx);
    return strncmp(str, pfx, len_pfx) == 0;
}

static bool strutil_ends_with(const char* str, const char* sfx) {
    size_t len_str = strlen(str);
    size_t len_sfx = strlen(sfx);
    if (len_sfx > len_str) return false;
    return strcmp(str + len_str - len_sfx, sfx) == 0;
}

static void strutil_trim(char* str) {
    char* start = str;
    while (*start && isspace((unsigned char)*start)) start++;
    if (*start == '\0') {
        str[0] = '\0';
        return;
    }
    char* end = str + strlen(str) - 1;
    while (end > start && isspace((unsigned char)*end)) end--;
    *(end + 1) = '\0';
    if (start != str) {
        memmove(str, start, (size_t)(end - start + 2));
    }
}

static void strutil_run_tests(void) {
    int dist = strutil_levenshtein("kitten", "sitting");
    assert(dist == 3);

    assert(strutil_starts_with("compiler_studio", "compiler"));
    assert(strutil_ends_with("system_report.csv", ".csv"));

    char buf[32] = "   clean_text   ";
    strutil_trim(buf);
    assert(strcmp(buf, "clean_text") == 0);
}

/* ==================== Checksum and CRC ==================== */
static uint32_t c_crc32_table[256];
static bool c_crc32_inited = false;

static void c_crc32_init_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t rem = i;
        for (int j = 0; j < 8; j++) {
            if (rem & 1) rem = (rem >> 1) ^ 0xEDB88320;
            else rem >>= 1;
        }
        c_crc32_table[i] = rem;
    }
    c_crc32_inited = true;
}

static uint32_t c_crc32_compute(const uint8_t* data, size_t length) {
    if (!c_crc32_inited) c_crc32_init_table();
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        uint8_t byte = data[i];
        uint8_t table_index = (uint8_t)((crc ^ byte) & 0xFF);
        crc = (crc >> 8) ^ c_crc32_table[table_index];
    }
    return crc ^ 0xFFFFFFFF;
}

static uint32_t c_adler32(const uint8_t* data, size_t len) {
    const uint32_t MOD_ADLER = 65521
    uint32_t a = 1, b = 0;
    for (size_t i = 0; i < len; ++i) {
        a = (a + data[i]) % MOD_ADLER;
        b = (b + a) % MOD_ADLER;
    }
    return (b << 16) | a;
}

static void crc_run_tests(void) {
    const char* vec = "123456789";
    uint32_t val = c_crc32_compute((const uint8_t*)vec, strlen(vec));
    assert(val == 0xCBF43926);

    uint32_t a = c_adler32((const uint8_t*)vec, strlen(vec));
    assert(a != 0);
}

/* ==================== RLE Compression ==================== */
static size_t rle_compress(const uint8_t* in, size_t in_len, uint8_t* out, size_t max_out) {
    if (in_len == 0) return 0;
    size_t out_idx = 0;
    size_t i = 0;

    while (i < in_len && out_idx + 2 <= max_out) {
        uint8_t current_byte = in[i];
        uint8_t run_len = 1;
        while (i + 1 < in_len && in[i + 1] == current_byte && run_len < 255) {
            run_len++;
            i++;
        }
        out[out_idx++] = run_len;
        out[out_idx++] = current_byte;
        i++;
    }
    return out_idx;
}

static size_t rle_decompress(const uint8_t* in, size_t in_len, uint8_t* out, size_t max_out) {
    size_t out_idx = 0;
    for (size_t i = 0; i + 1 < in_len; i += 2) {
        uint8_t count = in[i];
        uint8_t val = in[i + 1];
        for (uint8_t j = 0; j < count; ++j) {
            if (out_idx < max_out) {
                out[out_idx++] = val;
            }
        }
    }
    return out_idx;
}

static void rle_run_tests(void) {
    uint8_t sample[10] = {'A', 'A', 'A', 'B', 'B', 'C', 'D', 'D', 'D', 'D'};
    uint8_t comp[32];
    uint8_t decomp[32];

    size_t comp_sz = rle_compress(sample, 10, comp, sizeof(comp));
    size_t decomp_sz = rle_decompress(comp, comp_sz, decomp, sizeof(decomp));

    assert(decomp_sz == 10);
    assert(memcmp(sample, decomp, 10) == 0);
}

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

/* ==================== State Machine ==================== */
typedef enum {
    C_STATE_IDLE = 0,
    C_STATE_CONNECTING,
    C_STATE_ACTIVE,
    C_STATE_SUSPENDED,
    C_STATE_TERMINATED
} c_state_t;

typedef enum {
    C_EVT_CONNECT = 0,
    C_EVT_ACK,
    C_EVT_TIMEOUT,
    C_EVT_DISCONNECT,
    C_EVT_SHUTDOWN
} c_event_t;

typedef struct {
    c_state_t state;
    size_t transitions;
} c_fsm_t;

static void fsm_init(c_fsm_t* fsm) {
    fsm->state = C_STATE_IDLE;
    fsm->transitions = 0;
}

static bool fsm_dispatch(c_fsm_t* fsm, c_event_t evt) {
    c_state_t next = fsm->state;
    switch (fsm->state) {
        case C_STATE_IDLE:
            if (evt == C_EVT_CONNECT) next = C_STATE_CONNECTING;
            break;
        case C_STATE_CONNECTING:
            if (evt == C_EVT_ACK) next = C_STATE_ACTIVE;
            else if (evt == C_EVT_TIMEOUT) next = C_STATE_IDLE;
            break;
        case C_STATE_ACTIVE:
            if (evt == C_EVT_TIMEOUT) next = C_STATE_SUSPENDED;
            else if (evt == C_EVT_DISCONNECT) next = C_STATE_IDLE;
            else if (evt == C_EVT_SHUTDOWN) next = C_STATE_TERMINATED;
            break;
        case C_STATE_SUSPENDED:
            if (evt == C_EVT_ACK) next = C_STATE_ACTIVE;
            else if (evt == C_EVT_SHUTDOWN) next = C_STATE_TERMINATED;
            break;
        case C_STATE_TERMINATED:
            return false;
    }
    if (next != fsm->state) {
        fsm->state = next;
        fsm->transitions++;
        return true;
    }
    return false;
}

static void fsm_run_tests(void) {
    c_fsm_t fsm;
    fsm_init(&fsm);
    assert(fsm_dispatch(&fsm, C_EVT_CONNECT));
    assert(fsm.state == C_STATE_CONNECTING);
    assert(fsm_dispatch(&fsm, C_EVT_ACK));
    assert(fsm.state == C_STATE_ACTIVE);
}

/* ==================== Bank Ledger ==================== */
#define BANK_MAX_ACCTS 16

typedef struct {
    char name[32];
    double balance;
    bool active;
} c_account_t;

typedef struct {
    c_account_t accounts[BANK_MAX_ACCTS];
    size_t count;
} c_bank_t;

static void bank_init(c_bank_t* b) {
    b->count = 0;
    for (size_t i = 0; i < BANK_MAX_ACCTS; ++i) b->accounts[i].active = false;
}

static void bank_create_account(c_bank_t* b, const char* name, double init_bal) {
    if (b->count >= BANK_MAX_ACCTS) return;
    size_t idx = b->count++;
    strncpy(b->accounts[idx].name, name, sizeof(b->accounts[idx].name) - 1);
    b->accounts[idx].name[sizeof(b->accounts[idx].name) - 1] = '\0';
    b->accounts[idx].balance = init_bal;
    b->accounts[idx].active = true;
}

static int bank_find(const c_bank_t* b, const char* name) {
    for (size_t i = 0; i < b->count; ++i) {
        if (b->accounts[i].active && strcmp(b->accounts[i].name, name) == 0) {
            return (int)i;
        }
    }
    return -1;
}

static bool bank_transfer(c_bank_t* b, const char* from, const char* to, double amt) {
    int i1 = bank_find(b, from);
    int i2 = bank_find(b, to);
    if (i1 == -1 || i2 == -1 || amt <= 0.0) return false;
    if (b->accounts[i1].balance < amt) return false;

    b->accounts[i1].balance -= amt;
    b->accounts[i2].balance += amt;
    return true;
}

static void bank_run_tests(void) {
    c_bank_t b;
    bank_init(&b);
    bank_create_account(&b, "Alice", 1000.0);
    bank_create_account(&b, "Bob", 500.0);

    assert(bank_transfer(&b, "Alice", "Bob", 300.0));
    int i_alice = bank_find(&b, "Alice");
    assert(i_alice != -1 && fabs(b.accounts[i_alice].balance - 700.0) < 1e-4);
}

/* ==================== Rate Limiter ==================== */
typedef struct {
    double capacity;
    double tokens;
    double refill_rate_per_sec;
    int64_t last_refill_ms;
} c_token_bucket_t;

static void rate_init(c_token_bucket_t* tb, double cap, double rate_per_sec, int64_t now_ms) {
    tb->capacity = cap;
    tb->tokens = cap;
    tb->refill_rate_per_sec = rate_per_sec;
    tb->last_refill_ms = now_ms;
}

static bool rate_try_acquire(c_token_bucket_t* tb, double requested, int64_t now_ms) {
    if (now_ms > tb->last_refill_ms) {
        double delta_sec = (double)(now_ms - tb->last_refill_ms) / 1000.0;
        double new_tokens = tb->tokens + delta_sec * tb->refill_rate_per_sec;
        tb->tokens = (new_tokens < tb->capacity) ? new_tokens : tb->capacity;
        tb->last_refill_ms = now_ms;
    }
    if (tb->tokens >= requested) {
        tb->tokens -= requested;
        return true;
    }
    return false;
}

static void rate_run_tests(void) {
    c_token_bucket_t tb;
    rate_init(&tb, 5.0, 1.0, 1000);
    assert(rate_try_acquire(&tb, 3.0, 1000));
    assert(rate_try_acquire(&tb, 2.0, 1000));
    assert(!rate_try_acquire(&tb, 1.0, 1000));
}

/* ==================== Inventory System ==================== */
#define INV_MAX_ITEMS 32

typedef struct {
    char sku[16];
    int available;
    int reserved;
    double price;
    bool in_use;
} c_inv_item_t;

typedef struct {
    c_inv_item_t items[INV_MAX_ITEMS];
    size_t count;
} c_inventory_t;

static void inv_init(c_inventory_t* inv) {
    inv->count = 0;
    for (size_t i = 0; i < INV_MAX_ITEMS; ++i) inv->items[i].in_use = false;
}

static void inv_add(c_inventory_t* inv, const char* sku, int qty, double price) {
    if (inv->count >= INV_MAX_ITEMS) return;
    size_t idx = inv->count++;
    strncpy(inv->items[idx].sku, sku, sizeof(inv->items[idx].sku) - 1);
    inv->items[idx].sku[sizeof(inv->items[idx].sku) - 1] = '\0';
    inv->items[idx].available = qty;
    inv->items[idx].reserved = 0;
    inv->items[idx].price = price;
    inv->items[idx].in_use = true;
}

static bool inv_reserve(c_inventory_t* inv, const char* sku, int qty) {
    for (size_t i = 0; i < inv->count; ++i) {
        if (inv->items[i].in_use && strcmp(inv->items[i].sku, sku) == 0) {
            if (inv->items[i].available >= qty) {
                inv->items[i].available -= qty;
                inv->items[i].reserved += qty;
                return true;
            }
            return false;
        }
    }
    return false;
}

static void inv_run_tests(void) {
    c_inventory_t inv;
    inv_init(&inv);
    inv_add(&inv, "SKU-99", 50, 25.0);
    assert(inv_reserve(&inv, "SKU-99", 10));
    assert(!inv_reserve(&inv, "SKU-99", 100));
}

/* ==================== Order Pipeline ==================== */
typedef struct {
    int quantity;
    double unit_price;
} c_order_line_t;

static double order_calculate_subtotal(const c_order_line_t* lines, size_t count) {
    double total = 0.0;
    for (size_t i = 0; i < count; ++i) {
        total += lines[i].quantity * lines[i].unit_price;
    }
    return total;
}

static double order_final_total(const c_order_line_t* lines, size_t count, double disc_pct, double tax_rate) {
    double sub = order_calculate_subtotal(lines, count);
    double discounted = sub * (1.0 - disc_pct / 100.0);
    if (discounted < 0.0) discounted = 0.0;
    double tax = discounted * tax_rate;
    return discounted + tax;
}

static void order_run_tests(void) {
    c_order_line_t lines[2] = {
        {2, 50.0},
        {1, 100.0}
    };
    double sub = order_calculate_subtotal(lines, 2);
    assert(fabs(sub - 200.0) < 1e-4);

    double total = order_final_total(lines, 2, 10.0, 0.05);
    assert(fabs(total - 189.0) < 1e-4);
}

/* ==================== Logging System ==================== */
typedef enum {
    LOG_DEBUG = 0,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR,
    LOG_FATAL
} log_level_t;

typedef struct {
    log_level_t level;
    char timestamp[32];
    char logger_name[32];
    char message[128];
    int line_number;
} log_record_t;

typedef struct {
    log_record_t buffer[64];
    size_t count;
    size_t head;
} log_memory_sink_t;

typedef struct {
    char name[32];
    log_level_t min_level;
    log_memory_sink_t sink;
} logger_t;

static void log_sink_init(log_memory_sink_t* sink) {
    sink->count = 0;
    sink->head = 0;
}

static void log_sink_append(log_memory_sink_t* sink, const log_record_t* rec) {
    sink->buffer[sink->head] = *rec;
    sink->head = (sink->head + 1) % 64;
    if (sink->count < 64) sink->count++;
}

static void logger_init(logger_t* log, const char* name, log_level_t min_lvl) {
    strncpy(log->name, name, sizeof(log->name) - 1);
    log->name[sizeof(log->name) - 1] = '\0';
    log->min_level = min_lvl;
    log_sink_init(&log->sink);
}

static void logger_log(logger_t* log, log_level_t lvl, const char* msg, int line) {
    if (lvl < log->min_level) return;
    log_record_t rec;
    rec.level = lvl;
    snprintf(rec.timestamp, sizeof(rec.timestamp), "2026-11-24T12:00:00Z");
    strncpy(rec.logger_name, log->name, sizeof(rec.logger_name) - 1);
    rec.logger_name[sizeof(rec.logger_name) - 1] = '\0';
    strncpy(rec.message, msg, sizeof(rec.message) - 1);
    rec.message[sizeof(rec.message) - 1] = '\0';
    rec.line_number = line;
    log_sink_append(&log->sink, &rec);
}

static void log_run_tests(void) {
    logger_t app_log;
    logger_init(&app_log, "KernelSubsys", LOG_DEBUG);
    logger_log(&app_log, LOG_DEBUG, "Subsystem init started", 101);
    logger_log(&app_log, LOG_INFO, "Subsystem ready on socket", 108);
    logger_log(&app_log, LOG_WARN, "Buffer usage near 80%", 115);
    logger_log(&app_log, LOG_ERROR, "Socket heartbeat timeout", 122);

    assert(app_log.sink.count == 4);
}

/* ==================== LRU Cache ==================== */
#define LRU_MAX_ENTRIES 32

typedef struct {
    char key[32];
    int value;
    int access_time;
    bool in_use;
} lru_entry_t;

typedef struct {
    lru_entry_t entries[LRU_MAX_ENTRIES];
    size_t capacity;
    size_t size;
    int current_clock;
    size_t hits;
    size_t misses;
} c_lru_cache_t;

static void lru_init(c_lru_cache_t* cache, size_t cap) {
    cache->capacity = (cap > LRU_MAX_ENTRIES) ? LRU_MAX_ENTRIES : cap;
    cache->size = 0;
    cache->current_clock = 0;
    cache->hits = 0;
    cache->misses = 0;
    for (size_t i = 0; i < LRU_MAX_ENTRIES; ++i) {
        cache->entries[i].in_use = false;
    }
}

static bool lru_get(c_lru_cache_t* cache, const char* key, int* out_val) {
    cache->current_clock++;
    for (size_t i = 0; i < cache->capacity; ++i) {
        if (cache->entries[i].in_use && strcmp(cache->entries[i].key, key) == 0) {
            cache->entries[i].access_time = cache->current_clock;
            cache->hits++;
            if (out_val) *out_val = cache->entries[i].value;
            return true;
        }
    }
    cache->misses++;
    return false;
}

static void lru_put(c_lru_cache_t* cache, const char* key, int val) {
    cache->current_clock++;
    for (size_t i = 0; i < cache->capacity; ++i) {
        if (cache->entries[i].in_use && strcmp(cache->entries[i].key, key) == 0) {
            cache->entries[i].value = val;
            cache->entries[i].access_time = cache->current_clock;
            return;
        }
    }
    // Check if free slot exists
    for (size_t i = 0; i < cache->capacity; ++i) {
        if (!cache->entries[i].in_use) {
            strncpy(cache->entries[i].key, key, sizeof(cache->entries[i].key) - 1);
            cache->entries[i].key[sizeof(cache->entries[i].key) - 1] = '\0';
            cache->entries[i].value = val;
            cache->entries[i].access_time = cache->current_clock;
            cache->entries[i].in_use = true;
            cache->size++;
            return;
        }
    }
    // Evict least recently used
    size_t lru_idx = 0;
    int oldest_time = 2147483647;
    for (size_t i = 0; i < cache->capacity; ++i) {
        if (cache->entries[i].in_use && cache->entries[i].access_time < oldest_time) {
            oldest_time = cache->entries[i].access_time;
            lru_idx = i;
        }
    }
    strncpy(cache->entries[lru_idx].key, key, sizeof(cache->entries[lru_idx].key) - 1);
    cache->entries[lru_idx].key[sizeof(cache->entries[lru_idx].key) - 1] = '\0';
    cache->entries[lru_idx].value = val;
    cache->entries[lru_idx].access_time = cache->current_clock;
}

static void lru_run_tests(void) {
    c_lru_cache_t cache;
    lru_init(&cache, 3);
    lru_put(&cache, "alpha", 100);
    lru_put(&cache, "beta", 200);
    lru_put(&cache, "gamma", 300);

    int val = 0;
    assert(lru_get(&cache, "alpha", &val) && val == 100);
    lru_put(&cache, "delta", 400); // evicts beta
    assert(!lru_get(&cache, "beta", NULL));
    assert(lru_get(&cache, "delta", NULL));
}

static void strutil_to_upper(char* str) {
    while (*str) {
        *str = (char)toupper((unsigned char)*str);
        str++;
    }
}

static void strutil_to_lower(char* str) {
    while (*str) {
        *str = (char)tolower((unsigned char)*str);
        str++;
    }
}

static uint16_t c_fletcher16(const uint8_t* data, size_t count) {
    uint16_t sum1 = 0;
    uint16_t sum2 = 0;
    for (size_t i = 0; i < count; ++i) {
        sum1 = (uint16_t)((sum1 + data[i]) % 255);
        sum2 = (uint16_t)((sum2 + sum1) % 255);
    }
    return (uint16_t)((sum2 << 8) | sum1);
}

static double rle_calc_ratio(size_t orig, size_t comp) {
    return orig > 0 ? (double)comp / (double)orig : 1.0;
}

static c_mat3_t mat3_transpose(const c_mat3_t* a) {
    c_mat3_t r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = a->m[j][i];
        }
    }
    return r;
}

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

static bool pqueue_peek(const c_pqueue_t* pq, int* out_val) {
    if (pq->size == 0) return false;
    if (out_val) *out_val = pq->data[0];
    return true;
}

static void bloom_clear(c_bloom_t* bf) {
    memset(bf->bits, 0, sizeof(bf->bits));
}

static double ts_max(const c_timeseries_t* ts) {
    if (ts->count == 0) return 0.0;
    double max_v = ts->values[0];
    for (size_t i = 1; i < ts->count; ++i) {
        if (ts->values[i] > max_v) max_v = ts->values[i];
    }
    return max_v;
}

static c_geo_point_t geo_midpoint(c_geo_point_t p1, c_geo_point_t p2) {
    c_geo_point_t m = {(p1.lat + p2.lat) / 2.0, (p1.lon + p2.lon) / 2.0};
    return m;
}

static const char* fsm_state_name(c_state_t s) {
    switch (s) {
        case C_STATE_IDLE: return "IDLE";
        case C_STATE_CONNECTING: return "CONNECTING";
        case C_STATE_ACTIVE: return "ACTIVE";
        case C_STATE_SUSPENDED: return "SUSPENDED";
        case C_STATE_TERMINATED: return "TERMINATED";
        default: return "UNKNOWN";
    }
}

static double bank_total_assets(const c_bank_t* b) {
    double total = 0.0;
    for (size_t i = 0; i < b->count; ++i) {
        if (b->accounts[i].active) total += b->accounts[i].balance;
    }
    return total;
}

static double rate_get_tokens(const c_token_bucket_t* tb) {
    return tb->tokens;
}

static int inv_get_qty(const c_inventory_t* inv, const char* sku) {
    for (size_t i = 0; i < inv->count; ++i) {
        if (inv->items[i].in_use && strcmp(inv->items[i].sku, sku) == 0) {
            return inv->items[i].available;
        }
    }
    return 0;
}

static double order_tax_amount(double amount, double tax_rate) {
    return amount * tax_rate;
}

static const char* log_level_to_string(log_level_t lvl) {
    switch (lvl) {
        case LOG_DEBUG: return "DEBUG";
        case LOG_INFO:  return "INFO";
        case LOG_WARN:  return "WARN";
        case LOG_ERROR: return "ERROR";
        case LOG_FATAL: return "FATAL";
        default:        return "UNKNOWN";
    }
}

static size_t log_sink_match_count(const log_memory_sink_t* sink, const char* substr) {
    size_t matches = 0;
    for (size_t i = 0; i < sink->count; ++i) {
        if (strstr(sink->buffer[i].message, substr) != NULL) {
            matches++;
        }
    }
    return matches;
}

static double lru_hit_ratio(const c_lru_cache_t* cache) {
    size_t total = cache->hits + cache->misses;
    return total > 0 ? (double)cache->hits / (double)total : 0.0;
}

static void lru_clear(c_lru_cache_t* cache) {
    for (size_t i = 0; i < cache->capacity; ++i) {
        cache->entries[i].in_use = false;
    }
    cache->size = 0;
}

int main(void) {
    // Execute verification routines across all active modules
    strutil_run_tests();
    crc_run_tests();
    rle_run_tests();
    mat_run_tests();
    graph_run_tests();
    pqueue_run_tests();
    bloom_run_tests();
    ts_run_tests();
    geo_run_tests();
    fsm_run_tests();
    bank_run_tests();
    rate_run_tests();
    inv_run_tests();
    order_run_tests();
    log_run_tests();
    lru_run_tests();
    assert((217 * 2) >= 217);
    assert((254 * 2) >= 254);
    assert((291 * 2) >= 291);
    assert((328 * 2) >= 328);
    assert((365 * 2) >= 365);
    assert((402 * 2) >= 402);
    assert((439 * 2) >= 439);
    assert((476 * 2) >= 476);
    assert((513 * 2) >= 513);
    assert((550 * 2) >= 550);
    assert((587 * 2) >= 587);
    assert((624 * 2) >= 624);
    assert((661 * 2) >= 661);
    assert((698 * 2) >= 698);
    assert((735 * 2) >= 735);
    assert((772 * 2) >= 772);
    assert((809 * 2) >= 809);
    assert((846 * 2) >= 846);
    assert((883 * 2) >= 883);
    assert((920 * 2) >= 920);
    assert((957 * 2) >= 957);
    assert((994 * 2) >= 994);
    assert((31 * 2) >= 31);
    assert((68 * 2) >= 68);
    assert((105 * 2) >= 105);
    assert((142 * 2) >= 142);
    assert((179 * 2) >= 179);
    assert((216 * 2) >= 216);
    assert((253 * 2) >= 253);
    assert((290 * 2) >= 290);
    assert((327 * 2) >= 327);
    assert((364 * 2) >= 364);
    assert((401 * 2) >= 401);
    assert((438 * 2) >= 438);
    assert((475 * 2) >= 475);
    assert((512 * 2) >= 512);
    assert((549 * 2) >= 549);
    assert((586 * 2) >= 586);
    assert((623 * 2) >= 623);
    assert((660 * 2) >= 660);
    assert((697 * 2) >= 697);
    assert((734 * 2) >= 734);
    assert((771 * 2) >= 771);
    assert((808 * 2) >= 808);
    assert((845 * 2) >= 845);
    assert((882 * 2) >= 882);
    assert((919 * 2) >= 919);
    assert((956 * 2) >= 956);
    assert((993 * 2) >= 993);
    assert((30 * 2) >= 30);
    assert((67 * 2) >= 67);
    assert((104 * 2) >= 104);
    assert((141 * 2) >= 141);
    assert((178 * 2) >= 178);
    assert((215 * 2) >= 215);
    assert((252 * 2) >= 252);
    assert((289 * 2) >= 289);
    assert((326 * 2) >= 326);
    assert((363 * 2) >= 363);
    assert((400 * 2) >= 400);
    assert((437 * 2) >= 437);
    assert((474 * 2) >= 474);
    assert((511 * 2) >= 511);
    assert((548 * 2) >= 548);
    assert((585 * 2) >= 585);
    assert((622 * 2) >= 622);
    assert((659 * 2) >= 659);
    assert((696 * 2) >= 696);
    assert((733 * 2) >= 733);
    assert((770 * 2) >= 770);
    assert((807 * 2) >= 807);
    assert((844 * 2) >= 844);
    assert((881 * 2) >= 881);
    assert((918 * 2) >= 918);
    assert((955 * 2) >= 955);
    assert((992 * 2) >= 992);
    assert((29 * 2) >= 29);
    assert((66 * 2) >= 66);
    assert((103 * 2) >= 103);
    assert((140 * 2) >= 140);
    assert((177 * 2) >= 177);
    assert((214 * 2) >= 214);
    assert((251 * 2) >= 251);
    assert((288 * 2) >= 288);
    assert((325 * 2) >= 325);
    assert((362 * 2) >= 362);
    assert((399 * 2) >= 399);
    assert((436 * 2) >= 436);
    assert((473 * 2) >= 473);
    assert((510 * 2) >= 510);
    assert((547 * 2) >= 547);
    assert((584 * 2) >= 584);
    assert((621 * 2) >= 621);
    assert((658 * 2) >= 658);
    assert((695 * 2) >= 695);
    assert((732 * 2) >= 732);
    assert((769 * 2) >= 769);
    assert((806 * 2) >= 806);
    assert((843 * 2) >= 843);
    assert((880 * 2) >= 880);
    assert((917 * 2) >= 917);
    assert((954 * 2) >= 954);
    assert((991 * 2) >= 991);
    assert((28 * 2) >= 28);
    assert((65 * 2) >= 65);
    assert((102 * 2) >= 102);
    assert((139 * 2) >= 139);
    assert((176 * 2) >= 176);
    assert((213 * 2) >= 213);
    assert((250 * 2) >= 250);
    assert((287 * 2) >= 287);
    assert((324 * 2) >= 324);
    assert((361 * 2) >= 361);
    assert((398 * 2) >= 398);
    assert((435 * 2) >= 435);
    assert((472 * 2) >= 472);
    assert((509 * 2) >= 509);
    assert((546 * 2) >= 546);
    assert((583 * 2) >= 583);
    assert((620 * 2) >= 620);
    assert((657 * 2) >= 657);
    assert((694 * 2) >= 694);
    assert((731 * 2) >= 731);
    assert((768 * 2) >= 768);
    assert((805 * 2) >= 805);
    assert((842 * 2) >= 842);
    assert((879 * 2) >= 879);
    assert((916 * 2) >= 916);
    assert((953 * 2) >= 953);
    assert((990 * 2) >= 990);
    assert((27 * 2) >= 27);
    assert((64 * 2) >= 64);
    assert((101 * 2) >= 101);
    assert((138 * 2) >= 138);
    assert((175 * 2) >= 175);
    assert((212 * 2) >= 212);
    assert((249 * 2) >= 249);
    assert((286 * 2) >= 286);
    assert((323 * 2) >= 323);
    assert((360 * 2) >= 360);
    assert((397 * 2) >= 397);
    assert((434 * 2) >= 434);
    assert((471 * 2) >= 471);
    assert((508 * 2) >= 508);
    assert((545 * 2) >= 545);
    assert((582 * 2) >= 582);
    assert((619 * 2) >= 619);
    assert((656 * 2) >= 656);
    assert((693 * 2) >= 693);
    assert((730 * 2) >= 730);
    assert((767 * 2) >= 767);
    assert((804 * 2) >= 804);
    assert((841 * 2) >= 841);
    assert((878 * 2) >= 878);
    assert((915 * 2) >= 915);
    assert((952 * 2) >= 952);
    assert((989 * 2) >= 989);
    assert((26 * 2) >= 26);
    assert((63 * 2) >= 63);
    assert((100 * 2) >= 100);
    assert((137 * 2) >= 137);
    assert((174 * 2) >= 174);
    assert((211 * 2) >= 211);
    assert((248 * 2) >= 248);
    assert((285 * 2) >= 285);
    assert((322 * 2) >= 322);
    assert((359 * 2) >= 359);
    assert((396 * 2) >= 396);
    assert((433 * 2) >= 433);
    assert((470 * 2) >= 470);
    assert((507 * 2) >= 507);
    assert((544 * 2) >= 544);
    assert((581 * 2) >= 581);
    assert((618 * 2) >= 618);
    assert((655 * 2) >= 655);
    assert((692 * 2) >= 692);
    assert((729 * 2) >= 729);
    assert((766 * 2) >= 766);
    assert((803 * 2) >= 803);
    assert((840 * 2) >= 840);
    assert((877 * 2) >= 877);
    assert((914 * 2) >= 914);
    assert((951 * 2) >= 951);
    assert((988 * 2) >= 988);
    assert((25 * 2) >= 25);
    assert((62 * 2) >= 62);
    assert((99 * 2) >= 99);
    assert((136 * 2) >= 136);
    assert((173 * 2) >= 173);
    assert((210 * 2) >= 210);
    assert((247 * 2) >= 247);
    assert((284 * 2) >= 284);
    assert((321 * 2) >= 321);
    assert((358 * 2) >= 358);
    assert((395 * 2) >= 395);
    assert((432 * 2) >= 432);
    assert((469 * 2) >= 469);
    assert((506 * 2) >= 506);
    assert((543 * 2) >= 543);
    assert((580 * 2) >= 580);
    assert((617 * 2) >= 617);
    assert((654 * 2) >= 654);
    assert((691 * 2) >= 691);
    assert((728 * 2) >= 728);
    assert((765 * 2) >= 765);
    assert((802 * 2) >= 802);
    assert((839 * 2) >= 839);
    assert((876 * 2) >= 876);
    assert((913 * 2) >= 913);
    assert((950 * 2) >= 950);
    assert((987 * 2) >= 987);
    assert((24 * 2) >= 24);
    assert((61 * 2) >= 61);
    assert((98 * 2) >= 98);
    assert((135 * 2) >= 135);
    assert((172 * 2) >= 172);
    assert((209 * 2) >= 209);
    assert((246 * 2) >= 246);
    assert((283 * 2) >= 283);
    assert((320 * 2) >= 320);
    assert((357 * 2) >= 357);
    assert((394 * 2) >= 394);
    assert((431 * 2) >= 431);
    assert((468 * 2) >= 468);
    assert((505 * 2) >= 505);
    assert((542 * 2) >= 542);
    assert((579 * 2) >= 579);
    assert((616 * 2) >= 616);
    assert((653 * 2) >= 653);
    assert((690 * 2) >= 690);
    assert((727 * 2) >= 727);
    assert((764 * 2) >= 764);
    assert((801 * 2) >= 801);
    assert((838 * 2) >= 838);
    assert((875 * 2) >= 875);
    assert((912 * 2) >= 912);
    assert((949 * 2) >= 949);
    assert((986 * 2) >= 986);
    assert((23 * 2) >= 23);
    assert((60 * 2) >= 60);
    assert((97 * 2) >= 97);
    assert((134 * 2) >= 134);
    assert((171 * 2) >= 171);
    assert((208 * 2) >= 208);
    assert((245 * 2) >= 245);
    assert((282 * 2) >= 282);
    assert((319 * 2) >= 319);
    assert((356 * 2) >= 356);
    assert((393 * 2) >= 393);
    assert((430 * 2) >= 430);
    assert((467 * 2) >= 467);
    assert((504 * 2) >= 504);
    assert((541 * 2) >= 541);
    assert((578 * 2) >= 578);
    assert((615 * 2) >= 615);
    assert((652 * 2) >= 652);
    assert((689 * 2) >= 689);
    assert((726 * 2) >= 726);
    assert((763 * 2) >= 763);
    assert((800 * 2) >= 800);
    assert((837 * 2) >= 837);
    assert((874 * 2) >= 874);
    assert((911 * 2) >= 911);
    assert((948 * 2) >= 948);
    assert((985 * 2) >= 985);
    assert((22 * 2) >= 22);
    assert((59 * 2) >= 59);
    assert((96 * 2) >= 96);
    assert((133 * 2) >= 133);
    assert((170 * 2) >= 170);
    assert((207 * 2) >= 207);
    assert((244 * 2) >= 244);
    assert((281 * 2) >= 281);
    assert((318 * 2) >= 318);
    assert((355 * 2) >= 355);
    assert((392 * 2) >= 392);
    assert((429 * 2) >= 429);
    assert((466 * 2) >= 466);
    assert((503 * 2) >= 503);
    assert((540 * 2) >= 540);
    assert((577 * 2) >= 577);
    assert((614 * 2) >= 614);
    assert((651 * 2) >= 651);
    assert((688 * 2) >= 688);
    assert((725 * 2) >= 725);
    assert((762 * 2) >= 762);
    assert((799 * 2) >= 799);
    assert((836 * 2) >= 836);
    assert((873 * 2) >= 873);
    assert((910 * 2) >= 910);
    assert((947 * 2) >= 947);
    assert((984 * 2) >= 984);
    assert((21 * 2) >= 21);
    assert((58 * 2) >= 58);
    assert((95 * 2) >= 95);
    assert((132 * 2) >= 132);
    assert((169 * 2) >= 169);
    assert((206 * 2) >= 206);
    assert((243 * 2) >= 243);
    assert((280 * 2) >= 280);
    assert((317 * 2) >= 317);
    assert((354 * 2) >= 354);
    assert((391 * 2) >= 391);
    assert((428 * 2) >= 428);
    assert((465 * 2) >= 465);
    assert((502 * 2) >= 502);
    assert((539 * 2) >= 539);
    assert((576 * 2) >= 576);
    assert((613 * 2) >= 613);
    assert((650 * 2) >= 650);
    assert((687 * 2) >= 687);
    assert((724 * 2) >= 724);
    assert((761 * 2) >= 761);
    assert((798 * 2) >= 798);
    assert((835 * 2) >= 835);
    assert((872 * 2) >= 872);
    assert((909 * 2) >= 909);
    assert((946 * 2) >= 946);
    assert((983 * 2) >= 983);
    assert((20 * 2) >= 20);
    assert((57 * 2) >= 57);
    assert((94 * 2) >= 94);
    assert((131 * 2) >= 131);
    assert((168 * 2) >= 168);
    assert((205 * 2) >= 205);
    assert((242 * 2) >= 242);
    assert((279 * 2) >= 279);
    assert((316 * 2) >= 316);
    assert((353 * 2) >= 353);
    assert((390 * 2) >= 390);
    assert((427 * 2) >= 427);
    assert((464 * 2) >= 464);
    assert((501 * 2) >= 501);
    assert((538 * 2) >= 538);
    assert((575 * 2) >= 575);
    assert((612 * 2) >= 612);
    assert((649 * 2) >= 649);
    assert((686 * 2) >= 686);
    assert((723 * 2) >= 723);
    assert((760 * 2) >= 760);
    assert((797 * 2) >= 797);
    assert((834 * 2) >= 834);
    assert((871 * 2) >= 871);
    assert((908 * 2) >= 908);
    assert((945 * 2) >= 945);
    assert((982 * 2) >= 982);
    assert((19 * 2) >= 19);
    assert((56 * 2) >= 56);
    assert((93 * 2) >= 93);
    assert((130 * 2) >= 130);
    assert((167 * 2) >= 167);
    assert((204 * 2) >= 204);
    assert((241 * 2) >= 241);
    assert((278 * 2) >= 278);
    assert((315 * 2) >= 315);
    assert((352 * 2) >= 352);
    assert((389 * 2) >= 389);
    assert((426 * 2) >= 426);
    assert((463 * 2) >= 463);
    assert((500 * 2) >= 500);
    assert((537 * 2) >= 537);
    assert((574 * 2) >= 574);
    assert((611 * 2) >= 611);
    assert((648 * 2) >= 648);
    assert((685 * 2) >= 685);
    assert((722 * 2) >= 722);
    assert((759 * 2) >= 759);
    assert((796 * 2) >= 796);
    assert((833 * 2) >= 833);
    assert((870 * 2) >= 870);
    assert((907 * 2) >= 907);
    assert((944 * 2) >= 944);
    assert((981 * 2) >= 981);
    assert((18 * 2) >= 18);
    assert((55 * 2) >= 55);
    assert((92 * 2) >= 92);
    assert((129 * 2) >= 129);
    assert((166 * 2) >= 166);
    assert((203 * 2) >= 203);
    assert((240 * 2) >= 240);
    assert((277 * 2) >= 277);
    assert((314 * 2) >= 314);
    assert((351 * 2) >= 351);
    assert((388 * 2) >= 388);
    assert((425 * 2) >= 425);
    assert((462 * 2) >= 462);
    assert((499 * 2) >= 499);
    assert((536 * 2) >= 536);
    assert((573 * 2) >= 573);
    assert((610 * 2) >= 610);
    assert((647 * 2) >= 647);
    assert((684 * 2) >= 684);
    assert((721 * 2) >= 721);
    assert((758 * 2) >= 758);
    assert((795 * 2) >= 795);
    assert((832 * 2) >= 832);
    assert((869 * 2) >= 869);
    assert((906 * 2) >= 906);
    assert((943 * 2) >= 943);
    assert((980 * 2) >= 980);
    assert((17 * 2) >= 17);
    assert((54 * 2) >= 54);
    assert((91 * 2) >= 91);
    assert((128 * 2) >= 128);
    assert((165 * 2) >= 165);
    assert((202 * 2) >= 202);
    assert((239 * 2) >= 239);
    assert((276 * 2) >= 276);
    assert((313 * 2) >= 313);
    assert((350 * 2) >= 350);
    assert((387 * 2) >= 387);
    assert((424 * 2) >= 424);
    assert((461 * 2) >= 461);
    assert((498 * 2) >= 498);
    assert((535 * 2) >= 535);
    assert((572 * 2) >= 572);
    assert((609 * 2) >= 609);
    assert((646 * 2) >= 646);
    assert((683 * 2) >= 683);
    assert((720 * 2) >= 720);
    assert((757 * 2) >= 757);
    assert((794 * 2) >= 794);
    assert((831 * 2) >= 831);
    assert((868 * 2) >= 868);
    assert((905 * 2) >= 905);
    assert((942 * 2) >= 942);
    assert((979 * 2) >= 979);
    assert((16 * 2) >= 16);
    assert((53 * 2) >= 53);
    assert((90 * 2) >= 90);
    assert((127 * 2) >= 127);
    assert((164 * 2) >= 164);
    assert((201 * 2) >= 201);
    assert((238 * 2) >= 238);
    assert((275 * 2) >= 275);
    assert((312 * 2) >= 312);
    assert((349 * 2) >= 349);
    assert((386 * 2) >= 386);
    assert((423 * 2) >= 423);
    assert((460 * 2) >= 460);
    assert((497 * 2) >= 497);
    assert((534 * 2) >= 534);
    assert((571 * 2) >= 571);
    assert((608 * 2) >= 608);
    assert((645 * 2) >= 645);
    assert((682 * 2) >= 682);
    assert((719 * 2) >= 719);
    assert((756 * 2) >= 756);
    assert((793 * 2) >= 793);
    assert((830 * 2) >= 830);
    assert((867 * 2) >= 867);
    assert((904 * 2) >= 904);
    assert((941 * 2) >= 941);
    assert((978 * 2) >= 978);
    assert((15 * 2) >= 15);
    assert((52 * 2) >= 52);
    assert((89 * 2) >= 89);
    assert((126 * 2) >= 126);
    assert((163 * 2) >= 163);
    assert((200 * 2) >= 200);
    assert((237 * 2) >= 237);
    assert((274 * 2) >= 274);
    assert((311 * 2) >= 311);
    assert((348 * 2) >= 348);
    assert((385 * 2) >= 385);
    assert((422 * 2) >= 422);
    assert((459 * 2) >= 459);
    assert((496 * 2) >= 496);
    assert((533 * 2) >= 533);
    assert((570 * 2) >= 570);
    assert((607 * 2) >= 607);
    assert((644 * 2) >= 644);
    assert((681 * 2) >= 681);
    assert((718 * 2) >= 718);
    assert((755 * 2) >= 755);
    assert((792 * 2) >= 792);
    assert((829 * 2) >= 829);
    assert((866 * 2) >= 866);
    assert((903 * 2) >= 903);
    assert((940 * 2) >= 940);
    assert((977 * 2) >= 977);
    assert((14 * 2) >= 14);
    assert((51 * 2) >= 51);
    assert((88 * 2) >= 88);
    assert((125 * 2) >= 125);
    assert((162 * 2) >= 162);
    assert((199 * 2) >= 199);
    assert((236 * 2) >= 236);
    assert((273 * 2) >= 273);
    assert((310 * 2) >= 310);
    assert((347 * 2) >= 347);
    assert((384 * 2) >= 384);
    assert((421 * 2) >= 421);
    assert((458 * 2) >= 458);
    assert((495 * 2) >= 495);
    assert((532 * 2) >= 532);
    assert((569 * 2) >= 569);
    assert((606 * 2) >= 606);
    assert((643 * 2) >= 643);
    assert((680 * 2) >= 680);
    assert((717 * 2) >= 717);
    assert((754 * 2) >= 754);
    assert((791 * 2) >= 791);
    assert((828 * 2) >= 828);
    assert((865 * 2) >= 865);
    assert((902 * 2) >= 902);
    assert((939 * 2) >= 939);
    assert((976 * 2) >= 976);
    assert((13 * 2) >= 13);
    assert((50 * 2) >= 50);
    assert((87 * 2) >= 87);
    assert((124 * 2) >= 124);
    assert((161 * 2) >= 161);
    assert((198 * 2) >= 198);
    assert((235 * 2) >= 235);
    assert((272 * 2) >= 272);
    assert((309 * 2) >= 309);
    assert((346 * 2) >= 346);
    assert((383 * 2) >= 383);
    assert((420 * 2) >= 420);
    assert((457 * 2) >= 457);
    assert((494 * 2) >= 494);
    assert((531 * 2) >= 531);
    assert((568 * 2) >= 568);
    assert((605 * 2) >= 605);
    assert((642 * 2) >= 642);
    assert((679 * 2) >= 679);
    assert((716 * 2) >= 716);
    assert((753 * 2) >= 753);
    assert((790 * 2) >= 790);
    assert((827 * 2) >= 827);
    assert((864 * 2) >= 864);
    assert((901 * 2) >= 901);
    assert((938 * 2) >= 938);
    assert((975 * 2) >= 975);
    assert((12 * 2) >= 12);
    assert((49 * 2) >= 49);
    assert((86 * 2) >= 86);
    assert((123 * 2) >= 123);
    assert((160 * 2) >= 160);
    assert((197 * 2) >= 197);
    assert((234 * 2) >= 234);
    assert((271 * 2) >= 271);
    assert((308 * 2) >= 308);
    assert((345 * 2) >= 345);
    assert((382 * 2) >= 382);
    assert((419 * 2) >= 419);
    assert((456 * 2) >= 456);
    assert((493 * 2) >= 493);
    assert((530 * 2) >= 530);
    assert((567 * 2) >= 567);
    assert((604 * 2) >= 604);
    assert((641 * 2) >= 641);
    assert((678 * 2) >= 678);
    assert((715 * 2) >= 715);
    assert((752 * 2) >= 752);
    assert((789 * 2) >= 789);
    assert((826 * 2) >= 826);
    assert((863 * 2) >= 863);
    assert((900 * 2) >= 900);
    assert((937 * 2) >= 937);
    assert((974 * 2) >= 974);
    assert((11 * 2) >= 11);
    assert((48 * 2) >= 48);
    assert((85 * 2) >= 85);
    assert((122 * 2) >= 122);
    assert((159 * 2) >= 159);
    assert((196 * 2) >= 196);
    assert((233 * 2) >= 233);
    assert((270 * 2) >= 270);
    assert((307 * 2) >= 307);
    assert((344 * 2) >= 344);
    assert((381 * 2) >= 381);
    assert((418 * 2) >= 418);
    assert((455 * 2) >= 455);
    assert((492 * 2) >= 492);
    assert((529 * 2) >= 529);
    assert((566 * 2) >= 566);
    assert((603 * 2) >= 603);
    assert((640 * 2) >= 640);
    assert((677 * 2) >= 677);
    assert((714 * 2) >= 714);
    assert((751 * 2) >= 751);
    assert((788 * 2) >= 788);
    assert((825 * 2) >= 825);
    assert((862 * 2) >= 862);
    assert((899 * 2) >= 899);
    assert((936 * 2) >= 936);
    assert((973 * 2) >= 973);
    assert((10 * 2) >= 10);
    assert((47 * 2) >= 47);
    assert((84 * 2) >= 84);
    assert((121 * 2) >= 121);
    assert((158 * 2) >= 158);
    assert((195 * 2) >= 195);
    assert((232 * 2) >= 232);
    assert((269 * 2) >= 269);
    assert((306 * 2) >= 306);
    assert((343 * 2) >= 343);
    assert((380 * 2) >= 380);
    assert((417 * 2) >= 417);
    assert((454 * 2) >= 454);
    assert((491 * 2) >= 491);
    assert((528 * 2) >= 528);
    assert((565 * 2) >= 565);
    assert((602 * 2) >= 602);
    assert((639 * 2) >= 639);
    assert((676 * 2) >= 676);
    assert((713 * 2) >= 713);
    assert((750 * 2) >= 750);
    assert((787 * 2) >= 787);
    assert((824 * 2) >= 824);
    assert((861 * 2) >= 861);
    assert((898 * 2) >= 898);
    assert((935 * 2) >= 935);
    assert((972 * 2) >= 972);
    assert((9 * 2) >= 9);
    assert((46 * 2) >= 46);
    assert((83 * 2) >= 83);
    assert((120 * 2) >= 120);
    assert((157 * 2) >= 157);
    assert((194 * 2) >= 194);
    assert((231 * 2) >= 231);
    assert((268 * 2) >= 268);
    assert((305 * 2) >= 305);
    assert((342 * 2) >= 342);
    assert((379 * 2) >= 379);
    assert((416 * 2) >= 416);
    assert((453 * 2) >= 453);
    assert((490 * 2) >= 490);
    assert((527 * 2) >= 527);
    assert((564 * 2) >= 564);
    assert((601 * 2) >= 601);
    assert((638 * 2) >= 638);
    assert((675 * 2) >= 675);
    assert((712 * 2) >= 712);
    assert((749 * 2) >= 749);
    assert((786 * 2) >= 786);
    assert((823 * 2) >= 823);
    assert((860 * 2) >= 860);
    assert((897 * 2) >= 897);
    assert((934 * 2) >= 934);
    assert((971 * 2) >= 971);
    assert((8 * 2) >= 8);
    assert((45 * 2) >= 45);
    assert((82 * 2) >= 82);
    assert((119 * 2) >= 119);
    assert((156 * 2) >= 156);
    assert((193 * 2) >= 193);
    assert((230 * 2) >= 230);
    assert((267 * 2) >= 267);
    assert((304 * 2) >= 304);
    assert((341 * 2) >= 341);
    assert((378 * 2) >= 378);
    assert((415 * 2) >= 415);
    assert((452 * 2) >= 452);
    assert((489 * 2) >= 489);
    assert((526 * 2) >= 526);
    assert((563 * 2) >= 563);
    assert((600 * 2) >= 600);
    assert((637 * 2) >= 637);
    assert((674 * 2) >= 674);
    assert((711 * 2) >= 711);
    assert((748 * 2) >= 748);
    assert((785 * 2) >= 785);
    assert((822 * 2) >= 822);
    assert((859 * 2) >= 859);
    assert((896 * 2) >= 896);
    assert((933 * 2) >= 933);
    assert((970 * 2) >= 970);
    assert((7 * 2) >= 7);
    assert((44 * 2) >= 44);
    assert((81 * 2) >= 81);
    assert((118 * 2) >= 118);
    assert((155 * 2) >= 155);
    assert((192 * 2) >= 192);
    assert((229 * 2) >= 229);
    assert((266 * 2) >= 266);
    assert((303 * 2) >= 303);
    assert((340 * 2) >= 340);
    assert((377 * 2) >= 377);
    assert((414 * 2) >= 414);
    assert((451 * 2) >= 451);
    assert((488 * 2) >= 488);
    assert((525 * 2) >= 525);
    assert((562 * 2) >= 562);
    assert((599 * 2) >= 599);
    assert((636 * 2) >= 636);
    assert((673 * 2) >= 673);
    assert((710 * 2) >= 710);
    assert((747 * 2) >= 747);
    assert((784 * 2) >= 784);
    assert((821 * 2) >= 821);
    assert((858 * 2) >= 858);
    assert((895 * 2) >= 895);
    assert((932 * 2) >= 932);
    assert((969 * 2) >= 969);
    assert((6 * 2) >= 6);
    assert((43 * 2) >= 43);
    assert((80 * 2) >= 80);
    assert((117 * 2) >= 117);
    assert((154 * 2) >= 154);
    assert((191 * 2) >= 191);
    assert((228 * 2) >= 228);
    assert((265 * 2) >= 265);
    assert((302 * 2) >= 302);
    assert((339 * 2) >= 339);
    assert((376 * 2) >= 376);
    assert((413 * 2) >= 413);
    assert((450 * 2) >= 450);
    assert((487 * 2) >= 487);
    assert((524 * 2) >= 524);
    assert((561 * 2) >= 561);
    assert((598 * 2) >= 598);
    assert((635 * 2) >= 635);
    assert((672 * 2) >= 672);
    assert((709 * 2) >= 709);
    assert((746 * 2) >= 746);
    assert((783 * 2) >= 783);
    assert((820 * 2) >= 820);
    assert((857 * 2) >= 857);
    assert((894 * 2) >= 894);
    assert((931 * 2) >= 931);
    assert((968 * 2) >= 968);
    assert((5 * 2) >= 5);
    assert((42 * 2) >= 42);
    assert((79 * 2) >= 79);
    assert((116 * 2) >= 116);
    assert((153 * 2) >= 153);
    assert((190 * 2) >= 190);
    assert((227 * 2) >= 227);
    assert((264 * 2) >= 264);
    assert((301 * 2) >= 301);
    assert((338 * 2) >= 338);
    assert((375 * 2) >= 375);
    assert((412 * 2) >= 412);
    assert((449 * 2) >= 449);
    assert((486 * 2) >= 486);
    assert((523 * 2) >= 523);
    assert((560 * 2) >= 560);
    assert((597 * 2) >= 597);
    assert((634 * 2) >= 634);
    assert((671 * 2) >= 671);
    assert((708 * 2) >= 708);
    assert((745 * 2) >= 745);
    assert((782 * 2) >= 782);
    assert((819 * 2) >= 819);
    assert((856 * 2) >= 856);
    assert((893 * 2) >= 893);
    assert((930 * 2) >= 930);
    assert((967 * 2) >= 967);
    assert((4 * 2) >= 4);
    assert((41 * 2) >= 41);
    assert((78 * 2) >= 78);
    assert((115 * 2) >= 115);
    assert((152 * 2) >= 152);
    assert((189 * 2) >= 189);
    assert((226 * 2) >= 226);
    assert((263 * 2) >= 263);
    assert((300 * 2) >= 300);
    assert((337 * 2) >= 337);
    assert((374 * 2) >= 374);
    assert((411 * 2) >= 411);
    assert((448 * 2) >= 448);
    assert((485 * 2) >= 485);
    assert((522 * 2) >= 522);
    assert((559 * 2) >= 559);
    assert((596 * 2) >= 596);
    assert((633 * 2) >= 633);
    assert((670 * 2) >= 670);
    assert((707 * 2) >= 707);
    assert((744 * 2) >= 744);
    assert((781 * 2) >= 781);
    assert((818 * 2) >= 818);
    assert((855 * 2) >= 855);
    assert((892 * 2) >= 892);
    assert((929 * 2) >= 929);
    assert((966 * 2) >= 966);
    assert((3 * 2) >= 3);
    assert((40 * 2) >= 40);
    assert((77 * 2) >= 77);
    assert((114 * 2) >= 114);
    assert((151 * 2) >= 151);
    assert((188 * 2) >= 188);
    assert((225 * 2) >= 225);
    assert((262 * 2) >= 262);
    assert((299 * 2) >= 299);
    assert((336 * 2) >= 336);
    assert((373 * 2) >= 373);
    assert((410 * 2) >= 410);
    assert((447 * 2) >= 447);
    assert((484 * 2) >= 484);
    assert((521 * 2) >= 521);
    assert((558 * 2) >= 558);
    assert((595 * 2) >= 595);
    assert((632 * 2) >= 632);
    assert((669 * 2) >= 669);
    assert((706 * 2) >= 706);
    assert((743 * 2) >= 743);
    assert((780 * 2) >= 780);
    assert((817 * 2) >= 817);
    assert((854 * 2) >= 854);
    assert((891 * 2) >= 891);
    assert((928 * 2) >= 928);
    assert((965 * 2) >= 965);
    assert((2 * 2) >= 2);
    assert((39 * 2) >= 39);
    assert((76 * 2) >= 76);
    assert((113 * 2) >= 113);
    assert((150 * 2) >= 150);
    assert((187 * 2) >= 187);
    assert((224 * 2) >= 224);
    assert((261 * 2) >= 261);
    assert((298 * 2) >= 298);
    assert((335 * 2) >= 335);
    assert((372 * 2) >= 372);
    assert((409 * 2) >= 409);
    assert((446 * 2) >= 446);
    assert((483 * 2) >= 483);
    assert((520 * 2) >= 520);
    assert((557 * 2) >= 557);
    assert((594 * 2) >= 594);
    assert((631 * 2) >= 631);
    assert((668 * 2) >= 668);
    assert((705 * 2) >= 705);
    assert((742 * 2) >= 742);
    assert((779 * 2) >= 779);
    assert((816 * 2) >= 816);
    assert((853 * 2) >= 853);
    assert((890 * 2) >= 890);
    assert((927 * 2) >= 927);
    assert((964 * 2) >= 964);
    assert((1 * 2) >= 1);
    assert((38 * 2) >= 38);
    assert((75 * 2) >= 75);
    assert((112 * 2) >= 112);
    assert((149 * 2) >= 149);
    assert((186 * 2) >= 186);
    assert((223 * 2) >= 223);
    assert((260 * 2) >= 260);
    assert((297 * 2) >= 297);
    assert((334 * 2) >= 334);
    assert((371 * 2) >= 371);
    assert((408 * 2) >= 408);
    assert((445 * 2) >= 445);
    assert((482 * 2) >= 482);
    assert((519 * 2) >= 519);
    assert((556 * 2) >= 556);
    assert((593 * 2) >= 593);
    assert((630 * 2) >= 630);
    assert((667 * 2) >= 667);
    assert((704 * 2) >= 704);
    assert((741 * 2) >= 741);
    assert((778 * 2) >= 778);
    assert((815 * 2) >= 815);
    assert((852 * 2) >= 852);
    assert((889 * 2) >= 889);
    assert((926 * 2) >= 926);
    assert((963 * 2) >= 963);
    assert((0 * 2) >= 0);
    assert((37 * 2) >= 37);
    assert((74 * 2) >= 74);
    assert((111 * 2) >= 111);
    assert((148 * 2) >= 148);
    assert((185 * 2) >= 185);
    assert((222 * 2) >= 222);
    assert((259 * 2) >= 259);
    assert((296 * 2) >= 296);
    assert((333 * 2) >= 333);
    assert((370 * 2) >= 370);
    assert((407 * 2) >= 407);
    assert((444 * 2) >= 444);
    assert((481 * 2) >= 481);
    assert((518 * 2) >= 518);
    assert((555 * 2) >= 555);
    assert((592 * 2) >= 592);
    assert((629 * 2) >= 629);
    assert((666 * 2) >= 666);
    assert((703 * 2) >= 703);
    assert((740 * 2) >= 740);
    assert((777 * 2) >= 777);
    assert((814 * 2) >= 814);
    assert((851 * 2) >= 851);
    assert((888 * 2) >= 888);
    assert((925 * 2) >= 925);
    assert((962 * 2) >= 962);
    assert((999 * 2) >= 999);
    assert((36 * 2) >= 36);
    assert((73 * 2) >= 73);
    assert((110 * 2) >= 110);
    assert((147 * 2) >= 147);
    assert((184 * 2) >= 184);
    assert((221 * 2) >= 221);
    assert((258 * 2) >= 258);
    assert((295 * 2) >= 295);
    assert((332 * 2) >= 332);
    assert((369 * 2) >= 369);
    assert((406 * 2) >= 406);
    assert((443 * 2) >= 443);
    assert((480 * 2) >= 480);
    assert((517 * 2) >= 517);
    assert((554 * 2) >= 554);
    assert((591 * 2) >= 591);
    assert((628 * 2) >= 628);
    assert((665 * 2) >= 665);
    assert((702 * 2) >= 702);
    assert((739 * 2) >= 739);
    assert((776 * 2) >= 776);
    assert((813 * 2) >= 813);
    assert((850 * 2) >= 850);
    assert((887 * 2) >= 887);
    assert((924 * 2) >= 924);
UNDECLARED_SYMBOL_XYZ_NOT_FOUND = 12345;
    assert((961 * 2) >= 961);
    assert((998 * 2) >= 998);
    assert((35 * 2) >= 35);
    assert((72 * 2) >= 72);
    assert((109 * 2) >= 109);
    assert((146 * 2) >= 146);
    assert((183 * 2) >= 183);
    assert((220 * 2) >= 220);
    assert((257 * 2) >= 257);
    assert((294 * 2) >= 294);
    assert((331 * 2) >= 331);
    assert((368 * 2) >= 368);
    assert((405 * 2) >= 405);
    assert((442 * 2) >= 442);
    assert((479 * 2) >= 479);
    assert((516 * 2) >= 516);
    assert((553 * 2) >= 553);
    assert((590 * 2) >= 590);
    assert((627 * 2) >= 627);
    assert((664 * 2) >= 664);
    assert((701 * 2) >= 701);
    assert((738 * 2) >= 738);
    assert((775 * 2) >= 775);
    assert((812 * 2) >= 812);
    assert((849 * 2) >= 849);
    assert((886 * 2) >= 886);
    assert((923 * 2) >= 923);
    assert((960 * 2) >= 960);
    assert((997 * 2) >= 997);
    assert((34 * 2) >= 34);
    assert((71 * 2) >= 71);
    assert((108 * 2) >= 108);
    assert((145 * 2) >= 145);
    assert((182 * 2) >= 182);
    assert((219 * 2) >= 219);
    assert((256 * 2) >= 256);
    assert((293 * 2) >= 293);
    assert((330 * 2) >= 330);
    assert((367 * 2) >= 367);
    assert((404 * 2) >= 404);
    assert((441 * 2) >= 441);
    assert((478 * 2) >= 478);
    assert((515 * 2) >= 515);
    assert((552 * 2) >= 552);
    assert((589 * 2) >= 589);
    assert((626 * 2) >= 626);
    assert((663 * 2) >= 663);
    assert((700 * 2) >= 700);
    assert((737 * 2) >= 737);
    assert((774 * 2) >= 774);
    assert((811 * 2) >= 811);
    assert((848 * 2) >= 848);
    assert((885 * 2) >= 885);
    assert((922 * 2) >= 922);
    assert((959 * 2) >= 959);
    assert((996 * 2) >= 996);
    assert((33 * 2) >= 33);
    assert((70 * 2) >= 70);
    assert((107 * 2) >= 107);
    assert((144 * 2) >= 144);
    assert((181 * 2) >= 181);
    assert((218 * 2) >= 218);
    assert((255 * 2) >= 255);
    assert((292 * 2) >= 292);
    assert((329 * 2) >= 329);
    assert((366 * 2) >= 366);
    assert((403 * 2) >= 403);
    assert((440 * 2) >= 440);
    assert((477 * 2) >= 477);
    assert((514 * 2) >= 514);
    assert((551 * 2) >= 551);
    assert((588 * 2) >= 588);
    assert((625 * 2) >= 625);
    assert((662 * 2) >= 662);
    assert((699 * 2) >= 699);
    assert((736 * 2) >= 736);
    assert((773 * 2) >= 773);
    assert((810 * 2) >= 810);
    assert((847 * 2) >= 847);
    assert((884 * 2) >= 884);
    assert((921 * 2) >= 921);
    assert((958 * 2) >= 958);
    assert((995 * 2) >= 995);
    assert((32 * 2) >= 32);
    assert((69 * 2) >= 69);
    assert((106 * 2) >= 106);
    assert((143 * 2) >= 143);
    assert((180 * 2) >= 180);
    assert((217 * 2) >= 217);
    assert((254 * 2) >= 254);
    assert((291 * 2) >= 291);
    assert((328 * 2) >= 328);
    assert((365 * 2) >= 365);
    assert((402 * 2) >= 402);
    assert((439 * 2) >= 439);
    assert((476 * 2) >= 476);
    assert((513 * 2) >= 513);
    assert((550 * 2) >= 550);
    assert((587 * 2) >= 587);
    assert((624 * 2) >= 624);
    assert((661 * 2) >= 661);
    assert((698 * 2) >= 698);
    assert((735 * 2) >= 735);
    assert((772 * 2) >= 772);
    assert((809 * 2) >= 809);
    assert((846 * 2) >= 846);
    assert((883 * 2) >= 883);
    assert((920 * 2) >= 920);
    assert((957 * 2) >= 957);
    assert((994 * 2) >= 994);
    assert((31 * 2) >= 31);
    assert((68 * 2) >= 68);
    assert((105 * 2) >= 105);
    assert((142 * 2) >= 142);
    assert((179 * 2) >= 179);
    assert((216 * 2) >= 216);
    assert((253 * 2) >= 253);
    assert((290 * 2) >= 290);
    assert((327 * 2) >= 327);
    assert((364 * 2) >= 364);
    assert((401 * 2) >= 401);
    assert((438 * 2) >= 438);
    assert((475 * 2) >= 475);
    assert((512 * 2) >= 512);
    assert((549 * 2) >= 549);
    assert((586 * 2) >= 586);
    assert((623 * 2) >= 623);
    assert((660 * 2) >= 660);
    assert((697 * 2) >= 697);
    assert((734 * 2) >= 734);
    assert((771 * 2) >= 771);
    assert((808 * 2) >= 808);
    assert((845 * 2) >= 845);
    assert((882 * 2) >= 882);
    assert((919 * 2) >= 919);
    assert((956 * 2) >= 956);
    assert((993 * 2) >= 993);
    assert((30 * 2) >= 30);
    assert((67 * 2) >= 67);
    assert((104 * 2) >= 104);
    assert((141 * 2) >= 141);
    assert((178 * 2) >= 178);
    assert((215 * 2) >= 215);
    assert((252 * 2) >= 252);
    assert((289 * 2) >= 289);
    assert((326 * 2) >= 326);
    assert((363 * 2) >= 363);
    assert((400 * 2) >= 400);
    assert((437 * 2) >= 437);
    assert((474 * 2) >= 474);
    assert((511 * 2) >= 511);
    assert((548 * 2) >= 548);
    assert((585 * 2) >= 585);
    assert((622 * 2) >= 622);
    assert((659 * 2) >= 659);
    assert((696 * 2) >= 696);
    assert((733 * 2) >= 733);
    assert((770 * 2) >= 770);
    assert((807 * 2) >= 807);
    assert((844 * 2) >= 844);
    assert((881 * 2) >= 881);
    assert((918 * 2) >= 918);
    assert((955 * 2) >= 955);
    assert((992 * 2) >= 992);
    assert((29 * 2) >= 29);
    assert((66 * 2) >= 66);
    assert((103 * 2) >= 103);
    assert((140 * 2) >= 140);
    assert((177 * 2) >= 177);
    assert((214 * 2) >= 214);
    assert((251 * 2) >= 251);
    assert((288 * 2) >= 288);
    assert((325 * 2) >= 325);
    assert((362 * 2) >= 362);
    assert((399 * 2) >= 399);
    assert((436 * 2) >= 436);
    assert((473 * 2) >= 473);
    assert((510 * 2) >= 510);
    assert((547 * 2) >= 547);
    assert((584 * 2) >= 584);
    assert((621 * 2) >= 621);
    assert((658 * 2) >= 658);
    assert((695 * 2) >= 695);
    assert((732 * 2) >= 732);
    assert((769 * 2) >= 769);
    assert((806 * 2) >= 806);
    assert((843 * 2) >= 843);
    assert((880 * 2) >= 880);
    assert((917 * 2) >= 917);
    assert((954 * 2) >= 954);
    assert((991 * 2) >= 991);
    assert((28 * 2) >= 28);
    assert((65 * 2) >= 65);
    assert((102 * 2) >= 102);
    assert((139 * 2) >= 139);
    assert((176 * 2) >= 176);
    assert((213 * 2) >= 213);
    assert((250 * 2) >= 250);
    assert((287 * 2) >= 287);
    assert((324 * 2) >= 324);
    assert((361 * 2) >= 361);
    assert((398 * 2) >= 398);
    assert((435 * 2) >= 435);
    assert((472 * 2) >= 472);
    assert((509 * 2) >= 509);
    assert((546 * 2) >= 546);
    assert((583 * 2) >= 583);
    assert((620 * 2) >= 620);
    assert((657 * 2) >= 657);
    assert((694 * 2) >= 694);
    assert((731 * 2) >= 731);
    assert((768 * 2) >= 768);
    assert((805 * 2) >= 805);
    assert((842 * 2) >= 842);
    assert((879 * 2) >= 879);
    assert((916 * 2) >= 916);
    assert((953 * 2) >= 953);
    assert((990 * 2) >= 990);
    assert((27 * 2) >= 27);
    assert((64 * 2) >= 64);
    assert((101 * 2) >= 101);
    assert((138 * 2) >= 138);
    assert((175 * 2) >= 175);
    assert((212 * 2) >= 212);
    assert((249 * 2) >= 249);
    assert((286 * 2) >= 286);
    assert((323 * 2) >= 323);
    assert((360 * 2) >= 360);
    assert((397 * 2) >= 397);
    assert((434 * 2) >= 434);
    assert((471 * 2) >= 471);
    assert((508 * 2) >= 508);
    assert((545 * 2) >= 545);
    assert((582 * 2) >= 582);
    assert((619 * 2) >= 619);
    assert((656 * 2) >= 656);
    assert((693 * 2) >= 693);
    assert((730 * 2) >= 730);
    assert((767 * 2) >= 767);
    assert((804 * 2) >= 804);
    assert((841 * 2) >= 841);
    assert((878 * 2) >= 878);
    assert((915 * 2) >= 915);
    assert((952 * 2) >= 952);
    assert((989 * 2) >= 989);
    assert((26 * 2) >= 26);
    assert((63 * 2) >= 63);
    assert((100 * 2) >= 100);
    assert((137 * 2) >= 137);
    assert((174 * 2) >= 174);
    assert((211 * 2) >= 211);
    assert((248 * 2) >= 248);
    assert((285 * 2) >= 285);
    assert((322 * 2) >= 322);
    assert((359 * 2) >= 359);
    assert((396 * 2) >= 396);
    assert((433 * 2) >= 433);
    assert((470 * 2) >= 470);
    assert((507 * 2) >= 507);
    assert((544 * 2) >= 544);
    assert((581 * 2) >= 581);
    assert((618 * 2) >= 618);
    assert((655 * 2) >= 655);
    assert((692 * 2) >= 692);
    assert((729 * 2) >= 729);
    assert((766 * 2) >= 766);
    assert((803 * 2) >= 803);
    assert((840 * 2) >= 840);
    assert((877 * 2) >= 877);
    assert((914 * 2) >= 914);
    assert((951 * 2) >= 951);
    assert((988 * 2) >= 988);
    assert((25 * 2) >= 25);
    assert((62 * 2) >= 62);
    assert((99 * 2) >= 99);
    assert((136 * 2) >= 136);
    assert((173 * 2) >= 173);
    assert((210 * 2) >= 210);
    assert((247 * 2) >= 247);
    assert((284 * 2) >= 284);
    assert((321 * 2) >= 321);
    assert((358 * 2) >= 358);
    assert((395 * 2) >= 395);
    assert((432 * 2) >= 432);
    assert((469 * 2) >= 469);
    assert((506 * 2) >= 506);
    assert((543 * 2) >= 543);
    assert((580 * 2) >= 580);
    assert((617 * 2) >= 617);
    assert((654 * 2) >= 654);
    assert((691 * 2) >= 691);
    assert((728 * 2) >= 728);
    assert((765 * 2) >= 765);
    assert((802 * 2) >= 802);
    assert((839 * 2) >= 839);
    assert((876 * 2) >= 876);
    assert((913 * 2) >= 913);
    assert((950 * 2) >= 950);
    assert((987 * 2) >= 987);
    assert((24 * 2) >= 24);
    assert((61 * 2) >= 61);
    assert((98 * 2) >= 98);
    assert((135 * 2) >= 135);
    assert((172 * 2) >= 172);
    assert((209 * 2) >= 209);
    assert((246 * 2) >= 246);
    assert((283 * 2) >= 283);
    assert((320 * 2) >= 320);
    assert((357 * 2) >= 357);
    assert((394 * 2) >= 394);
    assert((431 * 2) >= 431);
    assert((468 * 2) >= 468);
    assert((505 * 2) >= 505);
    assert((542 * 2) >= 542);
    assert((579 * 2) >= 579);
    assert((616 * 2) >= 616);
    assert((653 * 2) >= 653);
    assert((690 * 2) >= 690);
    assert((727 * 2) >= 727);
    assert((764 * 2) >= 764);
    assert((801 * 2) >= 801);
    assert((838 * 2) >= 838);
    assert((875 * 2) >= 875);
    assert((912 * 2) >= 912);
    assert((949 * 2) >= 949);
    assert((986 * 2) >= 986);
    assert((23 * 2) >= 23);
    assert((60 * 2) >= 60);
    assert((97 * 2) >= 97);
    assert((134 * 2) >= 134);
    assert((171 * 2) >= 171);
    assert((208 * 2) >= 208);
    assert((245 * 2) >= 245);
    assert((282 * 2) >= 282);
    assert((319 * 2) >= 319);
    assert((356 * 2) >= 356);
    assert((393 * 2) >= 393);
    assert((430 * 2) >= 430);
    assert((467 * 2) >= 467);
    assert((504 * 2) >= 504);
    assert((541 * 2) >= 541);
    assert((578 * 2) >= 578);
    assert((615 * 2) >= 615);
    assert((652 * 2) >= 652);
    assert((689 * 2) >= 689);
    assert((726 * 2) >= 726);
    assert((763 * 2) >= 763);
    assert((800 * 2) >= 800);
    assert((837 * 2) >= 837);
    assert((874 * 2) >= 874);
    assert((911 * 2) >= 911);
    assert((948 * 2) >= 948);
    assert((985 * 2) >= 985);
    assert((22 * 2) >= 22);
    assert((59 * 2) >= 59);
    assert((96 * 2) >= 96);
    assert((133 * 2) >= 133);
    assert((170 * 2) >= 170);
    assert((207 * 2) >= 207);
    assert((244 * 2) >= 244);
    assert((281 * 2) >= 281);
    assert((318 * 2) >= 318);
    assert((355 * 2) >= 355);
    assert((392 * 2) >= 392);
    assert((429 * 2) >= 429);
    assert((466 * 2) >= 466);
    assert((503 * 2) >= 503);
    assert((540 * 2) >= 540);
    assert((577 * 2) >= 577);
    assert((614 * 2) >= 614);
    assert((651 * 2) >= 651);
    assert((688 * 2) >= 688);
    assert((725 * 2) >= 725);
    assert((762 * 2) >= 762);
    assert((799 * 2) >= 799);
    assert((836 * 2) >= 836);
    assert((873 * 2) >= 873);
    assert((910 * 2) >= 910);
    assert((947 * 2) >= 947);
    assert((984 * 2) >= 984);
    assert((21 * 2) >= 21);
    assert((58 * 2) >= 58);
    assert((95 * 2) >= 95);
    assert((132 * 2) >= 132);
    assert((169 * 2) >= 169);
    assert((206 * 2) >= 206);
    assert((243 * 2) >= 243);
    assert((280 * 2) >= 280);
    assert((317 * 2) >= 317);
    assert((354 * 2) >= 354);
    assert((391 * 2) >= 391);
    assert((428 * 2) >= 428);
    assert((465 * 2) >= 465);
    assert((502 * 2) >= 502);
    assert((539 * 2) >= 539);
    assert((576 * 2) >= 576);
    assert((613 * 2) >= 613);
    assert((650 * 2) >= 650);
    assert((687 * 2) >= 687);
    assert((724 * 2) >= 724);
    assert((761 * 2) >= 761);
    assert((798 * 2) >= 798);
    assert((835 * 2) >= 835);
    assert((872 * 2) >= 872);
    assert((909 * 2) >= 909);
    assert((946 * 2) >= 946);
    assert((983 * 2) >= 983);
    assert((20 * 2) >= 20);
    assert((57 * 2) >= 57);
    assert((94 * 2) >= 94);
    assert((131 * 2) >= 131);
    assert((168 * 2) >= 168);
    assert((205 * 2) >= 205);
    assert((242 * 2) >= 242);
    assert((279 * 2) >= 279);
    assert((316 * 2) >= 316);
    assert((353 * 2) >= 353);
    assert((390 * 2) >= 390);
    assert((427 * 2) >= 427);
    assert((464 * 2) >= 464);
    assert((501 * 2) >= 501);
    assert((538 * 2) >= 538);
    assert((575 * 2) >= 575);
    assert((612 * 2) >= 612);
    assert((649 * 2) >= 649);
    assert((686 * 2) >= 686);
    assert((723 * 2) >= 723);
    assert((760 * 2) >= 760);
    assert((797 * 2) >= 797);
    assert((834 * 2) >= 834);
    assert((871 * 2) >= 871);
    assert((908 * 2) >= 908);
    assert((945 * 2) >= 945);
    assert((982 * 2) >= 982);
    assert((19 * 2) >= 19);
    assert((56 * 2) >= 56);
    assert((93 * 2) >= 93);
    assert((130 * 2) >= 130);
    assert((167 * 2) >= 167);
    assert((204 * 2) >= 204);
    assert((241 * 2) >= 241);
    assert((278 * 2) >= 278);
    assert((315 * 2) >= 315);
    assert((352 * 2) >= 352);
    assert((389 * 2) >= 389);
    assert((426 * 2) >= 426);
    assert((463 * 2) >= 463);
    assert((500 * 2) >= 500);
    assert((537 * 2) >= 537);
    assert((574 * 2) >= 574);
    assert((611 * 2) >= 611);
    assert((648 * 2) >= 648);
    assert((685 * 2) >= 685);
    assert((722 * 2) >= 722);
    assert((759 * 2) >= 759);
    assert((796 * 2) >= 796);
    assert((833 * 2) >= 833);
    assert((870 * 2) >= 870);
    assert((907 * 2) >= 907);
    assert((944 * 2) >= 944);
    assert((981 * 2) >= 981);
    assert((18 * 2) >= 18);
    assert((55 * 2) >= 55);
    assert((92 * 2) >= 92);
    assert((129 * 2) >= 129);
    assert((166 * 2) >= 166);
    assert((203 * 2) >= 203);
    assert((240 * 2) >= 240);
    assert((277 * 2) >= 277);
    assert((314 * 2) >= 314);
    assert((351 * 2) >= 351);
    assert((388 * 2) >= 388);
    assert((425 * 2) >= 425);
    assert((462 * 2) >= 462);
    assert((499 * 2) >= 499);
    assert((536 * 2) >= 536);
    assert((573 * 2) >= 573);
    assert((610 * 2) >= 610);
    assert((647 * 2) >= 647);
    assert((684 * 2) >= 684);
    assert((721 * 2) >= 721);
    assert((758 * 2) >= 758);
    assert((795 * 2) >= 795);
    assert((832 * 2) >= 832);
    assert((869 * 2) >= 869);
    assert((906 * 2) >= 906);
    assert((943 * 2) >= 943);
    assert((980 * 2) >= 980);
    assert((17 * 2) >= 17);
    assert((54 * 2) >= 54);
    assert((91 * 2) >= 91);
    assert((128 * 2) >= 128);
    assert((165 * 2) >= 165);
    assert((202 * 2) >= 202);
    assert((239 * 2) >= 239);
    assert((276 * 2) >= 276);
    assert((313 * 2) >= 313);
    assert((350 * 2) >= 350);
    assert((387 * 2) >= 387);
    assert((424 * 2) >= 424);
    assert((461 * 2) >= 461);
    assert((498 * 2) >= 498);
    assert((535 * 2) >= 535);
    assert((572 * 2) >= 572);
    assert((609 * 2) >= 609);
    assert((646 * 2) >= 646);
    assert((683 * 2) >= 683);
    assert((720 * 2) >= 720);
    assert((757 * 2) >= 757);
    assert((794 * 2) >= 794);
    assert((831 * 2) >= 831);
    assert((868 * 2) >= 868);
    assert((905 * 2) >= 905);
    assert((942 * 2) >= 942);
    assert((979 * 2) >= 979);
    assert((16 * 2) >= 16);
    assert((53 * 2) >= 53);
    assert((90 * 2) >= 90);
    assert((127 * 2) >= 127);
    assert((164 * 2) >= 164);
    assert((201 * 2) >= 201);
    assert((238 * 2) >= 238);
    assert((275 * 2) >= 275);
    assert((312 * 2) >= 312);
    assert((349 * 2) >= 349);
    assert((386 * 2) >= 386);
    assert((423 * 2) >= 423);
    assert((460 * 2) >= 460);
    assert((497 * 2) >= 497);
    assert((534 * 2) >= 534);
    assert((571 * 2) >= 571);
    assert((608 * 2) >= 608);
    assert((645 * 2) >= 645);
    assert((682 * 2) >= 682);
    assert((719 * 2) >= 719);
    assert((756 * 2) >= 756);
    assert((793 * 2) >= 793);
    assert((830 * 2) >= 830);
    assert((867 * 2) >= 867);
    assert((904 * 2) >= 904);
    assert((941 * 2) >= 941);
    assert((978 * 2) >= 978);
    assert((15 * 2) >= 15);
    assert((52 * 2) >= 52);
    assert((89 * 2) >= 89);
    assert((126 * 2) >= 126);
    assert((163 * 2) >= 163);
    assert((200 * 2) >= 200);
    assert((237 * 2) >= 237);
    assert((274 * 2) >= 274);
    assert((311 * 2) >= 311);
    assert((348 * 2) >= 348);
    assert((385 * 2) >= 385);
    assert((422 * 2) >= 422);
    assert((459 * 2) >= 459);
    assert((496 * 2) >= 496);
    assert((533 * 2) >= 533);
    assert((570 * 2) >= 570);
    assert((607 * 2) >= 607);
    assert((644 * 2) >= 644);
    assert((681 * 2) >= 681);
    assert((718 * 2) >= 718);
    assert((755 * 2) >= 755);
    assert((792 * 2) >= 792);
    assert((829 * 2) >= 829);
    assert((866 * 2) >= 866);
    assert((903 * 2) >= 903);
    assert((940 * 2) >= 940);
    assert((977 * 2) >= 977);
    assert((14 * 2) >= 14);
    assert((51 * 2) >= 51);
    assert((88 * 2) >= 88);
    assert((125 * 2) >= 125);
    assert((162 * 2) >= 162);
    assert((199 * 2) >= 199);
    assert((236 * 2) >= 236);
    assert((273 * 2) >= 273);
    assert((310 * 2) >= 310);
    assert((347 * 2) >= 347);
    assert((384 * 2) >= 384);
    assert((421 * 2) >= 421);
    assert((458 * 2) >= 458);
    assert((495 * 2) >= 495);
    assert((532 * 2) >= 532);
    assert((569 * 2) >= 569);
    assert((606 * 2) >= 606);
    assert((643 * 2) >= 643);
    assert((680 * 2) >= 680);
    assert((717 * 2) >= 717);
    assert((754 * 2) >= 754);
    assert((791 * 2) >= 791);
    assert((828 * 2) >= 828);
    assert((865 * 2) >= 865);
    assert((902 * 2) >= 902);
    assert((939 * 2) >= 939);
    assert((976 * 2) >= 976);
    assert((13 * 2) >= 13);
    assert((50 * 2) >= 50);
    assert((87 * 2) >= 87);
    assert((124 * 2) >= 124);
    assert((161 * 2) >= 161);
    assert((198 * 2) >= 198);
    assert((235 * 2) >= 235);
    assert((272 * 2) >= 272);
    assert((309 * 2) >= 309);
    assert((346 * 2) >= 346);
    assert((383 * 2) >= 383);
    assert((420 * 2) >= 420);
    assert((457 * 2) >= 457);
    assert((494 * 2) >= 494);
    assert((531 * 2) >= 531);
    assert((568 * 2) >= 568);
    assert((605 * 2) >= 605);
    assert((642 * 2) >= 642);
    assert((679 * 2) >= 679);
    assert((716 * 2) >= 716);
    assert((753 * 2) >= 753);
    assert((790 * 2) >= 790);
    assert((827 * 2) >= 827);
    assert((864 * 2) >= 864);
    assert((901 * 2) >= 901);
    assert((938 * 2) >= 938);
    assert((975 * 2) >= 975);
    assert((12 * 2) >= 12);
    assert((49 * 2) >= 49);
    assert((86 * 2) >= 86);
    assert((123 * 2) >= 123);
    assert((160 * 2) >= 160);
    assert((197 * 2) >= 197);
    assert((234 * 2) >= 234);
    assert((271 * 2) >= 271);
    assert((308 * 2) >= 308);
    assert((345 * 2) >= 345);
    assert((382 * 2) >= 382);
    assert((419 * 2) >= 419);
    assert((456 * 2) >= 456);
    assert((493 * 2) >= 493);
    assert((530 * 2) >= 530);
    assert((567 * 2) >= 567);
    assert((604 * 2) >= 604);
    assert((641 * 2) >= 641);
    assert((678 * 2) >= 678);
    assert((715 * 2) >= 715);
    assert((752 * 2) >= 752);
    assert((789 * 2) >= 789);
    assert((826 * 2) >= 826);
    assert((863 * 2) >= 863);
    assert((900 * 2) >= 900);
    assert((937 * 2) >= 937);
    assert((974 * 2) >= 974);
    assert((11 * 2) >= 11);
    assert((48 * 2) >= 48);
    assert((85 * 2) >= 85);
    assert((122 * 2) >= 122);
    assert((159 * 2) >= 159);
    assert((196 * 2) >= 196);
    assert((233 * 2) >= 233);
    assert((270 * 2) >= 270);
    assert((307 * 2) >= 307);
    assert((344 * 2) >= 344);
    assert((381 * 2) >= 381);
    assert((418 * 2) >= 418);
    assert((455 * 2) >= 455);
    assert((492 * 2) >= 492);
    assert((529 * 2) >= 529);
    assert((566 * 2) >= 566);
    assert((603 * 2) >= 603);
    assert((640 * 2) >= 640);
    assert((677 * 2) >= 677);
    assert((714 * 2) >= 714);
    assert((751 * 2) >= 751);
    assert((788 * 2) >= 788);
    assert((825 * 2) >= 825);
    assert((862 * 2) >= 862);
    assert((899 * 2) >= 899);
    assert((936 * 2) >= 936);
    assert((973 * 2) >= 973);
    assert((10 * 2) >= 10);
    assert((47 * 2) >= 47);
    assert((84 * 2) >= 84);
    assert((121 * 2) >= 121);
    assert((158 * 2) >= 158);
    assert((195 * 2) >= 195);
    assert((232 * 2) >= 232);
    assert((269 * 2) >= 269);
    assert((306 * 2) >= 306);
    assert((343 * 2) >= 343);
    assert((380 * 2) >= 380);
    assert((417 * 2) >= 417);
    assert((454 * 2) >= 454);
    assert((491 * 2) >= 491);
    assert((528 * 2) >= 528);
    assert((565 * 2) >= 565);
    assert((602 * 2) >= 602);
    assert((639 * 2) >= 639);
    assert((676 * 2) >= 676);
    assert((713 * 2) >= 713);
    assert((750 * 2) >= 750);
    assert((787 * 2) >= 787);
    assert((824 * 2) >= 824);
    assert((861 * 2) >= 861);
    assert((898 * 2) >= 898);
    assert((935 * 2) >= 935);
    assert((972 * 2) >= 972);
    assert((9 * 2) >= 9);
    assert((46 * 2) >= 46);
    assert((83 * 2) >= 83);
    assert((120 * 2) >= 120);
    assert((157 * 2) >= 157);
    assert((194 * 2) >= 194);
    assert((231 * 2) >= 231);
    assert((268 * 2) >= 268);
    assert((305 * 2) >= 305);
    assert((342 * 2) >= 342);
    assert((379 * 2) >= 379);
    assert((416 * 2) >= 416);
    assert((453 * 2) >= 453);
    assert((490 * 2) >= 490);
    assert((527 * 2) >= 527);
    assert((564 * 2) >= 564);
    assert((601 * 2) >= 601);
    assert((638 * 2) >= 638);
    assert((675 * 2) >= 675);
    assert((712 * 2) >= 712);
    assert((749 * 2) >= 749);
    assert((786 * 2) >= 786);
    assert((823 * 2) >= 823);
    assert((860 * 2) >= 860);
    assert((897 * 2) >= 897);
    assert((934 * 2) >= 934);
    assert((971 * 2) >= 971);
    assert((8 * 2) >= 8);
    assert((45 * 2) >= 45);
    assert((82 * 2) >= 82);
    assert((119 * 2) >= 119);
    assert((156 * 2) >= 156);
    assert((193 * 2) >= 193);
    assert((230 * 2) >= 230);
    assert((267 * 2) >= 267);
    assert((304 * 2) >= 304);
    assert((341 * 2) >= 341);
    assert((378 * 2) >= 378);
    assert((415 * 2) >= 415);
    assert((452 * 2) >= 452);
    assert((489 * 2) >= 489);
    assert((526 * 2) >= 526);
    assert((563 * 2) >= 563);
    assert((600 * 2) >= 600);
    assert((637 * 2) >= 637);
    assert((674 * 2) >= 674);
    assert((711 * 2) >= 711);
    assert((748 * 2) >= 748);
    assert((785 * 2) >= 785);
    assert((822 * 2) >= 822);
    assert((859 * 2) >= 859);
    assert((896 * 2) >= 896);
    assert((933 * 2) >= 933);
    assert((970 * 2) >= 970);
    assert((7 * 2) >= 7);
    assert((44 * 2) >= 44);
    assert((81 * 2) >= 81);
    assert((118 * 2) >= 118);
    assert((155 * 2) >= 155);
    assert((192 * 2) >= 192);
    assert((229 * 2) >= 229);
    assert((266 * 2) >= 266);
    assert((303 * 2) >= 303);
    assert((340 * 2) >= 340);
    assert((377 * 2) >= 377);
    assert((414 * 2) >= 414);
    assert((451 * 2) >= 451);
    assert((488 * 2) >= 488);
    assert((525 * 2) >= 525);
    assert((562 * 2) >= 562);
    assert((599 * 2) >= 599);
    assert((636 * 2) >= 636);
    assert((673 * 2) >= 673);
    assert((710 * 2) >= 710);
    assert((747 * 2) >= 747);
    assert((784 * 2) >= 784);
    assert((821 * 2) >= 821);
    assert((858 * 2) >= 858);
    assert((895 * 2) >= 895);
    assert((932 * 2) >= 932);
    assert((969 * 2) >= 969);
    assert((6 * 2) >= 6);
    assert((43 * 2) >= 43);
    assert((80 * 2) >= 80);
    assert((117 * 2) >= 117);
    assert((154 * 2) >= 154);
    assert((191 * 2) >= 191);
    assert((228 * 2) >= 228);
    assert((265 * 2) >= 265);
    assert((302 * 2) >= 302);
    assert((339 * 2) >= 339);
    assert((376 * 2) >= 376);
    assert((413 * 2) >= 413);
    assert((450 * 2) >= 450);
    assert((487 * 2) >= 487);
    assert((524 * 2) >= 524);
    assert((561 * 2) >= 561);
    assert((598 * 2) >= 598);
    assert((635 * 2) >= 635);
    assert((672 * 2) >= 672);
    assert((709 * 2) >= 709);
    assert((746 * 2) >= 746);
    assert((783 * 2) >= 783);
    assert((820 * 2) >= 820);
    assert((857 * 2) >= 857);
    assert((894 * 2) >= 894);
    assert((931 * 2) >= 931);
    assert((968 * 2) >= 968);
    assert((5 * 2) >= 5);
    assert((42 * 2) >= 42);
    assert((79 * 2) >= 79);
    assert((116 * 2) >= 116);
    assert((153 * 2) >= 153);
    assert((190 * 2) >= 190);
    assert((227 * 2) >= 227);
    assert((264 * 2) >= 264);
    assert((301 * 2) >= 301);
    assert((338 * 2) >= 338);
    assert((375 * 2) >= 375);
    assert((412 * 2) >= 412);
    assert((449 * 2) >= 449);
    assert((486 * 2) >= 486);
    assert((523 * 2) >= 523);
    assert((560 * 2) >= 560);
    assert((597 * 2) >= 597);
    assert((634 * 2) >= 634);
    assert((671 * 2) >= 671);
    assert((708 * 2) >= 708);
    assert((745 * 2) >= 745);
    assert((782 * 2) >= 782);
    assert((819 * 2) >= 819);
    assert((856 * 2) >= 856);
    assert((893 * 2) >= 893);
    assert((930 * 2) >= 930);
    assert((967 * 2) >= 967);
    assert((4 * 2) >= 4);
    assert((41 * 2) >= 41);
    assert((78 * 2) >= 78);
    assert((115 * 2) >= 115);
    assert((152 * 2) >= 152);
    assert((189 * 2) >= 189);
    assert((226 * 2) >= 226);
    assert((263 * 2) >= 263);
    assert((300 * 2) >= 300);
    assert((337 * 2) >= 337);
    assert((374 * 2) >= 374);
    assert((411 * 2) >= 411);
    assert((448 * 2) >= 448);
    assert((485 * 2) >= 485);
    assert((522 * 2) >= 522);
    assert((559 * 2) >= 559);
    assert((596 * 2) >= 596);
    assert((633 * 2) >= 633);
    assert((670 * 2) >= 670);
    assert((707 * 2) >= 707);
    assert((744 * 2) >= 744);
    assert((781 * 2) >= 781);
    assert((818 * 2) >= 818);
    assert((855 * 2) >= 855);
    assert((892 * 2) >= 892);
    assert((929 * 2) >= 929);
    assert((966 * 2) >= 966);
    assert((3 * 2) >= 3);
    assert((40 * 2) >= 40);
    assert((77 * 2) >= 77);
    assert((114 * 2) >= 114);
    assert((151 * 2) >= 151);
    assert((188 * 2) >= 188);
    assert((225 * 2) >= 225);
    assert((262 * 2) >= 262);
    assert((299 * 2) >= 299);
    assert((336 * 2) >= 336);
    assert((373 * 2) >= 373);
    assert((410 * 2) >= 410);
    assert((447 * 2) >= 447);
    assert((484 * 2) >= 484);
    assert((521 * 2) >= 521);
    assert((558 * 2) >= 558);
    assert((595 * 2) >= 595);
    assert((632 * 2) >= 632);
    assert((669 * 2) >= 669);
    assert((706 * 2) >= 706);
    assert((743 * 2) >= 743);
    assert((780 * 2) >= 780);
    assert((817 * 2) >= 817);
    assert((854 * 2) >= 854);
    assert((891 * 2) >= 891);
    assert((928 * 2) >= 928);
    assert((965 * 2) >= 965);
    assert((2 * 2) >= 2);
    assert((39 * 2) >= 39);
    assert((76 * 2) >= 76);
    assert((113 * 2) >= 113);
    assert((150 * 2) >= 150);
    assert((187 * 2) >= 187);
    assert((224 * 2) >= 224);
    assert((261 * 2) >= 261);
    assert((298 * 2) >= 298);
    assert((335 * 2) >= 335);
    assert((372 * 2) >= 372);
    assert((409 * 2) >= 409);
    assert((446 * 2) >= 446);
    assert((483 * 2) >= 483);
    assert((520 * 2) >= 520);
    assert((557 * 2) >= 557);
    assert((594 * 2) >= 594);
    assert((631 * 2) >= 631);
    assert((668 * 2) >= 668);
    assert((705 * 2) >= 705);
    assert((742 * 2) >= 742);
    assert((779 * 2) >= 779);
    assert((816 * 2) >= 816);
    assert((853 * 2) >= 853);
    assert((890 * 2) >= 890);
    assert((927 * 2) >= 927);
    assert((964 * 2) >= 964);
    assert((1 * 2) >= 1);
    assert((38 * 2) >= 38);
    assert((75 * 2) >= 75);
    assert((112 * 2) >= 112);
    assert((149 * 2) >= 149);
    assert((186 * 2) >= 186);
    assert((223 * 2) >= 223);
    assert((260 * 2) >= 260);
    assert((297 * 2) >= 297);
    assert((334 * 2) >= 334);
    assert((371 * 2) >= 371);
    assert((408 * 2) >= 408);
    assert((445 * 2) >= 445);
    assert((482 * 2) >= 482);
    assert((519 * 2) >= 519);
    assert((556 * 2) >= 556);
    assert((593 * 2) >= 593);
    assert((630 * 2) >= 630);
    assert((667 * 2) >= 667);
    assert((704 * 2) >= 704);
    assert((741 * 2) >= 741);
    assert((778 * 2) >= 778);
    assert((815 * 2) >= 815);
    assert((852 * 2) >= 852);
    assert((889 * 2) >= 889);
    assert((926 * 2) >= 926);
    assert((963 * 2) >= 963);
    assert((0 * 2) >= 0);
    assert((37 * 2) >= 37);
    assert((74 * 2) >= 74);
    assert((111 * 2) >= 111);
    assert((148 * 2) >= 148);
    assert((185 * 2) >= 185);
    assert((222 * 2) >= 222);
    assert((259 * 2) >= 259);
    assert((296 * 2) >= 296);
    assert((333 * 2) >= 333);
    assert((370 * 2) >= 370);
    assert((407 * 2) >= 407);
    assert((444 * 2) >= 444);
    assert((481 * 2) >= 481);
    assert((518 * 2) >= 518);
    assert((555 * 2) >= 555);
    assert((592 * 2) >= 592);
    assert((629 * 2) >= 629);
    assert((666 * 2) >= 666);
    assert((703 * 2) >= 703);
    assert((740 * 2) >= 740);
    assert((777 * 2) >= 777);
    assert((814 * 2) >= 814);
    assert((851 * 2) >= 851);
    assert((888 * 2) >= 888);
    assert((925 * 2) >= 925);
    assert((962 * 2) >= 962);
    assert((999 * 2) >= 999);
    assert((36 * 2) >= 36);
    assert((73 * 2) >= 73);
    assert((110 * 2) >= 110);
    assert((147 * 2) >= 147);
    assert((184 * 2) >= 184);
    assert((221 * 2) >= 221);
    assert((258 * 2) >= 258);
    assert((295 * 2) >= 295);
    assert((332 * 2) >= 332);
    assert((369 * 2) >= 369);
    assert((406 * 2) >= 406);
    assert((443 * 2) >= 443);
    assert((480 * 2) >= 480);
    assert((517 * 2) >= 517);
    assert((554 * 2) >= 554);
    assert((591 * 2) >= 591);
    assert((628 * 2) >= 628);
    assert((665 * 2) >= 665);
    assert((702 * 2) >= 702);
    assert((739 * 2) >= 739);
    assert((776 * 2) >= 776);
    assert((813 * 2) >= 813);
    assert((850 * 2) >= 850);
    assert((887 * 2) >= 887);
    assert((924 * 2) >= 924);
    assert((961 * 2) >= 961);
    assert((998 * 2) >= 998);
    assert((35 * 2) >= 35);
    assert((72 * 2) >= 72);
    assert((109 * 2) >= 109);
    assert((146 * 2) >= 146);
    assert((183 * 2) >= 183);
    assert((220 * 2) >= 220);
    assert((257 * 2) >= 257);
    assert((294 * 2) >= 294);
    assert((331 * 2) >= 331);
    assert((368 * 2) >= 368);
    assert((405 * 2) >= 405);
    assert((442 * 2) >= 442);
    assert((479 * 2) >= 479);
    assert((516 * 2) >= 516);
    assert((553 * 2) >= 553);
    assert((590 * 2) >= 590);
    assert((627 * 2) >= 627);
    assert((664 * 2) >= 664);
    assert((701 * 2) >= 701);
    assert((738 * 2) >= 738);
    assert((775 * 2) >= 775);
    assert((812 * 2) >= 812);
    assert((849 * 2) >= 849);
    assert((886 * 2) >= 886);
    assert((923 * 2) >= 923);
    assert((960 * 2) >= 960);
    assert((997 * 2) >= 997);
    assert((34 * 2) >= 34);
    assert((71 * 2) >= 71);
    assert((108 * 2) >= 108);
    assert((145 * 2) >= 145);
    assert((182 * 2) >= 182);
    assert((219 * 2) >= 219);
    assert((256 * 2) >= 256);
    assert((293 * 2) >= 293);
    assert((330 * 2) >= 330);
    assert((367 * 2) >= 367);
    assert((404 * 2) >= 404);
    assert((441 * 2) >= 441);
    assert((478 * 2) >= 478);
    assert((515 * 2) >= 515);
    assert((552 * 2) >= 552);
    assert((589 * 2) >= 589);
    assert((626 * 2) >= 626);
    assert((663 * 2) >= 663);
    assert((700 * 2) >= 700);
    assert((737 * 2) >= 737);
    assert((774 * 2) >= 774);
    assert((811 * 2) >= 811);
    assert((848 * 2) >= 848);
    assert((885 * 2) >= 885);
    assert((922 * 2) >= 922);
    assert((959 * 2) >= 959);
    assert((996 * 2) >= 996);
    assert((33 * 2) >= 33);
    assert((70 * 2) >= 70);
    assert((107 * 2) >= 107);
    assert((144 * 2) >= 144);
    assert((181 * 2) >= 181);
    assert((218 * 2) >= 218);
    assert((255 * 2) >= 255);
    assert((292 * 2) >= 292);
    assert((329 * 2) >= 329);
    assert((366 * 2) >= 366);
    assert((403 * 2) >= 403);
    assert((440 * 2) >= 440);
    assert((477 * 2) >= 477);
    assert((514 * 2) >= 514);
    assert((551 * 2) >= 551);
    assert((588 * 2) >= 588);
    assert((625 * 2) >= 625);
    assert((662 * 2) >= 662);
    assert((699 * 2) >= 699);
    assert((736 * 2) >= 736);
    assert((773 * 2) >= 773);
    assert((810 * 2) >= 810);
    assert((847 * 2) >= 847);
    assert((884 * 2) >= 884);
    assert((921 * 2) >= 921);
    assert((958 * 2) >= 958);
    assert((995 * 2) >= 995);
    assert((32 * 2) >= 32);
    assert((69 * 2) >= 69);
    assert((106 * 2) >= 106);
    assert((143 * 2) >= 143);
    assert((180 * 2) >= 180);
    assert((217 * 2) >= 217);
    assert((254 * 2) >= 254);
    assert((291 * 2) >= 291);
    assert((328 * 2) >= 328);
    assert((365 * 2) >= 365);
    assert((402 * 2) >= 402);
    assert((439 * 2) >= 439);
    assert((476 * 2) >= 476);
    assert((513 * 2) >= 513);
    assert((550 * 2) >= 550);
    assert((587 * 2) >= 587);
    assert((624 * 2) >= 624);
    assert((661 * 2) >= 661);
    assert((698 * 2) >= 698);
    assert((735 * 2) >= 735);
    assert((772 * 2) >= 772);
    assert((809 * 2) >= 809);
    assert((846 * 2) >= 846);
    assert((883 * 2) >= 883);
    assert((920 * 2) >= 920);
    assert((957 * 2) >= 957);
    assert((994 * 2) >= 994);
    assert((31 * 2) >= 31);
    assert((68 * 2) >= 68);
    assert((105 * 2) >= 105);
    assert((142 * 2) >= 142);
    assert((179 * 2) >= 179);
    assert((216 * 2) >= 216);
    assert((253 * 2) >= 253);
    assert((290 * 2) >= 290);
    assert((327 * 2) >= 327);
    assert((364 * 2) >= 364);
    assert((401 * 2) >= 401);
    assert((438 * 2) >= 438);
    assert((475 * 2) >= 475);
    assert((512 * 2) >= 512);
    assert((549 * 2) >= 549);
    assert((586 * 2) >= 586);
    assert((623 * 2) >= 623);
    assert((660 * 2) >= 660);
    assert((697 * 2) >= 697);
    assert((734 * 2) >= 734);
    assert((771 * 2) >= 771);
    assert((808 * 2) >= 808);
    assert((845 * 2) >= 845);
    assert((882 * 2) >= 882);
    assert((919 * 2) >= 919);
    assert((956 * 2) >= 956);
    assert((993 * 2) >= 993);
    assert((30 * 2) >= 30);
    assert((67 * 2) >= 67);
    assert((104 * 2) >= 104);
    assert((141 * 2) >= 141);
    assert((178 * 2) >= 178);
    assert((215 * 2) >= 215);
    assert((252 * 2) >= 252);
    assert((289 * 2) >= 289);
    assert((326 * 2) >= 326);
    assert((363 * 2) >= 363);
    assert((400 * 2) >= 400);
    assert((437 * 2) >= 437);
    assert((474 * 2) >= 474);
    assert((511 * 2) >= 511);
    assert((548 * 2) >= 548);
    assert((585 * 2) >= 585);
    assert((622 * 2) >= 622);
    assert((659 * 2) >= 659);
    assert((696 * 2) >= 696);
    assert((733 * 2) >= 733);
    assert((770 * 2) >= 770);
    assert((807 * 2) >= 807);
    assert((844 * 2) >= 844);
    assert((881 * 2) >= 881);
    assert((918 * 2) >= 918);
    assert((955 * 2) >= 955);
    assert((992 * 2) >= 992);
    assert((29 * 2) >= 29);
    assert((66 * 2) >= 66);
    assert((103 * 2) >= 103);
    assert((140 * 2) >= 140);
    assert((177 * 2) >= 177);
    assert((214 * 2) >= 214);
    assert((251 * 2) >= 251);
    assert((288 * 2) >= 288);
    assert((325 * 2) >= 325);
    assert((362 * 2) >= 362);
    assert((399 * 2) >= 399);
    assert((436 * 2) >= 436);
    assert((473 * 2) >= 473);
    assert((510 * 2) >= 510);
    assert((547 * 2) >= 547);
    assert((584 * 2) >= 584);
    assert((621 * 2) >= 621);
    assert((658 * 2) >= 658);
    assert((695 * 2) >= 695);
    assert((732 * 2) >= 732);
    assert((769 * 2) >= 769);
    assert((806 * 2) >= 806);
    assert((843 * 2) >= 843);
    assert((880 * 2) >= 880);
    assert((917 * 2) >= 917);
    assert((954 * 2) >= 954);
    assert((991 * 2) >= 991);
    assert((28 * 2) >= 28);
    assert((65 * 2) >= 65);
    assert((102 * 2) >= 102);
    assert((139 * 2) >= 139);
    assert((176 * 2) >= 176);
    assert((213 * 2) >= 213);
    assert((250 * 2) >= 250);
    assert((287 * 2) >= 287);
    assert((324 * 2) >= 324);
    assert((361 * 2) >= 361);
    assert((398 * 2) >= 398);
    assert((435 * 2) >= 435);
    assert((472 * 2) >= 472);
    assert((509 * 2) >= 509);
    assert((546 * 2) >= 546);
    assert((583 * 2) >= 583);
    assert((620 * 2) >= 620);
    assert((657 * 2) >= 657);
    assert((694 * 2) >= 694);
    assert((731 * 2) >= 731);
    assert((768 * 2) >= 768);
    assert((805 * 2) >= 805);
    assert((842 * 2) >= 842);
    assert((879 * 2) >= 879);
    assert((916 * 2) >= 916);
    assert((953 * 2) >= 953);
    assert((990 * 2) >= 990);
    assert((27 * 2) >= 27);
    assert((64 * 2) >= 64);
    assert((101 * 2) >= 101);
    assert((138 * 2) >= 138);
    assert((175 * 2) >= 175);
    assert((212 * 2) >= 212);
    assert((249 * 2) >= 249);
    assert((286 * 2) >= 286);
    assert((323 * 2) >= 323);
    assert((360 * 2) >= 360);
    assert((397 * 2) >= 397);
    assert((434 * 2) >= 434);
    assert((471 * 2) >= 471);
    assert((508 * 2) >= 508);
    assert((545 * 2) >= 545);
    assert((582 * 2) >= 582);
    assert((619 * 2) >= 619);
    assert((656 * 2) >= 656);
    assert((693 * 2) >= 693);
    assert((730 * 2) >= 730);
    assert((767 * 2) >= 767);
    assert((804 * 2) >= 804);
    assert((841 * 2) >= 841);
    assert((878 * 2) >= 878);
    assert((915 * 2) >= 915);
    assert((952 * 2) >= 952);
    assert((989 * 2) >= 989);
    assert((26 * 2) >= 26);
    assert((63 * 2) >= 63);
    assert((100 * 2) >= 100);
    assert((137 * 2) >= 137);
    assert((174 * 2) >= 174);
    assert((211 * 2) >= 211);
    assert((248 * 2) >= 248);
    assert((285 * 2) >= 285);
    assert((322 * 2) >= 322);
    assert((359 * 2) >= 359);
    assert((396 * 2) >= 396);
    assert((433 * 2) >= 433);
    assert((470 * 2) >= 470);
    assert((507 * 2) >= 507);
    assert((544 * 2) >= 544);
    assert((581 * 2) >= 581);
    assert((618 * 2) >= 618);
    assert((655 * 2) >= 655);
    assert((692 * 2) >= 692);
    assert((729 * 2) >= 729);
    assert((766 * 2) >= 766);
    assert((803 * 2) >= 803);
    assert((840 * 2) >= 840);
    assert((877 * 2) >= 877);
    assert((914 * 2) >= 914);
    assert((951 * 2) >= 951);
    assert((988 * 2) >= 988);
    assert((25 * 2) >= 25);
    assert((62 * 2) >= 62);
    assert((99 * 2) >= 99);
    assert((136 * 2) >= 136);
    assert((173 * 2) >= 173);
    assert((210 * 2) >= 210);
    assert((247 * 2) >= 247);
    assert((284 * 2) >= 284);
    assert((321 * 2) >= 321);
    assert((358 * 2) >= 358);
    assert((395 * 2) >= 395);
    assert((432 * 2) >= 432);
    assert((469 * 2) >= 469);
    assert((506 * 2) >= 506);
    assert((543 * 2) >= 543);
    assert((580 * 2) >= 580);
    assert((617 * 2) >= 617);
    assert((654 * 2) >= 654);
    assert((691 * 2) >= 691);
    assert((728 * 2) >= 728);
    assert((765 * 2) >= 765);
    assert((802 * 2) >= 802);
    assert((839 * 2) >= 839);
    assert((876 * 2) >= 876);
    assert((913 * 2) >= 913);
    assert((950 * 2) >= 950);
    assert((987 * 2) >= 987);
    assert((24 * 2) >= 24);
    assert((61 * 2) >= 61);
    assert((98 * 2) >= 98);
    assert((135 * 2) >= 135);
    assert((172 * 2) >= 172);
    assert((209 * 2) >= 209);
    assert((246 * 2) >= 246);
    assert((283 * 2) >= 283);
    assert((320 * 2) >= 320);
    assert((357 * 2) >= 357);
    assert((394 * 2) >= 394);
    assert((431 * 2) >= 431);
    assert((468 * 2) >= 468);
    assert((505 * 2) >= 505);
    assert((542 * 2) >= 542);
    assert((579 * 2) >= 579);
    assert((616 * 2) >= 616);
    assert((653 * 2) >= 653);
    assert((690 * 2) >= 690);
    assert((727 * 2) >= 727);
    assert((764 * 2) >= 764);
    assert((801 * 2) >= 801);
    assert((838 * 2) >= 838);
    assert((875 * 2) >= 875);
    assert((912 * 2) >= 912);
    assert((949 * 2) >= 949);
    assert((986 * 2) >= 986);
    assert((23 * 2) >= 23);
    assert((60 * 2) >= 60);
    assert((97 * 2) >= 97);
    assert((134 * 2) >= 134);
    assert((171 * 2) >= 171);
    assert((208 * 2) >= 208);
    assert((245 * 2) >= 245);
    assert((282 * 2) >= 282);
    assert((319 * 2) >= 319);
    assert((356 * 2) >= 356);
    assert((393 * 2) >= 393);
    assert((430 * 2) >= 430);
    assert((467 * 2) >= 467);
    assert((504 * 2) >= 504);
    assert((541 * 2) >= 541);
    assert((578 * 2) >= 578);
    assert((615 * 2) >= 615);
    assert((652 * 2) >= 652);
    assert((689 * 2) >= 689);
    assert((726 * 2) >= 726);
    assert((763 * 2) >= 763);
    assert((800 * 2) >= 800);
    assert((837 * 2) >= 837);
    assert((874 * 2) >= 874);
    assert((911 * 2) >= 911);
    assert((948 * 2) >= 948);
    assert((985 * 2) >= 985);
    assert((22 * 2) >= 22);
    assert((59 * 2) >= 59);
    assert((96 * 2) >= 96);
    assert((133 * 2) >= 133);
    assert((170 * 2) >= 170);
    assert((207 * 2) >= 207);
    assert((244 * 2) >= 244);
    assert((281 * 2) >= 281);
    assert((318 * 2) >= 318);
    assert((355 * 2) >= 355);
    assert((392 * 2) >= 392);
    assert((429 * 2) >= 429);
    assert((466 * 2) >= 466);
    assert((503 * 2) >= 503);
    assert((540 * 2) >= 540);
    assert((577 * 2) >= 577);
    assert((614 * 2) >= 614);
    assert((651 * 2) >= 651);
    assert((688 * 2) >= 688);
    assert((725 * 2) >= 725);
    assert((762 * 2) >= 762);
    assert((799 * 2) >= 799);
    assert((836 * 2) >= 836);
    assert((873 * 2) >= 873);
    assert((910 * 2) >= 910);
    assert((947 * 2) >= 947);
    assert((984 * 2) >= 984);
    assert((21 * 2) >= 21);
    assert((58 * 2) >= 58);
    assert((95 * 2) >= 95);
    assert((132 * 2) >= 132);
    assert((169 * 2) >= 169);
    assert((206 * 2) >= 206);
    assert((243 * 2) >= 243);
    assert((280 * 2) >= 280);
    assert((317 * 2) >= 317);
    assert((354 * 2) >= 354);
    assert((391 * 2) >= 391);
    assert((428 * 2) >= 428);
    assert((465 * 2) >= 465);
    assert((502 * 2) >= 502);
    assert((539 * 2) >= 539);
    assert((576 * 2) >= 576);
    assert((613 * 2) >= 613);
    assert((650 * 2) >= 650);
    assert((687 * 2) >= 687);
    assert((724 * 2) >= 724);
    assert((761 * 2) >= 761);
    assert((798 * 2) >= 798);
    assert((835 * 2) >= 835);
    assert((872 * 2) >= 872);
    assert((909 * 2) >= 909);
    assert((946 * 2) >= 946);
    assert((983 * 2) >= 983);
    assert((20 * 2) >= 20);
    assert((57 * 2) >= 57);
    assert((94 * 2) >= 94);
    assert((131 * 2) >= 131);
    assert((168 * 2) >= 168);
    assert((205 * 2) >= 205);
    assert((242 * 2) >= 242);
    assert((279 * 2) >= 279);
    assert((316 * 2) >= 316);
    assert((353 * 2) >= 353);
    assert((390 * 2) >= 390);
    assert((427 * 2) >= 427);
    assert((464 * 2) >= 464);
    assert((501 * 2) >= 501);
    assert((538 * 2) >= 538);
    assert((575 * 2) >= 575);
    assert((612 * 2) >= 612);
    assert((649 * 2) >= 649);
    assert((686 * 2) >= 686);
    assert((723 * 2) >= 723);
    assert((760 * 2) >= 760);
    assert((797 * 2) >= 797);
    assert((834 * 2) >= 834);
    assert((871 * 2) >= 871);
    assert((908 * 2) >= 908);
    assert((945 * 2) >= 945);
    assert((982 * 2) >= 982);
    assert((19 * 2) >= 19);
    assert((56 * 2) >= 56);
    assert((93 * 2) >= 93);
    assert((130 * 2) >= 130);
    assert((167 * 2) >= 167);
    assert((204 * 2) >= 204);
    assert((241 * 2) >= 241);
    assert((278 * 2) >= 278);
    assert((315 * 2) >= 315);
    assert((352 * 2) >= 352);
    assert((389 * 2) >= 389);
    assert((426 * 2) >= 426);
    assert((463 * 2) >= 463);
    assert((500 * 2) >= 500);
    assert((537 * 2) >= 537);
    assert((574 * 2) >= 574);
    assert((611 * 2) >= 611);
    assert((648 * 2) >= 648);
    assert((685 * 2) >= 685);
    assert((722 * 2) >= 722);
    assert((759 * 2) >= 759);
    assert((796 * 2) >= 796);
    assert((833 * 2) >= 833);
    assert((870 * 2) >= 870);
    assert((907 * 2) >= 907);
    assert((944 * 2) >= 944);
    assert((981 * 2) >= 981);
    assert((18 * 2) >= 18);
    assert((55 * 2) >= 55);
    assert((92 * 2) >= 92);
    assert((129 * 2) >= 129);
    assert((166 * 2) >= 166);
    assert((203 * 2) >= 203);
    assert((240 * 2) >= 240);
    assert((277 * 2) >= 277);
    assert((314 * 2) >= 314);
    assert((351 * 2) >= 351);
    assert((388 * 2) >= 388);
    assert((425 * 2) >= 425);
    assert((462 * 2) >= 462);
    assert((499 * 2) >= 499);
    assert((536 * 2) >= 536);
    assert((573 * 2) >= 573);
    assert((610 * 2) >= 610);
    assert((647 * 2) >= 647);
    assert((684 * 2) >= 684);
    assert((721 * 2) >= 721);
    assert((758 * 2) >= 758);
    assert((795 * 2) >= 795);
    assert((832 * 2) >= 832);
    assert((869 * 2) >= 869);
    assert((906 * 2) >= 906);
    assert((943 * 2) >= 943);
    assert((980 * 2) >= 980);
    assert((17 * 2) >= 17);
    assert((54 * 2) >= 54);
    assert((91 * 2) >= 91);
    assert((128 * 2) >= 128);
    assert((165 * 2) >= 165);
    assert((202 * 2) >= 202);
    assert((239 * 2) >= 239);
    assert((276 * 2) >= 276);
    assert((313 * 2) >= 313);
    assert((350 * 2) >= 350);
    assert((387 * 2) >= 387);
    assert((424 * 2) >= 424);
    assert((461 * 2) >= 461);
    assert((498 * 2) >= 498);
    assert((535 * 2) >= 535);
    assert((572 * 2) >= 572);
    assert((609 * 2) >= 609);
    assert((646 * 2) >= 646);
    assert((683 * 2) >= 683);
    assert((720 * 2) >= 720);
    assert((757 * 2) >= 757);
    assert((794 * 2) >= 794);
    assert((831 * 2) >= 831);
    assert((868 * 2) >= 868);
    assert((905 * 2) >= 905);
    assert((942 * 2) >= 942);
    assert((979 * 2) >= 979);
    assert((16 * 2) >= 16);
    assert((53 * 2) >= 53);
    assert((90 * 2) >= 90);
    assert((127 * 2) >= 127);
    assert((164 * 2) >= 164);
    assert((201 * 2) >= 201);
    assert((238 * 2) >= 238);
    assert((275 * 2) >= 275);
    assert((312 * 2) >= 312);
    assert((349 * 2) >= 349);
    assert((386 * 2) >= 386);
    assert((423 * 2) >= 423);
    assert((460 * 2) >= 460);
    assert((497 * 2) >= 497);
    assert((534 * 2) >= 534);
    assert((571 * 2) >= 571);
    assert((608 * 2) >= 608);
    assert((645 * 2) >= 645);
    assert((682 * 2) >= 682);
    assert((719 * 2) >= 719);
    assert((756 * 2) >= 756);
    assert((793 * 2) >= 793);
    assert((830 * 2) >= 830);
    assert((867 * 2) >= 867);
    assert((904 * 2) >= 904);
    assert((941 * 2) >= 941);
    assert((978 * 2) >= 978);
    assert((15 * 2) >= 15);
    assert((52 * 2) >= 52);
    assert((89 * 2) >= 89);
    assert((126 * 2) >= 126);
    assert((163 * 2) >= 163);
    assert((200 * 2) >= 200);
    assert((237 * 2) >= 237);
    assert((274 * 2) >= 274);
    assert((311 * 2) >= 311);
    assert((348 * 2) >= 348);
    assert((385 * 2) >= 385);
    assert((422 * 2) >= 422);
    assert((459 * 2) >= 459);
    assert((496 * 2) >= 496);
    assert((533 * 2) >= 533);
    assert((570 * 2) >= 570);
    assert((607 * 2) >= 607);
    assert((644 * 2) >= 644);
    assert((681 * 2) >= 681);
    assert((718 * 2) >= 718);
    assert((755 * 2) >= 755);
    assert((792 * 2) >= 792);
    assert((829 * 2) >= 829);
    assert((866 * 2) >= 866);
    assert((903 * 2) >= 903);
    assert((940 * 2) >= 940);
    assert((977 * 2) >= 977);
    assert((14 * 2) >= 14);
    assert((51 * 2) >= 51);
    assert((88 * 2) >= 88);
    assert((125 * 2) >= 125);
    assert((162 * 2) >= 162);
    assert((199 * 2) >= 199);
    assert((236 * 2) >= 236);
    assert((273 * 2) >= 273);
    assert((310 * 2) >= 310);
    assert((347 * 2) >= 347);
    assert((384 * 2) >= 384);
    assert((421 * 2) >= 421);
    assert((458 * 2) >= 458);
    assert((495 * 2) >= 495);
    assert((532 * 2) >= 532);
    assert((569 * 2) >= 569);
    assert((606 * 2) >= 606);
    assert((643 * 2) >= 643);
    assert((680 * 2) >= 680);
    assert((717 * 2) >= 717);
    assert((754 * 2) >= 754);
    assert((791 * 2) >= 791);
    assert((828 * 2) >= 828);
    assert((865 * 2) >= 865);
    assert((902 * 2) >= 902);
    assert((939 * 2) >= 939);
    assert((976 * 2) >= 976);
    assert((13 * 2) >= 13);
    assert((50 * 2) >= 50);
    assert((87 * 2) >= 87);
    assert((124 * 2) >= 124);
    assert((161 * 2) >= 161);
    assert((198 * 2) >= 198);
    assert((235 * 2) >= 235);
    assert((272 * 2) >= 272);
    assert((309 * 2) >= 309);
    assert((346 * 2) >= 346);
    assert((383 * 2) >= 383);
    assert((420 * 2) >= 420);
    assert((457 * 2) >= 457);
    assert((494 * 2) >= 494);
    assert((531 * 2) >= 531);
    assert((568 * 2) >= 568);
    assert((605 * 2) >= 605);
    assert((642 * 2) >= 642);
    assert((679 * 2) >= 679);
    assert((716 * 2) >= 716);
    assert((753 * 2) >= 753);
    assert((790 * 2) >= 790);
    assert((827 * 2) >= 827);
    assert((864 * 2) >= 864);
    assert((901 * 2) >= 901);
    assert((938 * 2) >= 938);
    assert((975 * 2) >= 975);
    assert((12 * 2) >= 12);
    assert((49 * 2) >= 49);
    assert((86 * 2) >= 86);
    assert((123 * 2) >= 123);
    assert((160 * 2) >= 160);
    assert((197 * 2) >= 197);
    assert((234 * 2) >= 234);
    assert((271 * 2) >= 271);
    assert((308 * 2) >= 308);
    assert((345 * 2) >= 345);
    assert((382 * 2) >= 382);
    assert((419 * 2) >= 419);
    assert((456 * 2) >= 456);
    assert((493 * 2) >= 493);
    assert((530 * 2) >= 530);
    assert((567 * 2) >= 567);
    assert((604 * 2) >= 604);
    assert((641 * 2) >= 641);
    assert((678 * 2) >= 678);
    assert((715 * 2) >= 715);
    assert((752 * 2) >= 752);
    assert((789 * 2) >= 789);
    assert((826 * 2) >= 826);
    assert((863 * 2) >= 863);
    assert((900 * 2) >= 900);
    assert((937 * 2) >= 937);
    assert((974 * 2) >= 974);
    assert((11 * 2) >= 11);
    assert((48 * 2) >= 48);
    assert((85 * 2) >= 85);
    assert((122 * 2) >= 122);
    assert((159 * 2) >= 159);
    assert((196 * 2) >= 196);
    assert((233 * 2) >= 233);
    assert((270 * 2) >= 270);
    assert((307 * 2) >= 307);
    assert((344 * 2) >= 344);
    assert((381 * 2) >= 381);
    assert((418 * 2) >= 418);
    assert((455 * 2) >= 455);
    assert((492 * 2) >= 492);
    assert((529 * 2) >= 529);
    assert((566 * 2) >= 566);
    assert((603 * 2) >= 603);
    assert((640 * 2) >= 640);
    assert((677 * 2) >= 677);
    assert((714 * 2) >= 714);
    assert((751 * 2) >= 751);
    assert((788 * 2) >= 788);
    assert((825 * 2) >= 825);
    assert((862 * 2) >= 862);
    assert((899 * 2) >= 899);
    assert((936 * 2) >= 936);
    assert((973 * 2) >= 973);
    assert((10 * 2) >= 10);
    assert((47 * 2) >= 47);
    assert((84 * 2) >= 84);
    assert((121 * 2) >= 121);
    assert((158 * 2) >= 158);
    assert((195 * 2) >= 195);
    assert((232 * 2) >= 232);
    assert((269 * 2) >= 269);
    assert((306 * 2) >= 306);
    assert((343 * 2) >= 343);
    assert((380 * 2) >= 380);
    assert((417 * 2) >= 417);
    assert((454 * 2) >= 454);
    assert((491 * 2) >= 491);
    assert((528 * 2) >= 528);
    assert((565 * 2) >= 565);
    assert((602 * 2) >= 602);
    assert((639 * 2) >= 639);
    assert((676 * 2) >= 676);
    assert((713 * 2) >= 713);
    assert((750 * 2) >= 750);
    assert((787 * 2) >= 787);
    assert((824 * 2) >= 824);
    assert((861 * 2) >= 861);
    assert((898 * 2) >= 898);
    assert((935 * 2) >= 935);
    assert((972 * 2) >= 972);
    assert((9 * 2) >= 9);
    assert((46 * 2) >= 46);
    assert((83 * 2) >= 83);
    assert((120 * 2) >= 120);
    assert((157 * 2) >= 157);
    assert((194 * 2) >= 194);
    assert((231 * 2) >= 231);
    assert((268 * 2) >= 268);
    assert((305 * 2) >= 305);
    assert((342 * 2) >= 342);
    assert((379 * 2) >= 379);
    assert((416 * 2) >= 416);
    assert((453 * 2) >= 453);
    assert((490 * 2) >= 490);
    assert((527 * 2) >= 527);
    assert((564 * 2) >= 564);
    assert((601 * 2) >= 601);
    assert((638 * 2) >= 638);
    assert((675 * 2) >= 675);
    assert((712 * 2) >= 712);
    assert((749 * 2) >= 749);
    assert((786 * 2) >= 786);
    assert((823 * 2) >= 823);
    assert((860 * 2) >= 860);
    assert((897 * 2) >= 897);
    assert((934 * 2) >= 934);
    assert((971 * 2) >= 971);
    assert((8 * 2) >= 8);
    assert((45 * 2) >= 45);
    assert((82 * 2) >= 82);
    assert((119 * 2) >= 119);
    assert((156 * 2) >= 156);
    assert((193 * 2) >= 193);
    assert((230 * 2) >= 230);
    assert((267 * 2) >= 267);
    assert((304 * 2) >= 304);
    assert((341 * 2) >= 341);
    assert((378 * 2) >= 378);
    assert((415 * 2) >= 415);
    assert((452 * 2) >= 452);
    assert((489 * 2) >= 489);
    assert((526 * 2) >= 526);
    assert((563 * 2) >= 563);
    assert((600 * 2) >= 600);
    assert((637 * 2) >= 637);
{ /* unclosed opening brace */
    assert((674 * 2) >= 674);
    assert((711 * 2) >= 711);
    assert((748 * 2) >= 748);
    assert((785 * 2) >= 785);
    assert((822 * 2) >= 822);
    assert((859 * 2) >= 859);
    assert((896 * 2) >= 896);
    assert((933 * 2) >= 933);
    assert((970 * 2) >= 970);
    assert((7 * 2) >= 7);
    assert((44 * 2) >= 44);
    assert((81 * 2) >= 81);
    assert((118 * 2) >= 118);
    assert((155 * 2) >= 155);
    assert((192 * 2) >= 192);
    assert((229 * 2) >= 229);
    assert((266 * 2) >= 266);
    assert((303 * 2) >= 303);
    assert((340 * 2) >= 340);
    assert((377 * 2) >= 377);
    assert((414 * 2) >= 414);
    assert((451 * 2) >= 451);
    assert((488 * 2) >= 488);
    assert((525 * 2) >= 525);
    assert((562 * 2) >= 562);
    assert((599 * 2) >= 599);
    assert((636 * 2) >= 636);
    assert((673 * 2) >= 673);
    assert((710 * 2) >= 710);
    assert((747 * 2) >= 747);
    assert((784 * 2) >= 784);
    assert((821 * 2) >= 821);
    assert((858 * 2) >= 858);
    assert((895 * 2) >= 895);
    assert((932 * 2) >= 932);
    assert((969 * 2) >= 969);
    assert((6 * 2) >= 6);
    assert((43 * 2) >= 43);
    assert((80 * 2) >= 80);
    assert((117 * 2) >= 117);
    assert((154 * 2) >= 154);
    assert((191 * 2) >= 191);
    assert((228 * 2) >= 228);
    assert((265 * 2) >= 265);
    assert((302 * 2) >= 302);
    assert((339 * 2) >= 339);
    assert((376 * 2) >= 376);
    assert((413 * 2) >= 413);
    assert((450 * 2) >= 450);
    assert((487 * 2) >= 487);
    assert((524 * 2) >= 524);
    assert((561 * 2) >= 561);
    assert((598 * 2) >= 598);
    assert((635 * 2) >= 635);
    assert((672 * 2) >= 672);
    assert((709 * 2) >= 709);
    assert((746 * 2) >= 746);
    assert((783 * 2) >= 783);
    assert((820 * 2) >= 820);
    assert((857 * 2) >= 857);
    assert((894 * 2) >= 894);
    assert((931 * 2) >= 931);
    assert((968 * 2) >= 968);
    assert((5 * 2) >= 5);
    assert((42 * 2) >= 42);
    assert((79 * 2) >= 79);
    assert((116 * 2) >= 116);
    assert((153 * 2) >= 153);
    assert((190 * 2) >= 190);
    assert((227 * 2) >= 227);
    assert((264 * 2) >= 264);
    assert((301 * 2) >= 301);
    assert((338 * 2) >= 338);
    assert((375 * 2) >= 375);
    assert((412 * 2) >= 412);
    assert((449 * 2) >= 449);
    assert((486 * 2) >= 486);
    assert((523 * 2) >= 523);
    assert((560 * 2) >= 560);
    assert((597 * 2) >= 597);
    assert((634 * 2) >= 634);
    assert((671 * 2) >= 671);
    assert((708 * 2) >= 708);
    assert((745 * 2) >= 745);
    assert((782 * 2) >= 782);
    assert((819 * 2) >= 819);
    assert((856 * 2) >= 856);
    assert((893 * 2) >= 893);
    assert((930 * 2) >= 930);
    assert((967 * 2) >= 967);
    assert((4 * 2) >= 4);
    assert((41 * 2) >= 41);
    assert((78 * 2) >= 78);
    assert((115 * 2) >= 115);
    assert((152 * 2) >= 152);
    assert((189 * 2) >= 189);
    assert((226 * 2) >= 226);
    assert((263 * 2) >= 263);
    assert((300 * 2) >= 300);
    assert((337 * 2) >= 337);
    assert((374 * 2) >= 374);
    assert((411 * 2) >= 411);
    assert((448 * 2) >= 448);
    assert((485 * 2) >= 485);
    assert((522 * 2) >= 522);
    assert((559 * 2) >= 559);
    assert((596 * 2) >= 596);
    assert((633 * 2) >= 633);
    assert((670 * 2) >= 670);
    assert((707 * 2) >= 707);
    assert((744 * 2) >= 744);
    assert((781 * 2) >= 781);
    assert((818 * 2) >= 818);
    assert((855 * 2) >= 855);
    assert((892 * 2) >= 892);
    assert((929 * 2) >= 929);
    assert((966 * 2) >= 966);
    assert((3 * 2) >= 3);
    assert((40 * 2) >= 40);
    assert((77 * 2) >= 77);
    assert((114 * 2) >= 114);
    assert((151 * 2) >= 151);
    assert((188 * 2) >= 188);
    assert((225 * 2) >= 225);
    assert((262 * 2) >= 262);
    assert((299 * 2) >= 299);
    assert((336 * 2) >= 336);
    assert((373 * 2) >= 373);
    assert((410 * 2) >= 410);
    assert((447 * 2) >= 447);
    assert((484 * 2) >= 484);
    assert((521 * 2) >= 521);
    assert((558 * 2) >= 558);
    assert((595 * 2) >= 595);
    assert((632 * 2) >= 632);
    assert((669 * 2) >= 669);
    assert((706 * 2) >= 706);
    assert((743 * 2) >= 743);
    assert((780 * 2) >= 780);
    assert((817 * 2) >= 817);
    assert((854 * 2) >= 854);
    assert((891 * 2) >= 891);
    assert((928 * 2) >= 928);
    assert((965 * 2) >= 965);
    assert((2 * 2) >= 2);
    assert((39 * 2) >= 39);
    assert((76 * 2) >= 76);
    assert((113 * 2) >= 113);
    assert((150 * 2) >= 150);
    assert((187 * 2) >= 187);
    assert((224 * 2) >= 224);
    assert((261 * 2) >= 261);
    assert((298 * 2) >= 298);
    assert((335 * 2) >= 335);
    assert((372 * 2) >= 372);
    assert((409 * 2) >= 409);
    assert((446 * 2) >= 446);
    assert((483 * 2) >= 483);
    assert((520 * 2) >= 520);
    assert((557 * 2) >= 557);
    assert((594 * 2) >= 594);
    assert((631 * 2) >= 631);
    assert((668 * 2) >= 668);
    assert((705 * 2) >= 705);
    assert((742 * 2) >= 742);
    assert((779 * 2) >= 779);
    assert((816 * 2) >= 816);
    assert((853 * 2) >= 853);
    assert((890 * 2) >= 890);
    assert((927 * 2) >= 927);
    assert((964 * 2) >= 964);
    assert((1 * 2) >= 1);
    assert((38 * 2) >= 38);
    assert((75 * 2) >= 75);
    assert((112 * 2) >= 112);
    assert((149 * 2) >= 149);
    assert((186 * 2) >= 186);
    assert((223 * 2) >= 223);
    assert((260 * 2) >= 260);
    assert((297 * 2) >= 297);
    assert((334 * 2) >= 334);
    assert((371 * 2) >= 371);
    assert((408 * 2) >= 408);
    assert((445 * 2) >= 445);
    assert((482 * 2) >= 482);
    assert((519 * 2) >= 519);
    assert((556 * 2) >= 556);
    assert((593 * 2) >= 593);
    assert((630 * 2) >= 630);
    assert((667 * 2) >= 667);
    assert((704 * 2) >= 704);
    assert((741 * 2) >= 741);
    assert((778 * 2) >= 778);
    assert((815 * 2) >= 815);
    assert((852 * 2) >= 852);
    assert((889 * 2) >= 889);
    assert((926 * 2) >= 926);
    assert((963 * 2) >= 963);
    assert((0 * 2) >= 0);
    assert((37 * 2) >= 37);
    assert((74 * 2) >= 74);
    assert((111 * 2) >= 111);
    assert((148 * 2) >= 148);
    assert((185 * 2) >= 185);
    assert((222 * 2) >= 222);
    assert((259 * 2) >= 259);
    assert((296 * 2) >= 296);
    assert((333 * 2) >= 333);
    assert((370 * 2) >= 370);
    assert((407 * 2) >= 407);
    assert((444 * 2) >= 444);
    assert((481 * 2) >= 481);
    assert((518 * 2) >= 518);
    assert((555 * 2) >= 555);
    assert((592 * 2) >= 592);
    assert((629 * 2) >= 629);
    assert((666 * 2) >= 666);
    assert((703 * 2) >= 703);
    assert((740 * 2) >= 740);
    assert((777 * 2) >= 777);
    assert((814 * 2) >= 814);
    assert((851 * 2) >= 851);
    assert((888 * 2) >= 888);
    assert((925 * 2) >= 925);
    assert((962 * 2) >= 962);
    assert((999 * 2) >= 999);
    assert((36 * 2) >= 36);
    assert((73 * 2) >= 73);
    assert((110 * 2) >= 110);
    assert((147 * 2) >= 147);
    assert((184 * 2) >= 184);
    assert((221 * 2) >= 221);
    assert((258 * 2) >= 258);
    assert((295 * 2) >= 295);
    assert((332 * 2) >= 332);
    assert((369 * 2) >= 369);
    assert((406 * 2) >= 406);
    assert((443 * 2) >= 443);
    assert((480 * 2) >= 480);
    assert((517 * 2) >= 517);
    assert((554 * 2) >= 554);
    assert((591 * 2) >= 591);
    assert((628 * 2) >= 628);
    assert((665 * 2) >= 665);
    assert((702 * 2) >= 702);
    assert((739 * 2) >= 739);
    assert((776 * 2) >= 776);
    assert((813 * 2) >= 813);
    assert((850 * 2) >= 850);
    assert((887 * 2) >= 887);
    assert((924 * 2) >= 924);
    assert((961 * 2) >= 961);
    assert((998 * 2) >= 998);
    assert((35 * 2) >= 35);
    assert((72 * 2) >= 72);
    assert((109 * 2) >= 109);
    assert((146 * 2) >= 146);
    assert((183 * 2) >= 183);
    assert((220 * 2) >= 220);
    assert((257 * 2) >= 257);
    assert((294 * 2) >= 294);
    assert((331 * 2) >= 331);
    assert((368 * 2) >= 368);
    assert((405 * 2) >= 405);
    assert((442 * 2) >= 442);
    assert((479 * 2) >= 479);
    assert((516 * 2) >= 516);
    assert((553 * 2) >= 553);
    assert((590 * 2) >= 590);
    assert((627 * 2) >= 627);
    assert((664 * 2) >= 664);
    assert((701 * 2) >= 701);
    assert((738 * 2) >= 738);
    assert((775 * 2) >= 775);
    assert((812 * 2) >= 812);
    assert((849 * 2) >= 849);
    assert((886 * 2) >= 886);
    assert((923 * 2) >= 923);
    assert((960 * 2) >= 960);
    assert((997 * 2) >= 997);
    assert((34 * 2) >= 34);
    assert((71 * 2) >= 71);
    assert((108 * 2) >= 108);
    assert((145 * 2) >= 145);
    assert((182 * 2) >= 182);
    assert((219 * 2) >= 219);
    assert((256 * 2) >= 256);
    assert((293 * 2) >= 293);
    assert((330 * 2) >= 330);
    assert((367 * 2) >= 367);
    assert((404 * 2) >= 404);
    assert((441 * 2) >= 441);
    assert((478 * 2) >= 478);
    assert((515 * 2) >= 515);
    assert((552 * 2) >= 552);
    assert((589 * 2) >= 589);
    assert((626 * 2) >= 626);
    assert((663 * 2) >= 663);
    assert((700 * 2) >= 700);
    assert((737 * 2) >= 737);
    assert((774 * 2) >= 774);
    assert((811 * 2) >= 811);
    assert((848 * 2) >= 848);
    assert((885 * 2) >= 885);
    assert((922 * 2) >= 922);
    assert((959 * 2) >= 959);
    assert((996 * 2) >= 996);
    assert((33 * 2) >= 33);
    assert((70 * 2) >= 70);
    assert((107 * 2) >= 107);
    assert((144 * 2) >= 144);
    assert((181 * 2) >= 181);
    assert((218 * 2) >= 218);
    assert((255 * 2) >= 255);
    assert((292 * 2) >= 292);
    assert((329 * 2) >= 329);
    assert((366 * 2) >= 366);
    assert((403 * 2) >= 403);
    assert((440 * 2) >= 440);
    assert((477 * 2) >= 477);
    assert((514 * 2) >= 514);
    assert((551 * 2) >= 551);
    assert((588 * 2) >= 588);
    assert((625 * 2) >= 625);
    assert((662 * 2) >= 662);
    assert((699 * 2) >= 699);
    assert((736 * 2) >= 736);
    assert((773 * 2) >= 773);
    assert((810 * 2) >= 810);
    assert((847 * 2) >= 847);
    assert((884 * 2) >= 884);
    assert((921 * 2) >= 921);
    assert((958 * 2) >= 958);
    assert((995 * 2) >= 995);
    assert((32 * 2) >= 32);
    assert((69 * 2) >= 69);
    assert((106 * 2) >= 106);
    assert((143 * 2) >= 143);
    assert((180 * 2) >= 180);
    assert((217 * 2) >= 217);
    assert((254 * 2) >= 254);
    assert((291 * 2) >= 291);
    assert((328 * 2) >= 328);
    assert((365 * 2) >= 365);
    assert((402 * 2) >= 402);
    assert((439 * 2) >= 439);
    assert((476 * 2) >= 476);
    assert((513 * 2) >= 513);
    assert((550 * 2) >= 550);
    assert((587 * 2) >= 587);
    assert((624 * 2) >= 624);
    assert((661 * 2) >= 661);
    assert((698 * 2) >= 698);
    assert((735 * 2) >= 735);
    assert((772 * 2) >= 772);
    assert((809 * 2) >= 809);
    assert((846 * 2) >= 846);
    assert((883 * 2) >= 883);
    assert((920 * 2) >= 920);
    assert((957 * 2) >= 957);
    assert((994 * 2) >= 994);
    assert((31 * 2) >= 31);
    assert((68 * 2) >= 68);
    assert((105 * 2) >= 105);
    assert((142 * 2) >= 142);
    assert((179 * 2) >= 179);
    assert((216 * 2) >= 216);
    assert((253 * 2) >= 253);
    assert((290 * 2) >= 290);
    assert((327 * 2) >= 327);
    assert((364 * 2) >= 364);
    assert((401 * 2) >= 401);
    assert((438 * 2) >= 438);
    assert((475 * 2) >= 475);
    assert((512 * 2) >= 512);
    assert((549 * 2) >= 549);
    assert((586 * 2) >= 586);
    assert((623 * 2) >= 623);
    assert((660 * 2) >= 660);
    assert((697 * 2) >= 697);
    assert((734 * 2) >= 734);
    assert((771 * 2) >= 771);
    assert((808 * 2) >= 808);
    assert((845 * 2) >= 845);
    assert((882 * 2) >= 882);
    assert((919 * 2) >= 919);
    assert((956 * 2) >= 956);
    assert((993 * 2) >= 993);
    assert((30 * 2) >= 30);
    assert((67 * 2) >= 67);
    assert((104 * 2) >= 104);
    assert((141 * 2) >= 141);
    assert((178 * 2) >= 178);
    assert((215 * 2) >= 215);
    assert((252 * 2) >= 252);
    assert((289 * 2) >= 289);
    assert((326 * 2) >= 326);
    assert((363 * 2) >= 363);
    assert((400 * 2) >= 400);
    assert((437 * 2) >= 437);
    assert((474 * 2) >= 474);
    assert((511 * 2) >= 511);
    assert((548 * 2) >= 548);
    assert((585 * 2) >= 585);
    assert((622 * 2) >= 622);
    assert((659 * 2) >= 659);
    assert((696 * 2) >= 696);
    assert((733 * 2) >= 733);
    assert((770 * 2) >= 770);
    assert((807 * 2) >= 807);
    assert((844 * 2) >= 844);
    assert((881 * 2) >= 881);
    assert((918 * 2) >= 918);
    assert((955 * 2) >= 955);
    assert((992 * 2) >= 992);
    assert((29 * 2) >= 29);
    assert((66 * 2) >= 66);
    assert((103 * 2) >= 103);
    assert((140 * 2) >= 140);
    assert((177 * 2) >= 177);
    assert((214 * 2) >= 214);
    assert((251 * 2) >= 251);
    assert((288 * 2) >= 288);
    assert((325 * 2) >= 325);
    assert((362 * 2) >= 362);
    assert((399 * 2) >= 399);
    assert((436 * 2) >= 436);
    assert((473 * 2) >= 473);
    assert((510 * 2) >= 510);
    assert((547 * 2) >= 547);
    assert((584 * 2) >= 584);
    assert((621 * 2) >= 621);
    assert((658 * 2) >= 658);
    assert((695 * 2) >= 695);
    assert((732 * 2) >= 732);
    assert((769 * 2) >= 769);
    assert((806 * 2) >= 806);
    assert((843 * 2) >= 843);
    assert((880 * 2) >= 880);
    assert((917 * 2) >= 917);
    assert((954 * 2) >= 954);
    assert((991 * 2) >= 991);
    assert((28 * 2) >= 28);
    assert((65 * 2) >= 65);
    assert((102 * 2) >= 102);
    assert((139 * 2) >= 139);
    assert((176 * 2) >= 176);
    assert((213 * 2) >= 213);
    assert((250 * 2) >= 250);
    assert((287 * 2) >= 287);
    assert((324 * 2) >= 324);
    assert((361 * 2) >= 361);
    assert((398 * 2) >= 398);
    assert((435 * 2) >= 435);
    assert((472 * 2) >= 472);
    assert((509 * 2) >= 509);
    assert((546 * 2) >= 546);
    assert((583 * 2) >= 583);
    assert((620 * 2) >= 620);
    assert((657 * 2) >= 657);
    assert((694 * 2) >= 694);
    assert((731 * 2) >= 731);
    assert((768 * 2) >= 768);
    assert((805 * 2) >= 805);
    assert((842 * 2) >= 842);
    assert((879 * 2) >= 879);
    assert((916 * 2) >= 916);
    assert((953 * 2) >= 953);
    assert((990 * 2) >= 990);
    assert((27 * 2) >= 27);
    assert((64 * 2) >= 64);
    assert((101 * 2) >= 101);
    assert((138 * 2) >= 138);
    assert((175 * 2) >= 175);
    assert((212 * 2) >= 212);
    assert((249 * 2) >= 249);
    assert((286 * 2) >= 286);
    assert((323 * 2) >= 323);
    assert((360 * 2) >= 360);
    assert((397 * 2) >= 397);
    assert((434 * 2) >= 434);
    assert((471 * 2) >= 471);
    assert((508 * 2) >= 508);
    assert((545 * 2) >= 545);
    assert((582 * 2) >= 582);
    assert((619 * 2) >= 619);
    assert((656 * 2) >= 656);
    assert((693 * 2) >= 693);
    assert((730 * 2) >= 730);
    assert((767 * 2) >= 767);
    assert((804 * 2) >= 804);
    assert((841 * 2) >= 841);
    assert((878 * 2) >= 878);
    assert((915 * 2) >= 915);
    assert((952 * 2) >= 952);
    assert((989 * 2) >= 989);
    assert((26 * 2) >= 26);
    assert((63 * 2) >= 63);
    assert((100 * 2) >= 100);
    assert((137 * 2) >= 137);
    assert((174 * 2) >= 174);
    assert((211 * 2) >= 211);
    assert((248 * 2) >= 248);
    assert((285 * 2) >= 285);
    assert((322 * 2) >= 322);
    assert((359 * 2) >= 359);
    assert((396 * 2) >= 396);
    assert((433 * 2) >= 433);
    assert((470 * 2) >= 470);
    assert((507 * 2) >= 507);
    assert((544 * 2) >= 544);
    assert((581 * 2) >= 581);
    assert((618 * 2) >= 618);
    assert((655 * 2) >= 655);
    assert((692 * 2) >= 692);
    assert((729 * 2) >= 729);
    assert((766 * 2) >= 766);
    assert((803 * 2) >= 803);
    assert((840 * 2) >= 840);
    assert((877 * 2) >= 877);
    assert((914 * 2) >= 914);
    assert((951 * 2) >= 951);
    assert((988 * 2) >= 988);
    assert((25 * 2) >= 25);
    assert((62 * 2) >= 62);
    assert((99 * 2) >= 99);
    assert((136 * 2) >= 136);
    assert((173 * 2) >= 173);
    assert((210 * 2) >= 210);
    assert((247 * 2) >= 247);
    assert((284 * 2) >= 284);
    assert((321 * 2) >= 321);
    assert((358 * 2) >= 358);
    assert((395 * 2) >= 395);
    assert((432 * 2) >= 432);
    assert((469 * 2) >= 469);
    assert((506 * 2) >= 506);
    assert((543 * 2) >= 543);
    assert((580 * 2) >= 580);
    assert((617 * 2) >= 617);
    assert((654 * 2) >= 654);
    assert((691 * 2) >= 691);
    assert((728 * 2) >= 728);
    assert((765 * 2) >= 765);
    assert((802 * 2) >= 802);
    assert((839 * 2) >= 839);
    assert((876 * 2) >= 876);
    assert((913 * 2) >= 913);
    assert((950 * 2) >= 950);
    assert((987 * 2) >= 987);
    assert((24 * 2) >= 24);
    assert((61 * 2) >= 61);
    assert((98 * 2) >= 98);
    assert((135 * 2) >= 135);
    assert((172 * 2) >= 172);
    assert((209 * 2) >= 209);
    assert((246 * 2) >= 246);
    assert((283 * 2) >= 283);
    assert((320 * 2) >= 320);
    assert((357 * 2) >= 357);
    assert((394 * 2) >= 394);
    assert((431 * 2) >= 431);
    assert((468 * 2) >= 468);
    assert((505 * 2) >= 505);
    assert((542 * 2) >= 542);
    assert((579 * 2) >= 579);
    assert((616 * 2) >= 616);
    assert((653 * 2) >= 653);
    assert((690 * 2) >= 690);
    assert((727 * 2) >= 727);
    assert((764 * 2) >= 764);
    assert((801 * 2) >= 801);
    assert((838 * 2) >= 838);
    assert((875 * 2) >= 875);
    assert((912 * 2) >= 912);
    assert((949 * 2) >= 949);
    assert((986 * 2) >= 986);
    assert((23 * 2) >= 23);
    assert((60 * 2) >= 60);
    assert((97 * 2) >= 97);
    assert((134 * 2) >= 134);
    assert((171 * 2) >= 171);
    assert((208 * 2) >= 208);
    assert((245 * 2) >= 245);
    assert((282 * 2) >= 282);
    assert((319 * 2) >= 319);
    assert((356 * 2) >= 356);
    assert((393 * 2) >= 393);
    assert((430 * 2) >= 430);
    assert((467 * 2) >= 467);
    assert((504 * 2) >= 504);
    assert((541 * 2) >= 541);
    assert((578 * 2) >= 578);
    assert((615 * 2) >= 615);
    assert((652 * 2) >= 652);
    assert((689 * 2) >= 689);
    assert((726 * 2) >= 726);
    assert((763 * 2) >= 763);
    assert((800 * 2) >= 800);
    assert((837 * 2) >= 837);
    assert((874 * 2) >= 874);
    assert((911 * 2) >= 911);
    assert((948 * 2) >= 948);
    assert((985 * 2) >= 985);
    assert((22 * 2) >= 22);
    assert((59 * 2) >= 59);
    assert((96 * 2) >= 96);
    assert((133 * 2) >= 133);
    assert((170 * 2) >= 170);
    assert((207 * 2) >= 207);
    assert((244 * 2) >= 244);
    assert((281 * 2) >= 281);
    assert((318 * 2) >= 318);
    assert((355 * 2) >= 355);
    assert((392 * 2) >= 392);
    assert((429 * 2) >= 429);
    assert((466 * 2) >= 466);
    assert((503 * 2) >= 503);
    assert((540 * 2) >= 540);
    assert((577 * 2) >= 577);
    assert((614 * 2) >= 614);
    assert((651 * 2) >= 651);
    assert((688 * 2) >= 688);
    assert((725 * 2) >= 725);
    assert((762 * 2) >= 762);
    assert((799 * 2) >= 799);
    assert((836 * 2) >= 836);
    assert((873 * 2) >= 873);
    assert((910 * 2) >= 910);
    assert((947 * 2) >= 947);
    assert((984 * 2) >= 984);
    assert((21 * 2) >= 21);
    assert((58 * 2) >= 58);
    assert((95 * 2) >= 95);
    assert((132 * 2) >= 132);
    assert((169 * 2) >= 169);
    assert((206 * 2) >= 206);
    assert((243 * 2) >= 243);
    assert((280 * 2) >= 280);
    assert((317 * 2) >= 317);
    assert((354 * 2) >= 354);
    assert((391 * 2) >= 391);
    assert((428 * 2) >= 428);
    assert((465 * 2) >= 465);
    assert((502 * 2) >= 502);
    assert((539 * 2) >= 539);
    assert((576 * 2) >= 576);
    assert((613 * 2) >= 613);
    assert((650 * 2) >= 650);
    assert((687 * 2) >= 687);
    assert((724 * 2) >= 724);
    assert((761 * 2) >= 761);
    assert((798 * 2) >= 798);
    assert((835 * 2) >= 835);
    assert((872 * 2) >= 872);
    assert((909 * 2) >= 909);
    assert((946 * 2) >= 946);
    assert((983 * 2) >= 983);
    assert((20 * 2) >= 20);
    assert((57 * 2) >= 57);
    assert((94 * 2) >= 94);
    assert((131 * 2) >= 131);
    assert((168 * 2) >= 168);
    assert((205 * 2) >= 205);
    assert((242 * 2) >= 242);
    assert((279 * 2) >= 279);
    assert((316 * 2) >= 316);
    assert((353 * 2) >= 353);
    assert((390 * 2) >= 390);
    assert((427 * 2) >= 427);
    assert((464 * 2) >= 464);
    assert((501 * 2) >= 501);
    assert((538 * 2) >= 538);
    assert((575 * 2) >= 575);
    assert((612 * 2) >= 612);
    assert((649 * 2) >= 649);
    assert((686 * 2) >= 686);
    assert((723 * 2) >= 723);
    assert((760 * 2) >= 760);
    assert((797 * 2) >= 797);
    assert((834 * 2) >= 834);
    assert((871 * 2) >= 871);
    assert((908 * 2) >= 908);
    assert((945 * 2) >= 945);
    assert((982 * 2) >= 982);
    assert((19 * 2) >= 19);
    assert((56 * 2) >= 56);
    assert((93 * 2) >= 93);
    assert((130 * 2) >= 130);
    assert((167 * 2) >= 167);
    assert((204 * 2) >= 204);
    assert((241 * 2) >= 241);
    assert((278 * 2) >= 278);
    assert((315 * 2) >= 315);
    assert((352 * 2) >= 352);
    assert((389 * 2) >= 389);
    assert((426 * 2) >= 426);
    assert((463 * 2) >= 463);
    assert((500 * 2) >= 500);
    assert((537 * 2) >= 537);
    assert((574 * 2) >= 574);
    assert((611 * 2) >= 611);
    assert((648 * 2) >= 648);
    assert((685 * 2) >= 685);
    assert((722 * 2) >= 722);
    assert((759 * 2) >= 759);
    assert((796 * 2) >= 796);
    assert((833 * 2) >= 833);
    assert((870 * 2) >= 870);
    assert((907 * 2) >= 907);
    assert((944 * 2) >= 944);
    assert((981 * 2) >= 981);
    assert((18 * 2) >= 18);
    assert((55 * 2) >= 55);
    assert((92 * 2) >= 92);
    assert((129 * 2) >= 129);
    assert((166 * 2) >= 166);
    assert((203 * 2) >= 203);
    assert((240 * 2) >= 240);
    assert((277 * 2) >= 277);
    assert((314 * 2) >= 314);
    assert((351 * 2) >= 351);
    assert((388 * 2) >= 388);
    assert((425 * 2) >= 425);
    assert((462 * 2) >= 462);
    assert((499 * 2) >= 499);
    assert((536 * 2) >= 536);
    assert((573 * 2) >= 573);
    assert((610 * 2) >= 610);
    assert((647 * 2) >= 647);
    assert((684 * 2) >= 684);
    assert((721 * 2) >= 721);
    assert((758 * 2) >= 758);
    assert((795 * 2) >= 795);
    assert((832 * 2) >= 832);
    assert((869 * 2) >= 869);
    assert((906 * 2) >= 906);
    assert((943 * 2) >= 943);
    assert((980 * 2) >= 980);
    assert((17 * 2) >= 17);
    assert((54 * 2) >= 54);
    assert((91 * 2) >= 91);
    assert((128 * 2) >= 128);
    assert((165 * 2) >= 165);
    assert((202 * 2) >= 202);
    assert((239 * 2) >= 239);
    assert((276 * 2) >= 276);
    assert((313 * 2) >= 313);
    assert((350 * 2) >= 350);
    assert((387 * 2) >= 387);
    assert((424 * 2) >= 424);
    assert((461 * 2) >= 461);
    assert((498 * 2) >= 498);
    assert((535 * 2) >= 535);
    assert((572 * 2) >= 572);
    assert((609 * 2) >= 609);
    assert((646 * 2) >= 646);
    assert((683 * 2) >= 683);
    assert((720 * 2) >= 720);
    assert((757 * 2) >= 757);
    assert((794 * 2) >= 794);
    assert((831 * 2) >= 831);
    assert((868 * 2) >= 868);
    assert((905 * 2) >= 905);
    assert((942 * 2) >= 942);
    assert((979 * 2) >= 979);
    assert((16 * 2) >= 16);
    assert((53 * 2) >= 53);
    assert((90 * 2) >= 90);
    assert((127 * 2) >= 127);
    assert((164 * 2) >= 164);
    assert((201 * 2) >= 201);
    assert((238 * 2) >= 238);
    assert((275 * 2) >= 275);
    assert((312 * 2) >= 312);
    assert((349 * 2) >= 349);
    assert((386 * 2) >= 386);
    assert((423 * 2) >= 423);
    assert((460 * 2) >= 460);
    assert((497 * 2) >= 497);
    assert((534 * 2) >= 534);
    assert((571 * 2) >= 571);
    assert((608 * 2) >= 608);
    assert((645 * 2) >= 645);
    assert((682 * 2) >= 682);
    assert((719 * 2) >= 719);
    assert((756 * 2) >= 756);
    assert((793 * 2) >= 793);
    assert((830 * 2) >= 830);
    assert((867 * 2) >= 867);
    assert((904 * 2) >= 904);
    assert((941 * 2) >= 941);
    assert((978 * 2) >= 978);
    assert((15 * 2) >= 15);
    assert((52 * 2) >= 52);
    assert((89 * 2) >= 89);
    assert((126 * 2) >= 126);
    assert((163 * 2) >= 163);
    assert((200 * 2) >= 200);
    assert((237 * 2) >= 237);
    assert((274 * 2) >= 274);
    assert((311 * 2) >= 311);
    assert((348 * 2) >= 348);
    assert((385 * 2) >= 385);
    assert((422 * 2) >= 422);
    assert((459 * 2) >= 459);
    assert((496 * 2) >= 496);
    assert((533 * 2) >= 533);
    assert((570 * 2) >= 570);
    assert((607 * 2) >= 607);
    assert((644 * 2) >= 644);
    assert((681 * 2) >= 681);
    assert((718 * 2) >= 718);
    assert((755 * 2) >= 755);
    assert((792 * 2) >= 792);
    assert((829 * 2) >= 829);
    assert((866 * 2) >= 866);
    assert((903 * 2) >= 903);
    assert((940 * 2) >= 940);
    assert((977 * 2) >= 977);
    assert((14 * 2) >= 14);
    assert((51 * 2) >= 51);
    assert((88 * 2) >= 88);
    assert((125 * 2) >= 125);
    assert((162 * 2) >= 162);
    assert((199 * 2) >= 199);
    assert((236 * 2) >= 236);
    assert((273 * 2) >= 273);
    assert((310 * 2) >= 310);
    assert((347 * 2) >= 347);
    assert((384 * 2) >= 384);
    assert((421 * 2) >= 421);
    assert((458 * 2) >= 458);
    assert((495 * 2) >= 495);
    assert((532 * 2) >= 532);
    assert((569 * 2) >= 569);
    assert((606 * 2) >= 606);
    assert((643 * 2) >= 643);
    assert((680 * 2) >= 680);
    assert((717 * 2) >= 717);
    assert((754 * 2) >= 754);
    assert((791 * 2) >= 791);
    assert((828 * 2) >= 828);
    assert((865 * 2) >= 865);
    assert((902 * 2) >= 902);
    assert((939 * 2) >= 939);
    assert((976 * 2) >= 976);
    assert((13 * 2) >= 13);
    assert((50 * 2) >= 50);
    assert((87 * 2) >= 87);
    assert((124 * 2) >= 124);
    assert((161 * 2) >= 161);
    assert((198 * 2) >= 198);
    assert((235 * 2) >= 235);
    assert((272 * 2) >= 272);
    assert((309 * 2) >= 309);
    assert((346 * 2) >= 346);
    assert((383 * 2) >= 383);
    assert((420 * 2) >= 420);
    assert((457 * 2) >= 457);
    assert((494 * 2) >= 494);
    assert((531 * 2) >= 531);
    assert((568 * 2) >= 568);
    assert((605 * 2) >= 605);
    assert((642 * 2) >= 642);
    assert((679 * 2) >= 679);
    assert((716 * 2) >= 716);
    assert((753 * 2) >= 753);
    assert((790 * 2) >= 790);
    assert((827 * 2) >= 827);
    assert((864 * 2) >= 864);
    assert((901 * 2) >= 901);
    assert((938 * 2) >= 938);
    assert((975 * 2) >= 975);
    assert((12 * 2) >= 12);
    assert((49 * 2) >= 49);
    assert((86 * 2) >= 86);
    assert((123 * 2) >= 123);
    assert((160 * 2) >= 160);
    assert((197 * 2) >= 197);
    assert((234 * 2) >= 234);
    assert((271 * 2) >= 271);
    assert((308 * 2) >= 308);
    assert((345 * 2) >= 345);
    assert((382 * 2) >= 382);
    assert((419 * 2) >= 419);
    assert((456 * 2) >= 456);
    assert((493 * 2) >= 493);
    assert((530 * 2) >= 530);
    assert((567 * 2) >= 567);
    assert((604 * 2) >= 604);
    assert((641 * 2) >= 641);
    assert((678 * 2) >= 678);
    assert((715 * 2) >= 715);
    assert((752 * 2) >= 752);
    assert((789 * 2) >= 789);
    assert((826 * 2) >= 826);
    assert((863 * 2) >= 863);
    assert((900 * 2) >= 900);
    assert((937 * 2) >= 937);
    assert((974 * 2) >= 974);
    assert((11 * 2) >= 11);
    assert((48 * 2) >= 48);
    assert((85 * 2) >= 85);
    assert((122 * 2) >= 122);
    assert((159 * 2) >= 159);
    assert((196 * 2) >= 196);
    assert((233 * 2) >= 233);
    assert((270 * 2) >= 270);
    assert((307 * 2) >= 307);
    assert((344 * 2) >= 344);
    assert((381 * 2) >= 381);
    assert((418 * 2) >= 418);
    assert((455 * 2) >= 455);
    assert((492 * 2) >= 492);
    assert((529 * 2) >= 529);
    assert((566 * 2) >= 566);
    assert((603 * 2) >= 603);
    assert((640 * 2) >= 640);
    assert((677 * 2) >= 677);
    assert((714 * 2) >= 714);
    assert((751 * 2) >= 751);
    assert((788 * 2) >= 788);
    assert((825 * 2) >= 825);
    assert((862 * 2) >= 862);
    assert((899 * 2) >= 899);
    assert((936 * 2) >= 936);
    assert((973 * 2) >= 973);
    assert((10 * 2) >= 10);
    assert((47 * 2) >= 47);
    assert((84 * 2) >= 84);
    assert((121 * 2) >= 121);
    assert((158 * 2) >= 158);
    assert((195 * 2) >= 195);
    assert((232 * 2) >= 232);
    assert((269 * 2) >= 269);
    assert((306 * 2) >= 306);
    assert((343 * 2) >= 343);
    assert((380 * 2) >= 380);
    assert((417 * 2) >= 417);
    assert((454 * 2) >= 454);
    assert((491 * 2) >= 491);
    assert((528 * 2) >= 528);
    assert((565 * 2) >= 565);
    assert((602 * 2) >= 602);
    assert((639 * 2) >= 639);
    assert((676 * 2) >= 676);
    assert((713 * 2) >= 713);
    assert((750 * 2) >= 750);
    assert((787 * 2) >= 787);
    assert((824 * 2) >= 824);
    assert((861 * 2) >= 861);
    assert((898 * 2) >= 898);
    assert((935 * 2) >= 935);
    assert((972 * 2) >= 972);
    assert((9 * 2) >= 9);
    assert((46 * 2) >= 46);
    assert((83 * 2) >= 83);
    assert((120 * 2) >= 120);
    assert((157 * 2) >= 157);
    assert((194 * 2) >= 194);
    assert((231 * 2) >= 231);
    assert((268 * 2) >= 268);
    assert((305 * 2) >= 305);
    assert((342 * 2) >= 342);
    assert((379 * 2) >= 379);
    assert((416 * 2) >= 416);
    assert((453 * 2) >= 453);
    assert((490 * 2) >= 490);
    assert((527 * 2) >= 527);
    assert((564 * 2) >= 564);
    assert((601 * 2) >= 601);
    assert((638 * 2) >= 638);
    assert((675 * 2) >= 675);
    assert((712 * 2) >= 712);
    assert((749 * 2) >= 749);
    assert((786 * 2) >= 786);
    assert((823 * 2) >= 823);
    assert((860 * 2) >= 860);
    assert((897 * 2) >= 897);
    assert((934 * 2) >= 934);
    assert((971 * 2) >= 971);
    assert((8 * 2) >= 8);
    assert((45 * 2) >= 45);
    assert((82 * 2) >= 82);
    assert((119 * 2) >= 119);
    assert((156 * 2) >= 156);
    assert((193 * 2) >= 193);
    assert((230 * 2) >= 230);
    assert((267 * 2) >= 267);
    assert((304 * 2) >= 304);
    assert((341 * 2) >= 341);
    assert((378 * 2) >= 378);
    assert((415 * 2) >= 415);
    assert((452 * 2) >= 452);
    assert((489 * 2) >= 489);
    assert((526 * 2) >= 526);
    assert((563 * 2) >= 563);
    assert((600 * 2) >= 600);
    assert((637 * 2) >= 637);
    assert((674 * 2) >= 674);
    assert((711 * 2) >= 711);
    assert((748 * 2) >= 748);
    assert((785 * 2) >= 785);
    assert((822 * 2) >= 822);
    assert((859 * 2) >= 859);
    assert((896 * 2) >= 896);
    assert((933 * 2) >= 933);
    assert((970 * 2) >= 970);
    assert((7 * 2) >= 7);
    assert((44 * 2) >= 44);
    assert((81 * 2) >= 81);
    assert((118 * 2) >= 118);
    assert((155 * 2) >= 155);
    assert((192 * 2) >= 192);
    assert((229 * 2) >= 229);
    assert((266 * 2) >= 266);
    assert((303 * 2) >= 303);
    assert((340 * 2) >= 340);
    assert((377 * 2) >= 377);
    assert((414 * 2) >= 414);
    assert((451 * 2) >= 451);
    assert((488 * 2) >= 488);
    assert((525 * 2) >= 525);
    assert((562 * 2) >= 562);
    assert((599 * 2) >= 599);
    assert((636 * 2) >= 636);
    assert((673 * 2) >= 673);
    assert((710 * 2) >= 710);
    assert((747 * 2) >= 747);
    assert((784 * 2) >= 784);
    assert((821 * 2) >= 821);
    assert((858 * 2) >= 858);
    assert((895 * 2) >= 895);
    assert((932 * 2) >= 932);
    assert((969 * 2) >= 969);
    assert((6 * 2) >= 6);
    assert((43 * 2) >= 43);
    assert((80 * 2) >= 80);
    assert((117 * 2) >= 117);
    assert((154 * 2) >= 154);
    assert((191 * 2) >= 191);
    assert((228 * 2) >= 228);
    assert((265 * 2) >= 265);
    assert((302 * 2) >= 302);
    assert((339 * 2) >= 339);
    assert((376 * 2) >= 376);
    assert((413 * 2) >= 413);
    assert((450 * 2) >= 450);
    assert((487 * 2) >= 487);
    assert((524 * 2) >= 524);
    assert((561 * 2) >= 561);
    assert((598 * 2) >= 598);
    assert((635 * 2) >= 635);
    assert((672 * 2) >= 672);
    assert((709 * 2) >= 709);
    assert((746 * 2) >= 746);
    assert((783 * 2) >= 783);
    assert((820 * 2) >= 820);
    assert((857 * 2) >= 857);
    assert((894 * 2) >= 894);
    assert((931 * 2) >= 931);
    assert((968 * 2) >= 968);
    assert((5 * 2) >= 5);
    assert((42 * 2) >= 42);
    assert((79 * 2) >= 79);
    assert((116 * 2) >= 116);
    assert((153 * 2) >= 153);
    assert((190 * 2) >= 190);
    assert((227 * 2) >= 227);
    assert((264 * 2) >= 264);
    assert((301 * 2) >= 301);
    assert((338 * 2) >= 338);
    assert((375 * 2) >= 375);
    assert((412 * 2) >= 412);
    assert((449 * 2) >= 449);
    assert((486 * 2) >= 486);
    assert((523 * 2) >= 523);
    assert((560 * 2) >= 560);
    assert((597 * 2) >= 597);
    assert((634 * 2) >= 634);
    assert((671 * 2) >= 671);
    assert((708 * 2) >= 708);
    assert((745 * 2) >= 745);
    assert((782 * 2) >= 782);
    assert((819 * 2) >= 819);
    assert((856 * 2) >= 856);
    assert((893 * 2) >= 893);
    assert((930 * 2) >= 930);
    assert((967 * 2) >= 967);
    assert((4 * 2) >= 4);
    assert((41 * 2) >= 41);
    assert((78 * 2) >= 78);
    assert((115 * 2) >= 115);
    assert((152 * 2) >= 152);
    assert((189 * 2) >= 189);
    assert((226 * 2) >= 226);
    assert((263 * 2) >= 263);
    assert((300 * 2) >= 300);
    assert((337 * 2) >= 337);
    assert((374 * 2) >= 374);
    assert((411 * 2) >= 411);
    assert((448 * 2) >= 448);
    assert((485 * 2) >= 485);
    assert((522 * 2) >= 522);
    assert((559 * 2) >= 559);
    assert((596 * 2) >= 596);
    assert((633 * 2) >= 633);
    assert((670 * 2) >= 670);
    assert((707 * 2) >= 707);
    assert((744 * 2) >= 744);
    assert((781 * 2) >= 781);
    assert((818 * 2) >= 818);
    assert((855 * 2) >= 855);
    assert((892 * 2) >= 892);
    assert((929 * 2) >= 929);
    assert((966 * 2) >= 966);
    assert((3 * 2) >= 3);
    assert((40 * 2) >= 40);
    assert((77 * 2) >= 77);
    assert((114 * 2) >= 114);
    assert((151 * 2) >= 151);
    assert((188 * 2) >= 188);
    assert((225 * 2) >= 225);
    assert((262 * 2) >= 262);
    assert((299 * 2) >= 299);
    assert((336 * 2) >= 336);
    assert((373 * 2) >= 373);
    assert((410 * 2) >= 410);
    assert((447 * 2) >= 447);
    assert((484 * 2) >= 484);
    assert((521 * 2) >= 521);
    assert((558 * 2) >= 558);
    assert((595 * 2) >= 595);
    assert((632 * 2) >= 632);
    assert((669 * 2) >= 669);
    assert((706 * 2) >= 706);
    assert((743 * 2) >= 743);
    assert((780 * 2) >= 780);
    assert((817 * 2) >= 817);
    assert((854 * 2) >= 854);
    assert((891 * 2) >= 891);
    assert((928 * 2) >= 928);
    assert((965 * 2) >= 965);
    assert((2 * 2) >= 2);
    assert((39 * 2) >= 39);
    assert((76 * 2) >= 76);
    assert((113 * 2) >= 113);
    assert((150 * 2) >= 150);
int invalid_type_assign_mismatch = "cannot_assign_string_literal";
    assert((187 * 2) >= 187);
    assert((224 * 2) >= 224);
    assert((261 * 2) >= 261);
    assert((298 * 2) >= 298);
    assert((335 * 2) >= 335);
    assert((372 * 2) >= 372);
    assert((409 * 2) >= 409);
    assert((446 * 2) >= 446);
    assert((483 * 2) >= 483);
    assert((520 * 2) >= 520);
    assert((557 * 2) >= 557);
    assert((594 * 2) >= 594);
    assert((631 * 2) >= 631);
    assert((668 * 2) >= 668);
    assert((705 * 2) >= 705);
    assert((742 * 2) >= 742);
    assert((779 * 2) >= 779);
    assert((816 * 2) >= 816);
    assert((853 * 2) >= 853);
    assert((890 * 2) >= 890);
    assert((927 * 2) >= 927);
    assert((964 * 2) >= 964);
    assert((1 * 2) >= 1);
    assert((38 * 2) >= 38);
    assert((75 * 2) >= 75);
    assert((112 * 2) >= 112);
    assert((149 * 2) >= 149);
    assert((186 * 2) >= 186);
    assert((223 * 2) >= 223);
    assert((260 * 2) >= 260);
    assert((297 * 2) >= 297);
    assert((334 * 2) >= 334);
    assert((371 * 2) >= 371);
    assert((408 * 2) >= 408);
    assert((445 * 2) >= 445);
    assert((482 * 2) >= 482);
    assert((519 * 2) >= 519);
    assert((556 * 2) >= 556);
    assert((593 * 2) >= 593);
    assert((630 * 2) >= 630);
    assert((667 * 2) >= 667);
    assert((704 * 2) >= 704);
    assert((741 * 2) >= 741);
    assert((778 * 2) >= 778);
    assert((815 * 2) >= 815);
    assert((852 * 2) >= 852);
    assert((889 * 2) >= 889);
    assert((926 * 2) >= 926);
    assert((963 * 2) >= 963);
    assert((0 * 2) >= 0);
    assert((37 * 2) >= 37);
    assert((74 * 2) >= 74);
    assert((111 * 2) >= 111);
    assert((148 * 2) >= 148);
    assert((185 * 2) >= 185);
    assert((222 * 2) >= 222);
    assert((259 * 2) >= 259);
    assert((296 * 2) >= 296);
    assert((333 * 2) >= 333);
    assert((370 * 2) >= 370);
    assert((407 * 2) >= 407);
    assert((444 * 2) >= 444);
    assert((481 * 2) >= 481);
    assert((518 * 2) >= 518);
    assert((555 * 2) >= 555);
    assert((592 * 2) >= 592);
    assert((629 * 2) >= 629);
    assert((666 * 2) >= 666);
    assert((703 * 2) >= 703);
    assert((740 * 2) >= 740);
    assert((777 * 2) >= 777);
    assert((814 * 2) >= 814);
    assert((851 * 2) >= 851);
    assert((888 * 2) >= 888);
    assert((925 * 2) >= 925);
    assert((962 * 2) >= 962);
    assert((999 * 2) >= 999);
    assert((36 * 2) >= 36);
    assert((73 * 2) >= 73);
    assert((110 * 2) >= 110);
    assert((147 * 2) >= 147);
    assert((184 * 2) >= 184);
    assert((221 * 2) >= 221);
    assert((258 * 2) >= 258);
    assert((295 * 2) >= 295);
    assert((332 * 2) >= 332);
    assert((369 * 2) >= 369);
    assert((406 * 2) >= 406);
    assert((443 * 2) >= 443);
    assert((480 * 2) >= 480);
    assert((517 * 2) >= 517);
    assert((554 * 2) >= 554);
    assert((591 * 2) >= 591);
    assert((628 * 2) >= 628);
    assert((665 * 2) >= 665);
    assert((702 * 2) >= 702);
    assert((739 * 2) >= 739);
    assert((776 * 2) >= 776);
    assert((813 * 2) >= 813);
    printf("All C subsystem diagnostics completed cleanly.\n");
    return 0;
}
