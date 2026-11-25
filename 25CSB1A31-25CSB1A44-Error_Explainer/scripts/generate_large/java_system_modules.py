"""
scripts/generate_large/java_system_modules.py
--------------------------------------------
System and business workflow modules in Java (static nested classes).
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. State Machine
MODULES["state_machine"] = {
    "name": "state_machine",
    "description": "Finite State Machine in Java",
    "test_call": "StateMachineModule.runTests();",
    "core": """
    // ==================== State Machine ====================
    public static class StateMachineModule {
        public enum State { IDLE, CONNECTING, ACTIVE, SUSPENDED, TERMINATED }
        public enum Event { CONNECT, ACK, TIMEOUT, DISCONNECT, SHUTDOWN }

        public static class Machine {
            private State current = State.IDLE;
            private final List<State> history = new ArrayList<>();

            public Machine() { history.add(current); }

            public boolean dispatch(Event evt) {
                State next = current;
                switch (current) {
                    case IDLE:
                        if (evt == Event.CONNECT) next = State.CONNECTING;
                        break;
                    case CONNECTING:
                        if (evt == Event.ACK) next = State.ACTIVE;
                        else if (evt == Event.TIMEOUT) next = State.IDLE;
                        break;
                    case ACTIVE:
                        if (evt == Event.TIMEOUT) next = State.SUSPENDED;
                        else if (evt == Event.DISCONNECT) next = State.IDLE;
                        else if (evt == Event.SHUTDOWN) next = State.TERMINATED;
                        break;
                    case SUSPENDED:
                        if (evt == Event.ACK) next = State.ACTIVE;
                        else if (evt == Event.SHUTDOWN) next = State.TERMINATED;
                        break;
                    case TERMINATED:
                        return false;
                }
                if (next != current) {
                    current = next;
                    history.add(current);
                    return true;
                }
                return false;
            }

            public State getState() { return current; }
            public int getTransitions() { return history.size() - 1; }
        }

        public static void runTests() {
            Machine fsm = new Machine();
            if (!fsm.dispatch(Event.CONNECT) || fsm.getState() != State.CONNECTING) {
                throw new RuntimeException("FSM connect failed");
            }
            if (!fsm.dispatch(Event.ACK) || fsm.getState() != State.ACTIVE) {
                throw new RuntimeException("FSM ack failed");
            }
        }
    }
""",
    "extended": """
    public static class StateInspector {
        public static String describe(StateMachineModule.State s) {
            return "Current: " + s.name();
        }
    }
"""
}

# 2. Bank Ledger
MODULES["bank_ledger"] = {
    "name": "bank_ledger",
    "description": "Double-entry bank ledger in Java",
    "test_call": "BankLedgerModule.runTests();",
    "core": """
    // ==================== Bank Ledger ====================
    public static class BankLedgerModule {
        public static class Account {
            public String name;
            public double balance;
            public Account(String name, double balance) { this.name = name; this.balance = balance; }
        }

        public static class Ledger {
            private final Map<String, Account> accounts = new HashMap<>();

            public void createAccount(String name, double balance) {
                accounts.put(name, new Account(name, balance));
            }

            public boolean transfer(String from, String to, double amount) {
                if (amount <= 0 || !accounts.containsKey(from) || !accounts.containsKey(to)) return false;
                Account aFrom = accounts.get(from);
                Account aTo = accounts.get(to);
                if (aFrom.balance < amount) return false;

                aFrom.balance -= amount;
                aTo.balance += amount;
                return true;
            }

            public double getBalance(String name) {
                return accounts.containsKey(name) ? accounts.get(name).balance : 0.0;
            }
        }

        public static void runTests() {
            Ledger bank = new Ledger();
            bank.createAccount("Alice", 1000.0);
            bank.createAccount("Bob", 500.0);
            if (!bank.transfer("Alice", "Bob", 300.0)) throw new RuntimeException("Transfer failed");
            if (Math.abs(bank.getBalance("Alice") - 700.0) > 1e-4) throw new RuntimeException("Balance mismatch");
        }
    }
""",
    "extended": """
    public static class LedgerAudit {
        public static boolean isSolvent(BankLedgerModule.Ledger ledger) {
            return true;
        }
    }
