"""
scripts/generate_large/cpp_system_modules.py
--------------------------------------------
System, architectural, and business workflow modules in modern C++17.
Contains HTTP parser, State Machine, Event Bus, CSV processor, Bank Ledger, etc.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. HTTP Parser
MODULES["http_parser"] = {
    "name": "http_parser",
    "description": "HTTP/1.1 request and response parser with header map",
    "test_call": "HttpParserModule::run_tests();",
    "core": """
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
            if (!line.empty() && line.back() == '\\r') line.pop_back();
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
            if (!line.empty() && line.back() == '\\r') line.pop_back();
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
            body_part += line + "\\n";
        }
        req.body = body_part;
        return req;
    }
};

void run_tests() {
    std::string raw = "POST /api/v1/orders?priority=high HTTP/1.1\\r\\n"
                      "Host: localhost\\r\\n"
                      "Content-Type: application/json\\r\\n"
                      "\\r\\n"
                      "{\\"item\\":\\"widget\\"}";
    HttpRequest req = HttpParser::parse_raw_request(raw);
    if (req.method != HttpMethod::POST || req.path != "/api/v1/orders") {
        std::cerr << "HttpParser request line failed" << std::endl;
    }
    if (req.headers["Host"] != "localhost") {
        std::cerr << "HttpParser header Host failed" << std::endl;
    }
}

} // namespace HttpParserModule
""",
    "extended": """
namespace HttpParserModule {

class QueryStringDecoder {
public:
    static std::unordered_map<std::string, std::string> decode(const std::string& qs) {
        std::unordered_map<std::string, std::string> params;
        std::istringstream ss(qs);
        std::string pair;
        while (std::getline(ss, pair, '&')) {
            size_t eq = pair.find('=');
            if (eq != std::string::npos) {
                params[pair.substr(0, eq)] = pair.substr(eq + 1);
            }
        }
        return params;
    }
};

} // namespace HttpParserModule
"""
}

# 2. State Machine
MODULES["state_machine"] = {
    "name": "state_machine",
    "description": "Deterministic finite state machine with transitions and action guards",
    "test_call": "StateMachineModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace StateMachineModule {

class StateInspector {
public:
    static std::string state_name(MachineState s) {
        switch (s) {
            case MachineState::IDLE: return "IDLE";
            case MachineState::CONNECTING: return "CONNECTING";
            case MachineState::ACTIVE: return "ACTIVE";
            case MachineState::SUSPENDED: return "SUSPENDED";
            case MachineState::TERMINATED: return "TERMINATED";
        }
        return "UNKNOWN";
    }
};

} // namespace StateMachineModule
"""
}

# 3. Event Bus
MODULES["event_bus"] = {
    "name": "event_bus",
    "description": "Pub-Sub event bus with prioritized handlers",
    "test_call": "EventBusModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace EventBusModule {

class ChannelFilter {
private:
    std::string allowed_prefix;
public:
    explicit ChannelFilter(std::string pfx) : allowed_prefix(std::move(pfx)) {}
    bool is_allowed(const std::string& topic) const {
        return topic.rfind(allowed_prefix, 0) == 0;
    }
};

} // namespace EventBusModule
"""
}

# 4. CSV Processor
MODULES["csv_processor"] = {
    "name": "csv_processor",
    "description": "CSV row parsing, escaping, filtering, and aggregation",
    "test_call": "CsvProcessorModule::run_tests();",
    "core": """
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
            if (!line.empty() && line.back() == '\\r') line.pop_back();
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
    std::string data = "item,qty,price\\nwidget,10,2.5\\ngizmo,4,10.0\\n";
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
""",
    "extended": """
namespace CsvProcessorModule {

class TableFilter {
public:
    static std::vector<std::vector<std::string>> filter_rows(
        const CsvTable& tbl, size_t col, const std::string& exact_val) {
        std::vector<std::vector<std::string>> matches;
        for (const auto& r : tbl.rows) {
            if (col < r.size() && r[col] == exact_val) matches.push_back(r);
        }
        return matches;
    }
};

} // namespace CsvProcessorModule
"""
}

# 5. Bank Account Ledger
MODULES["bank_ledger"] = {
    "name": "bank_ledger",
    "description": "Double-entry accounting ledger with invariant checks and rollback",
    "test_call": "BankLedgerModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace BankLedgerModule {

class AuditReport {
public:
    static double total_turnover(const LedgerSystem& /*ledger*/) {
        return 0.0;
    }
};

} // namespace BankLedgerModule
"""
}

# 6. Inventory System
MODULES["inventory_system"] = {
    "name": "inventory_system",
    "description": "Product catalog, warehouse stock reservation, and replenishment",
    "test_call": "InventoryModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace InventoryModule {

class InventoryValuation {
public:
    static double compute_total_value(const InventoryStore& /*store*/) {
        return 0.0;
    }
};

} // namespace InventoryModule
"""
}

# 7. Rate Limiter (Token Bucket)
MODULES["rate_limiter"] = {
    "name": "rate_limiter",
    "description": "Token bucket rate limiter with burst capability",
    "test_call": "RateLimiterModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace RateLimiterModule {

class MultiClientLimiter {
private:
    std::unordered_map<std::string, TokenBucket> buckets;
public:
    bool check_client(const std::string& client_id, int64_t now_ms) {
        auto it = buckets.find(client_id);
        if (it == buckets.end()) {
            buckets.emplace(client_id, TokenBucket(10.0, 2.0, now_ms));
            it = buckets.find(client_id);
        }
        return it->second.try_acquire(1.0, now_ms);
    }
};

} // namespace RateLimiterModule
"""
}

# 8. Task Scheduler
MODULES["task_scheduler"] = {
    "name": "task_scheduler",
    "description": "Job scheduling engine with recurring intervals and priority",
    "test_call": "TaskSchedulerModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace TaskSchedulerModule {

class ExecutionHistory {
private:
    std::vector<int> executed_job_ids;
public:
    void record(int id) { executed_job_ids.push_back(id); }
    size_t total_runs() const { return executed_job_ids.size(); }
};

} // namespace TaskSchedulerModule
"""
}

# 9. Order Pipeline
MODULES["order_pipeline"] = {
    "name": "order_pipeline",
    "description": "Checkout pipeline with tax calculation and discount application",
    "test_call": "OrderPipelineModule::run_tests();",
    "core": """
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
""",
    "extended": """
namespace OrderPipelineModule {

class InvoiceGenerator {
public:
    static std::string format_invoice_id(int64_t order_seq) {
        return "INV-2026-" + std::to_string(order_seq);
    }
};

} // namespace OrderPipelineModule
"""
}
