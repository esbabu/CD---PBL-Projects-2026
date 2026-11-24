// Lightweight vendored nlohmann::json-compatible header for OptAgent C++17 drivers.
// Inside sandbox-native Docker, system <nlohmann/json.hpp> is preferred when present.
#ifndef OPTAGENT_NLOHMANN_JSON_HPP
#define OPTAGENT_NLOHMANN_JSON_HPP

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <iomanip>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

namespace nlohmann {

class json {
public:
    using array_t = std::vector<json>;
    using object_t = std::map<std::string, json>;
    using storage_t = std::variant<std::nullptr_t, bool, int64_t, double, std::string, array_t, object_t>;

    storage_t data;

    json() : data(nullptr) {}
    json(std::nullptr_t) : data(nullptr) {}
    json(bool v) : data(v) {}
    json(int v) : data(static_cast<int64_t>(v)) {}
    json(long v) : data(static_cast<int64_t>(v)) {}
    json(long long v) : data(static_cast<int64_t>(v)) {}
    json(unsigned int v) : data(static_cast<int64_t>(v)) {}
    json(unsigned long v) : data(static_cast<int64_t>(v)) {}
    json(unsigned long long v) : data(static_cast<int64_t>(v)) {}
    json(double v) : data(v) {}
    json(float v) : data(static_cast<double>(v)) {}
    json(const char *v) : data(std::string(v ? v : "")) {}
    json(std::string v) : data(std::move(v)) {}
    json(array_t v) : data(std::move(v)) {}
    json(object_t v) : data(std::move(v)) {}

    static json array() { return json(array_t{}); }
    static json object() { return json(object_t{}); }

    bool is_null() const { return std::holds_alternative<std::nullptr_t>(data); }
    bool is_boolean() const { return std::holds_alternative<bool>(data); }
    bool is_number_integer() const { return std::holds_alternative<int64_t>(data); }
    bool is_number_float() const { return std::holds_alternative<double>(data); }
    bool is_number() const { return is_number_integer() || is_number_float(); }
    bool is_string() const { return std::holds_alternative<std::string>(data); }
    bool is_array() const { return std::holds_alternative<array_t>(data); }
    bool is_object() const { return std::holds_alternative<object_t>(data); }

    size_t size() const {
        if (auto *a = std::get_if<array_t>(&data)) return a->size();
        if (auto *o = std::get_if<object_t>(&data)) return o->size();
        return 0;
    }

    void push_back(json v) {
        if (!is_array()) data = array_t{};
        std::get<array_t>(data).push_back(std::move(v));
    }

    bool contains(const std::string &k) const {
        if (auto *o = std::get_if<object_t>(&data)) return o->find(k) != o->end();
        return false;
    }

    json &operator[](const std::string &k) {
        if (!is_object()) data = object_t{};
        return std::get<object_t>(data)[k];
    }
    const json &at(const std::string &k) const { return std::get<object_t>(data).at(k); }
    const json &operator[](size_t i) const { return std::get<array_t>(data).at(i); }
    json &operator[](size_t i) { return std::get<array_t>(data).at(i); }

    template <typename T>
    T get() const;

    std::string dump() const {
        std::ostringstream os;
        dump_to(os);
        return os.str();
    }

    static json parse(const std::string &s) {
        size_t pos = 0;
        return parse_val(s, pos);
    }

private:
    static void escape_str(std::ostringstream &os, const std::string &s) {
        os << '"';
        for (unsigned char c : s) {
            if (c == '"') os << "\\\"";
            else if (c == '\\') os << "\\\\";
            else if (c == '\b') os << "\\b";
            else if (c == '\f') os << "\\f";
            else if (c == '\n') os << "\\n";
            else if (c == '\r') os << "\\r";
            else if (c == '\t') os << "\\t";
            else if (c < 0x20) {
                char buf[8];
                std::snprintf(buf, sizeof(buf), "\\u%04x", c);
                os << buf;
            } else os << static_cast<char>(c);
        }
        os << '"';
    }

    void dump_to(std::ostringstream &os) const {
        if (is_null()) { os << "null"; return; }
        if (auto *b = std::get_if<bool>(&data)) { os << (*b ? "true" : "false"); return; }
        if (auto *i = std::get_if<int64_t>(&data)) { os << *i; return; }
        if (auto *d = std::get_if<double>(&data)) {
            if (std::isnan(*d)) os << "{\"__float\":\"nan\"}";
            else if (std::isinf(*d)) os << (*d > 0 ? "{\"__float\":\"inf\"}" : "{\"__float\":\"-inf\"}");
            else if (*d == 0.0 && std::signbit(*d)) os << "{\"__float\":\"-0\"}";
            else {
                char buf[64];
                std::snprintf(buf, sizeof(buf), "%.17g", *d);
                os << buf;
            }
            return;
        }
        if (auto *s = std::get_if<std::string>(&data)) { escape_str(os, *s); return; }
        if (auto *a = std::get_if<array_t>(&data)) {
            os << '[';
            for (size_t i = 0; i < a->size(); i++) {
                if (i) os << ',';
                (*a)[i].dump_to(os);
            }
            os << ']';
            return;
        }
        if (auto *o = std::get_if<object_t>(&data)) {
            os << '{';
            bool first = true;
            for (const auto &kv : *o) {
                if (!first) os << ',';
                first = false;
                escape_str(os, kv.first);
                os << ':';
                kv.second.dump_to(os);
            }
            os << '}';
        }
    }