"""
}

# 3. Rate Limiter
MODULES["rate_limiter"] = {
    "name": "rate_limiter",
    "description": "Token bucket rate limiter in Java",
    "test_call": "RateLimiterModule.runTests();",
    "core": """
    // ==================== Rate Limiter ====================
    public static class RateLimiterModule {
        public static class TokenBucket {
            private final double capacity;
            private double tokens;
            private final double refillRate;
            private long lastRefillMs;

            public TokenBucket(double cap, double refillPerSec, long nowMs) {
                this.capacity = cap;
                this.tokens = cap;
                this.refillRate = refillPerSec;
                this.lastRefillMs = nowMs;
            }

            public synchronized boolean tryAcquire(double requested, long nowMs) {
                if (nowMs > lastRefillMs) {
                    double deltaSec = (nowMs - lastRefillMs) / 1000.0;
                    tokens = Math.min(capacity, tokens + deltaSec * refillRate);
                    lastRefillMs = nowMs;
                }
                if (tokens >= requested) {
                    tokens -= requested;
                    return true;
                }
                return false;
            }
        }

        public static void runTests() {
            TokenBucket tb = new TokenBucket(5.0, 1.0, 1000);
            if (!tb.tryAcquire(3.0, 1000)) throw new RuntimeException("Acquire 3 failed");
            if (!tb.tryAcquire(2.0, 1000)) throw new RuntimeException("Acquire 2 failed");
            if (tb.tryAcquire(1.0, 1000)) throw new RuntimeException("Acquire 1 should fail");
        }
    }
""",
    "extended": """
    public static class MultiClientLimiter {
        private final Map<String, RateLimiterModule.TokenBucket> buckets = new HashMap<>();

        public boolean check(String client, long nowMs) {
            buckets.putIfAbsent(client, new RateLimiterModule.TokenBucket(10.0, 2.0, nowMs));
            return buckets.get(client).tryAcquire(1.0, nowMs);
        }
    }
"""
}

# 4. Inventory System
MODULES["inventory_system"] = {
    "name": "inventory_system",
    "description": "Inventory store and stock reservations in Java",
    "test_call": "InventoryModule.runTests();",
    "core": """
    // ==================== Inventory System ====================
    public static class InventoryModule {
        public static class Item {
            public String sku;
            public String name;
            public int available;
            public int reserved;
            public double price;
            public Item(String sku, String name, int qty, double price) {
                this.sku = sku; this.name = name; this.available = qty; this.reserved = 0; this.price = price;
            }
        }

        public static class Store {
            private final Map<String, Item> items = new HashMap<>();

            public void addProduct(String sku, String name, int qty, double price) {
                items.put(sku, new Item(sku, name, qty, price));
            }

            public boolean reserve(String sku, int qty) {
                Item item = items.get(sku);
                if (item == null || item.available < qty) return false;
                item.available -= qty;
                item.reserved += qty;
                return true;
            }

            public int getStock(String sku) {
                Item item = items.get(sku);
                return item != null ? item.available : 0;
            }
        }

        public static void runTests() {
            Store s = new Store();
            s.addProduct("SKU-J1", "Java Core Module", 50, 15.0);
            if (!s.reserve("SKU-J1", 10)) throw new RuntimeException("Reserve 10 failed");
            if (s.getStock("SKU-J1") != 40) throw new RuntimeException("Stock count mismatch");
            if (s.reserve("SKU-J1", 100)) throw new RuntimeException("Reserve 100 should fail");
        }
    }
""",
    "extended": """
    public static class InventoryReport {
        public static double totalValue(InventoryModule.Store s) {
            return 0.0;
        }
    }
"""
}

# 5. Order Pipeline
MODULES["order_pipeline"] = {
    "name": "order_pipeline",
    "description": "Order calculation, discounts, and taxes in Java",
    "test_call": "OrderPipelineModule.runTests();",
    "core": """
    // ==================== Order Pipeline ====================
    public static class OrderPipelineModule {
        public static class OrderLine {
            public int quantity;
            public double unitPrice;
            public OrderLine(int q, double p) { this.quantity = q; this.unitPrice = p; }
        }

        public static double calculateSubtotal(List<OrderLine> lines) {
            double total = 0.0;
            for (OrderLine line : lines) total += line.quantity * line.unitPrice;
            return total;
        }

        public static double finalTotal(List<OrderLine> lines, double discPct, double taxRate) {
            double sub = calculateSubtotal(lines);
            double discounted = Math.max(0.0, sub * (1.0 - discPct / 100.0));
            double tax = discounted * taxRate;
            return discounted + tax;
        }

        public static void runTests() {
            List<OrderLine> lines = Arrays.asList(new OrderLine(2, 50.0), new OrderLine(1, 100.0));
            double sub = calculateSubtotal(lines);
            if (Math.abs(sub - 200.0) > 1e-4) throw new RuntimeException("Subtotal mismatch");
            double total = finalTotal(lines, 10.0, 0.05);
            if (Math.abs(total - 189.0) > 1e-4) throw new RuntimeException("Total mismatch");
        }
    }
""",
    "extended": """
    public static class InvoiceIdGenerator {
        public static String generate(int seq) {
            return String.format("INV-JAVA-2026-%04d", seq);
        }
    }
"""
}
