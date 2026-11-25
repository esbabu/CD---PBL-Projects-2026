"""
scripts/generate_large/c_core_modules.py
----------------------------------------
Core data structures and utility modules in clean C11.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Logging System
MODULES["logging_system"] = {
    "name": "logging_system",
    "description": "C11 logging system with levels and ring buffer sink",
    "test_call": "log_run_tests();",
    "core": """
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
    log->name[sizeof(log->name) - 1] = '\\0';
    log->min_level = min_lvl;
    log_sink_init(&log->sink);
}

static void logger_log(logger_t* log, log_level_t lvl, const char* msg, int line) {
    if (lvl < log->min_level) return;
    log_record_t rec;
    rec.level = lvl;
    snprintf(rec.timestamp, sizeof(rec.timestamp), "2026-11-24T12:00:00Z");
    strncpy(rec.logger_name, log->name, sizeof(rec.logger_name) - 1);
    rec.logger_name[sizeof(rec.logger_name) - 1] = '\\0';
    strncpy(rec.message, msg, sizeof(rec.message) - 1);
    rec.message[sizeof(rec.message) - 1] = '\\0';
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
""",
    "extended": """
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
"""
}

# 2. LRU Cache
MODULES["lru_cache"] = {
    "name": "lru_cache",
    "description": "C11 double-linked array based LRU cache",
    "test_call": "lru_run_tests();",
    "core": """
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
            cache->entries[i].key[sizeof(cache->entries[i].key) - 1] = '\\0';
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
    cache->entries[lru_idx].key[sizeof(cache->entries[lru_idx].key) - 1] = '\\0';
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
""",
    "extended": """
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
"""
}

# 3. String Utilities
MODULES["string_utils"] = {
    "name": "string_utils",
    "description": "C11 Levenshtein distance, trimming, and prefix matching",
    "test_call": "strutil_run_tests();",
    "core": """
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
    if (*start == '\\0') {
        str[0] = '\\0';
        return;
    }
    char* end = str + strlen(str) - 1;
    while (end > start && isspace((unsigned char)*end)) end--;
    *(end + 1) = '\\0';
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
""",
    "extended": """
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
"""
}

# 4. Checksum CRC
MODULES["checksum_crc"] = {
    "name": "checksum_crc",
    "description": "CRC32 lookup table and Adler-32 implementation in C11",
    "test_call": "crc_run_tests();",
    "core": """
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
    const uint32_t MOD_ADLER = 65521;
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
""",
    "extended": """
static uint16_t c_fletcher16(const uint8_t* data, size_t count) {
    uint16_t sum1 = 0;
    uint16_t sum2 = 0;
    for (size_t i = 0; i < count; ++i) {
        sum1 = (uint16_t)((sum1 + data[i]) % 255);
        sum2 = (uint16_t)((sum2 + sum1) % 255);
    }
    return (uint16_t)((sum2 << 8) | sum1);
}
"""
}

# 5. Run-Length Compression
MODULES["compression_rle"] = {
    "name": "compression_rle",
    "description": "RLE byte encoding and decoding in C11",
    "test_call": "rle_run_tests();",
    "core": """
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
""",
    "extended": """
static double rle_calc_ratio(size_t orig, size_t comp) {
    return orig > 0 ? (double)comp / (double)orig : 1.0;
}
"""
}
