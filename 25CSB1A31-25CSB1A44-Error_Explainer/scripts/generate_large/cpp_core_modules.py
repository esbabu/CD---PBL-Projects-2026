"""
scripts/generate_large/cpp_core_modules.py
------------------------------------------
Core data structures and utility modules in modern C++17.
Each module contains a self-contained namespace, data types, logic, and run_tests().
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Logging System
MODULES["logging_system"] = {
    "name": "logging_system",
    "description": "Structured logging system with levels, sinks, and formatting",
    "test_call": "LoggingSystem::run_tests();",
    "core": """
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
""",
    "extended": """
namespace LoggingSystem {

class LogFormatter {
public:
    static std::string format_text(const LogRecord& rec) {
        std::string lvl_str;
        switch (rec.level) {
            case Level::DEBUG_LVL: lvl_str = "DEBUG"; break;
            case Level::INFO_LVL:  lvl_str = "INFO"; break;
            case Level::WARN_LVL:  lvl_str = "WARN"; break;
            case Level::ERROR_LVL: lvl_str = "ERROR"; break;
            case Level::FATAL_LVL: lvl_str = "FATAL"; break;
        }
        std::ostringstream oss;
        oss << "[" << rec.timestamp << "] [" << lvl_str << "] ["
            << rec.logger_name << ":" << rec.line_number << "] " << rec.message;
        return oss.str();
    }

    static std::string format_json(const LogRecord& rec) {
        std::ostringstream oss;
        oss << "{\\"time\\":\\"" << rec.timestamp << "\\",\\"logger\\":\\""
            << rec.logger_name << "\\",\\"msg\\":\\"" << rec.message << "\\"}";
        return oss.str();
    }
};

class FilteredLogSink {
private:
    std::vector<std::string> patterns;
    std::vector<LogRecord> matching_records;
public:
    void add_pattern(const std::string& pat) { patterns.push_back(pat); }
    void ingest(const LogRecord& rec) {
        for (const auto& pat : patterns) {
            if (rec.message.find(pat) != std::string::npos) {
                matching_records.push_back(rec);
                break;
            }
        }
    }
    size_t match_count() const { return matching_records.size(); }
};

} // namespace LoggingSystem
"""
}

# 2. LRU Cache
MODULES["lru_cache"] = {
    "name": "lru_cache",
    "description": "Double-linked list and hash map based LRU cache",
    "test_call": "LruCacheModule::run_tests();",
    "core": """
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
""",
    "extended": """
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
"""
}

# 3. JSON Parser
MODULES["json_parser"] = {
    "name": "json_parser",
    "description": "JSON tokenizer, AST node tree, and parser",
    "test_call": "JsonParserModule::run_tests();",
    "core": """
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
        while (pos < input.size() && (input[pos] == ' ' || input[pos] == '\\t' ||
                                      input[pos] == '\\n' || input[pos] == '\\r')) {
            pos++;
        }
    }

    char peek() {
        skip_whitespace();
        return pos < input.size() ? input[pos] : '\\0';
    }

    char get() {
        skip_whitespace();
        return pos < input.size() ? input[pos++] : '\\0';
    }

    std::string parse_string() {
        get(); // consume opening quote
        std::string res;
        while (pos < input.size() && input[pos] != '"') {
            if (input[pos] == '\\\\' && pos + 1 < input.size()) pos++;
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
            case JsonType::J_STRING: return "\\"" + val.str_val + "\\"";
            case JsonType::J_ARRAY: return "[]";
            case JsonType::J_OBJECT: return "{}";
        }
        return "null";
    }
};

void run_tests() {
    auto j1 = JsonDocument::parse_snippet("\\"status_ok\\"");
    if (j1.type != JsonType::J_STRING || j1.str_val != "status_ok") {
        std::cerr << "Json parse string failed" << std::endl;
    }
    auto j2 = JsonDocument::parse_snippet("42.5");
    if (j2.type != JsonType::J_NUMBER || j2.num_val < 42.0) {
        std::cerr << "Json parse number failed" << std::endl;
    }
}

} // namespace JsonParserModule
""",
    "extended": """
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
"""
}

# 4. Configuration Store
MODULES["config_store"] = {
    "name": "config_store",
    "description": "Hierarchical configuration manager with type casting and defaults",
    "test_call": "ConfigStoreModule::run_tests();",
    "core": """
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
""",
    "extended": """
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
"""
}

# 5. String Utilities
MODULES["string_utils"] = {
    "name": "string_utils",
    "description": "String algorithms: Levenshtein distance, tokenization, wildcard matching",
    "test_call": "StringUtilsModule::run_tests();",
    "core": """
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
        size_t start = s.find_first_not_of(" \\t\\n\\r");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \\t\\n\\r");
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
""",
    "extended": """
namespace StringUtilsModule {

class PatternMatcher {
public:
    static bool wildcard_match(const char* pattern, const char* str) {
        if (*pattern == '\\0' && *str == '\\0') return true;
        if (*pattern == '*' && *(pattern + 1) != '\\0' && *str == '\\0') return false;
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
"""
}

# 6. Checksum and CRC
MODULES["checksum_crc"] = {
    "name": "checksum_crc",
    "description": "CRC32 lookup table and Adler-32 / Fletcher-16 checksums",
    "test_call": "ChecksumModule::run_tests();",
    "core": """
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
""",
    "extended": """
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
"""
}

# 7. Run-Length Compression
MODULES["compression_rle"] = {
    "name": "compression_rle",
    "description": "Run-length byte encoding and decoding with integrity checks",
    "test_call": "RleModule::run_tests();",
    "core": """
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
""",
    "extended": """
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
"""
}
