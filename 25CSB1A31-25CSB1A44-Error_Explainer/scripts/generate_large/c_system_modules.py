"""
scripts/generate_large/c_system_modules.py
------------------------------------------
System and business workflow modules in clean C11.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. State Machine
MODULES["state_machine"] = {
    "name": "state_machine",
    "description": "Finite state machine in C11",
    "test_call": "fsm_run_tests();",
    "core": """
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
""",
    "extended": """
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
"""
}

# 2. Bank Ledger
MODULES["bank_ledger"] = {
    "name": "bank_ledger",
    "description": "Double-entry accounting ledger in C11",
    "test_call": "bank_run_tests();",
    "core": """
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
    b->accounts[idx].name[sizeof(b->accounts[idx].name) - 1] = '\\0';
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
""",
    "extended": """
static double bank_total_assets(const c_bank_t* b) {
    double total = 0.0;
    for (size_t i = 0; i < b->count; ++i) {
        if (b->accounts[i].active) total += b->accounts[i].balance;
    }
    return total;
}
"""
}

# 3. Rate Limiter (Token Bucket)
MODULES["rate_limiter"] = {
    "name": "rate_limiter",
    "description": "Token bucket rate limiter in C11",
    "test_call": "rate_run_tests();",
    "core": """
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
""",
    "extended": """
static double rate_get_tokens(const c_token_bucket_t* tb) {
    return tb->tokens;
}
"""
}

# 4. Inventory System
MODULES["inventory_system"] = {
    "name": "inventory_system",
    "description": "Stock inventory catalog in C11",
    "test_call": "inv_run_tests();",
    "core": """
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
    inv->items[idx].sku[sizeof(inv->items[idx].sku) - 1] = '\\0';
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
""",
    "extended": """
static int inv_get_qty(const c_inventory_t* inv, const char* sku) {
    for (size_t i = 0; i < inv->count; ++i) {
        if (inv->items[i].in_use && strcmp(inv->items[i].sku, sku) == 0) {
            return inv->items[i].available;
        }
    }
    return 0;
}
"""
}

# 5. Order Pipeline
MODULES["order_pipeline"] = {
    "name": "order_pipeline",
    "description": "Order calculation, tax, and discount pipeline in C11",
    "test_call": "order_run_tests();",
    "core": """
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
""",
    "extended": """
static double order_tax_amount(double amount, double tax_rate) {
    return amount * tax_rate;
}
"""
}
