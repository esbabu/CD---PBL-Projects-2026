"""
scripts/generate_large/python_system_modules.py
-----------------------------------------------
System, architectural, and workflow modules in clean Python 3.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. State Machine
MODULES["state_machine"] = {
    "name": "state_machine",
    "description": "Finite State Machine in Python 3",
    "test_call": "test_state_machine()",
    "core": """
# ==================== State Machine ====================
class MachineState(enum.Enum):
    IDLE = 1
    CONNECTING = 2
    ACTIVE = 3
    SUSPENDED = 4
    TERMINATED = 5


class MachineEvent(enum.Enum):
    CONNECT = 1
    ACK = 2
    TIMEOUT = 3
    DISCONNECT = 4
    SHUTDOWN = 5


class FiniteStateMachine:
    def __init__(self):
        self.state = MachineState.IDLE
        self.history: List[MachineState] = [self.state]

    def dispatch(self, event: MachineEvent) -> bool:
        nxt = self.state
        if self.state == MachineState.IDLE:
            if event == MachineEvent.CONNECT:
                nxt = MachineState.CONNECTING
        elif self.state == MachineState.CONNECTING:
            if event == MachineEvent.ACK:
                nxt = MachineState.ACTIVE
            elif event == MachineEvent.TIMEOUT:
                nxt = MachineState.IDLE
        elif self.state == MachineState.ACTIVE:
            if event == MachineEvent.TIMEOUT:
                nxt = MachineState.SUSPENDED
            elif event == MachineEvent.DISCONNECT:
                nxt = MachineState.IDLE
            elif event == MachineEvent.SHUTDOWN:
                nxt = MachineState.TERMINATED
        elif self.state == MachineState.SUSPENDED:
            if event == MachineEvent.ACK:
                nxt = MachineState.ACTIVE
            elif event == MachineEvent.SHUTDOWN:
                nxt = MachineState.TERMINATED
        elif self.state == MachineState.TERMINATED:
            return False

        if nxt != self.state:
            self.state = nxt
            self.history.append(self.state)
            return True
        return False


def test_state_machine() -> None:
    fsm = FiniteStateMachine()
    assert fsm.dispatch(MachineEvent.CONNECT)
    assert fsm.state == MachineState.CONNECTING
    assert fsm.dispatch(MachineEvent.ACK)
    assert fsm.state == MachineState.ACTIVE
""",
    "extended": """
class StateTracker:
    @staticmethod
    def total_transitions(fsm: FiniteStateMachine) -> int:
        return len(fsm.history) - 1
"""
}

# 2. Bank Ledger
MODULES["bank_ledger"] = {
    "name": "bank_ledger",
    "description": "Double-entry accounting ledger in Python 3",
    "test_call": "test_bank_ledger()",
    "core": """
# ==================== Bank Ledger ====================
@dataclasses.dataclass
class Account:
    name: str
    balance: float


class BankLedger:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def create_account(self, name: str, init_bal: float) -> None:
        self.accounts[name] = Account(name, init_bal)

    def transfer(self, src: str, dst: str, amt: float) -> bool:
        if amt <= 0.0 or src not in self.accounts or dst not in self.accounts:
            return False
        if self.accounts[src].balance < amt:
            return False
        self.accounts[src].balance -= amt
        self.accounts[dst].balance += amt
        return True

    def total_liquidity(self) -> float:
        return sum(a.balance for a in self.accounts.values())


def test_bank_ledger() -> None:
    bank = BankLedger()
    bank.create_account("Alice", 1000.0)
    bank.create_account("Bob", 500.0)
    assert bank.transfer("Alice", "Bob", 300.0)
    assert abs(bank.accounts["Alice"].balance - 700.0) < 1e-4
    assert abs(bank.total_liquidity() - 1500.0) < 1e-4
""",
    "extended": """
class LedgerAudit:
    @staticmethod
    def audit_accounts(bank: BankLedger) -> bool:
        return all(a.balance >= 0.0 for a in bank.accounts.values())