    static void skip_ws(const std::string &s, size_t &p) {
        while (p < s.size() && static_cast<unsigned char>(s[p]) <= 32) p++;
    }

    static std::string parse_str(const std::string &s, size_t &p) {
        if (p >= s.size() || s[p] != '"') throw std::runtime_error("Expected string");
        p++;
        std::string out;
        while (p < s.size() && s[p] != '"') {
            char c = s[p++];
            if (c == '\\' && p < s.size()) {
                char e = s[p++];
                switch (e) {
                    case '"': c = '"'; break;
                    case '\\': c = '\\'; break;
                    case '/': c = '/'; break;
                    case 'b': c = '\b'; break;
                    case 'f': c = '\f'; break;
                    case 'n': c = '\n'; break;
                    case 'r': c = '\r'; break;
                    case 't': c = '\t'; break;
                    default: c = e; break;
                }
            }
            out.push_back(c);
        }
        if (p >= s.size() || s[p] != '"') throw std::runtime_error("Unterminated string");
        p++;
        return out;
    }

    static json parse_val(const std::string &s, size_t &p) {
        skip_ws(s, p);
        if (p >= s.size()) throw std::runtime_error("Unexpected EOF");
        char c = s[p];
        if (s.compare(p, 4, "null") == 0) { p += 4; return json(nullptr); }
        if (s.compare(p, 4, "true") == 0) { p += 4; return json(true); }
        if (s.compare(p, 5, "false") == 0) { p += 5; return json(false); }
        if (c == '"') return json(parse_str(s, p));
        if (c == '[') {
            p++;
            array_t a;
            skip_ws(s, p);
            if (p < s.size() && s[p] == ']') { p++; return json(std::move(a)); }
            while (p < s.size()) {
                a.push_back(parse_val(s, p));
                skip_ws(s, p);
                if (p < s.size() && s[p] == ',') { p++; continue; }
                if (p < s.size() && s[p] == ']') { p++; return json(std::move(a)); }
                throw std::runtime_error("Malformed array");
            }
        }
        if (c == '{') {
            p++;
            object_t o;
            skip_ws(s, p);
            if (p < s.size() && s[p] == '}') { p++; return json(std::move(o)); }
            while (p < s.size()) {
                skip_ws(s, p);
                std::string k = parse_str(s, p);
                skip_ws(s, p);
                if (p >= s.size() || s[p] != ':') throw std::runtime_error("Expected ':'");
                p++;
                o[std::move(k)] = parse_val(s, p);
                skip_ws(s, p);
                if (p < s.size() && s[p] == ',') { p++; continue; }
                if (p < s.size() && s[p] == '}') { p++; return json(std::move(o)); }
                throw std::runtime_error("Malformed object");
            }
        }
        const char *start = s.c_str() + p;
        char *end_d = nullptr;
        double d = std::strtod(start, &end_d);
        if (end_d == start) throw std::runtime_error("Invalid number");
        bool is_fp = false;
        for (const char *q = start; q < end_d; q++) {
            if (*q == '.' || *q == 'e' || *q == 'E') { is_fp = true; break; }
        }
        p = static_cast<size_t>(end_d - s.c_str());
        if (!is_fp) {
            int64_t iv = std::strtoll(start, nullptr, 10);
            return json(iv);
        }
        return json(d);
    }
};

template <> inline bool json::get<bool>() const { return std::get<bool>(data); }
template <> inline int json::get<int>() const {
    return is_number_integer() ? static_cast<int>(std::get<int64_t>(data)) : static_cast<int>(std::get<double>(data));
}
template <> inline long json::get<long>() const {
    return is_number_integer() ? static_cast<long>(std::get<int64_t>(data)) : static_cast<long>(std::get<double>(data));
}
template <> inline long long json::get<long long>() const {
    return is_number_integer() ? static_cast<long long>(std::get<int64_t>(data)) : static_cast<long long>(std::get<double>(data));
}
template <> inline unsigned int json::get<unsigned int>() const {
    return is_number_integer() ? static_cast<unsigned int>(std::get<int64_t>(data)) : static_cast<unsigned int>(std::get<double>(data));
}
template <> inline size_t json::get<size_t>() const {
    return is_number_integer() ? static_cast<size_t>(std::get<int64_t>(data)) : static_cast<size_t>(std::get<double>(data));
}
template <> inline double json::get<double>() const {
    if (is_object() && contains("__float__")) {
        auto f = at("__float__").get<std::string>();
        if (f == "nan") return std::nan("");
        if (f == "inf") return INFINITY;
        if (f == "-inf") return -INFINITY;
        if (f == "-0") return -0.0;
    }
    return is_number_float() ? std::get<double>(data) : static_cast<double>(std::get<int64_t>(data));
}
template <> inline float json::get<float>() const { return static_cast<float>(get<double>()); }
template <> inline std::string json::get<std::string>() const { return std::get<std::string>(data); }

} // namespace nlohmann

#endif // OPTAGENT_NLOHMANN_JSON_HPP