"""
}

# 3. Rate Limiter
MODULES["rate_limiter"] = {
    "name": "rate_limiter",
    "description": "Token bucket rate limiter in Python 3",
    "test_call": "test_rate_limiter()",
    "core": """
# ==================== Rate Limiter ====================
class TokenBucket:
    def __init__(self, capacity: float, refill_rate_per_sec: float, now_ms: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate_per_sec
        self.last_refill_ms = now_ms

    def try_acquire(self, tokens: float, now_ms: int) -> bool:
        if now_ms > self.last_refill_ms:
            delta_sec = (now_ms - self.last_refill_ms) / 1000.0
            self.tokens = min(self.capacity, self.tokens + delta_sec * self.refill_rate)
            self.last_refill_ms = now_ms

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


def test_rate_limiter() -> None:
    tb = TokenBucket(5.0, 1.0, 1000)
    assert tb.try_acquire(3.0, 1000)
    assert tb.try_acquire(2.0, 1000)
    assert not tb.try_acquire(1.0, 1000)
""",
    "extended": """
class MultiClientLimiter:
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}

    def allow(self, client: str, now_ms: int) -> bool:
        if client not in self.buckets:
            self.buckets[client] = TokenBucket(10.0, 2.0, now_ms)
        return self.buckets[client].try_acquire(1.0, now_ms)
"""
}

# 4. Inventory System
MODULES["inventory_system"] = {
    "name": "inventory_system",
    "description": "Inventory store and stock reservations in Python 3",
    "test_call": "test_inventory_system()",
    "core": """
# ==================== Inventory System ====================
@dataclasses.dataclass
class Product:
    sku: str
    name: str
    available: int
    reserved: int
    price: float


class InventorySystem:
    def __init__(self):
        self.items: Dict[str, Product] = {}

    def add_product(self, sku: str, name: str, qty: int, price: float) -> None:
        self.items[sku] = Product(sku, name, qty, 0, price)

    def reserve(self, sku: str, qty: int) -> bool:
        if sku not in self.items or self.items[sku].available < qty:
            return False
        self.items[sku].available -= qty
        self.items[sku].reserved += qty
        return True

    def get_stock(self, sku: str) -> int:
        return self.items[sku].available if sku in self.items else 0


def test_inventory_system() -> None:
    inv = InventorySystem()
    inv.add_product("SKU-99", "Module Sensor", 50, 25.0)
    assert inv.reserve("SKU-99", 10)
    assert inv.get_stock("SKU-99") == 40
    assert not inv.reserve("SKU-99", 100)
""",
    "extended": """
class InventoryValuation:
    @staticmethod
    def total_value(inv: InventorySystem) -> float:
        return sum(p.available * p.price for p in inv.items.values())
"""
}

# 5. Order Pipeline
MODULES["order_pipeline"] = {
    "name": "order_pipeline",
    "description": "Order calculation, discounts, and taxes in Python 3",
    "test_call": "test_order_pipeline()",
    "core": """
# ==================== Order Pipeline ====================
@dataclasses.dataclass
class OrderLine:
    quantity: int
    unit_price: float


class OrderPipeline:
    @staticmethod
    def calculate_subtotal(lines: List[OrderLine]) -> float:
        return sum(line.quantity * line.unit_price for line in lines)

    @staticmethod
    def final_total(lines: List[OrderLine], discount_pct: float, tax_rate: float) -> float:
        sub = OrderPipeline.calculate_subtotal(lines)
        discounted = max(0.0, sub * (1.0 - discount_pct / 100.0))
        tax = discounted * tax_rate
        return discounted + tax


def test_order_pipeline() -> None:
    lines = [OrderLine(2, 50.0), OrderLine(1, 100.0)]
    sub = OrderPipeline.calculate_subtotal(lines)
    assert abs(sub - 200.0) < 1e-4
    total = OrderPipeline.final_total(lines, 10.0, 0.05)
    assert abs(total - 189.0) < 1e-4
""",
    "extended": """
class InvoiceGenerator:
    @staticmethod
    def generate_id(seq: int) -> str:
        return f"INV-PY-2026-{seq:04d}"
"""
}
