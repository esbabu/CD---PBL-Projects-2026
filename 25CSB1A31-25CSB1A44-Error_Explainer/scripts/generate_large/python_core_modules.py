"""
scripts/generate_large/python_core_modules.py
---------------------------------------------
Core utility and data structure modules in Python 3.
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Logging System
MODULES["logging_system"] = {
    "name": "logging_system",
    "description": "Python logging module with memory ring sink and formatters",
    "test_call": "test_logging_system()",
    "core": """
# ==================== Logging Subsystem ====================
class LogLevel(enum.IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50


@dataclasses.dataclass
class LogRecord:
    level: LogLevel
    timestamp: str
    logger_name: str
    message: str
    line_number: int


class MemoryLogSink:
    def __init__(self, capacity: int = 64):
        self.capacity = capacity
        self.buffer: List[LogRecord] = []

    def append(self, rec: LogRecord) -> None:
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(rec)

    def count(self) -> int:
        return len(self.buffer)

    def clear(self) -> None:
        self.buffer.clear()


class StructuredLogger:
    def __init__(self, name: str, min_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.min_level = min_level
        self.sink = MemoryLogSink()

    def log(self, level: LogLevel, msg: str, line: int = 0) -> None:
        if level < self.min_level:
            return
        rec = LogRecord(
            level=level,
            timestamp="2026-11-24T12:00:00Z",
            logger_name=self.name,
            message=msg,
            line_number=line
        )
        self.sink.append(rec)

    def debug(self, msg: str, line: int = 0) -> None:
        self.log(LogLevel.DEBUG, msg, line)

    def info(self, msg: str, line: int = 0) -> None:
        self.log(LogLevel.INFO, msg, line)

    def warn(self, msg: str, line: int = 0) -> None:
        self.log(LogLevel.WARN, msg, line)

    def error(self, msg: str, line: int = 0) -> None:
        self.log(LogLevel.ERROR, msg, line)


def test_logging_system() -> None:
    logger = StructuredLogger("PyAppCore", LogLevel.DEBUG)
    logger.debug("Init subcomponents", 12)
    logger.info("Service bind 0.0.0.0:8080", 25)
    logger.warn("Memory pressure 75%", 34)
    logger.error("DB connection retry exceeded", 50)
    assert logger.sink.count() == 4
""",
    "extended": """
class LogFormatter:
    @staticmethod
    def format_json(rec: LogRecord) -> str:
        return json.dumps({
            "level": rec.level.name,
            "ts": rec.timestamp,
            "logger": rec.logger_name,
            "msg": rec.message,
            "line": rec.line_number
        })
"""
}

# 2. LRU Cache
MODULES["lru_cache"] = {
    "name": "lru_cache",
    "description": "Doubly linked LRU Cache in Python 3",
    "test_call": "test_lru_cache()",
    "core": """
# ==================== LRU Cache ====================
class CacheNode:
    def __init__(self, key: str, val: Any):
        self.key = key
        self.val = val
        self.prev: Optional['CacheNode'] = None
        self.next: Optional['CacheNode'] = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.lookup: Dict[str, CacheNode] = {}
        self.head: Optional[CacheNode] = None
        self.tail: Optional[CacheNode] = None
        self.hits = 0
        self.misses = 0

    def _detach(self, node: CacheNode) -> None:
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def _attach_front(self, node: CacheNode) -> None:
        node.next = self.head
        node.prev = None
        if self.head:
            self.head.prev = node
        self.head = node
        if not self.tail:
            self.tail = node

    def get(self, key: str) -> Optional[Any]:
        if key not in self.lookup:
            self.misses += 1
            return None
        self.hits += 1
        node = self.lookup[key]
        self._detach(node)
        self._attach_front(node)
        return node.val

    def put(self, key: str, val: Any) -> None:
        if key in self.lookup:
            node = self.lookup[key]
            node.val = val
            self._detach(node)
            self._attach_front(node)
            return

        if len(self.lookup) >= self.capacity and self.tail:
            victim = self.tail
            self._detach(victim)
            del self.lookup[victim.key]

        new_node = CacheNode(key, val)
        self._attach_front(new_node)
        self.lookup[key] = new_node

    def size(self) -> int:
        return len(self.lookup)


def test_lru_cache() -> None:
    cache = LRUCache(3)
    cache.put("alpha", 100)
    cache.put("beta", 200)
    cache.put("gamma", 300)

    assert cache.get("alpha") == 100
    cache.put("delta", 400)
    assert cache.get("beta") is None
    assert cache.get("delta") == 400
""",
    "extended": """
class TimedCacheEntry:
    def __init__(self, val: Any, ttl_s: float):
        self.val = val
        self.expiry = time.time() + ttl_s

    def is_expired(self) -> bool:
        return time.time() > self.expiry
"""
}

# 3. String Utilities
MODULES["string_utils"] = {
    "name": "string_utils",
    "description": "Levenshtein distance, slugify, and wildcard matching in Python",
    "test_call": "test_string_utils()",
    "core": """
# ==================== String Utilities ====================
class StringUtils:
    @staticmethod
    def levenshtein(s1: str, s2: str) -> int:
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )
        return dp[m][n]

    @staticmethod
    def slugify(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\\w\\s-]', '', text)
        return re.sub(r'[-\\s]+', '-', text)

    @staticmethod
    def wildcard_match(pattern: str, text: str) -> bool:
        regex_pat = "^" + pattern.replace("*", ".*").replace("?", ".") + "$"
        return bool(re.match(regex_pat, text))


def test_string_utils() -> None:
    assert StringUtils.levenshtein("kitten", "sitting") == 3
    assert StringUtils.slugify("Hello World 2026!") == "hello-world-2026"
    assert StringUtils.wildcard_match("sys_*.csv", "sys_report.csv")
""",
    "extended": """
class TextMetrics:
    @staticmethod
    def word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def char_frequency(text: str) -> Dict[str, int]:
        freq: Dict[str, int] = collections.defaultdict(int)
        for c in text:
            freq[c] += 1
        return dict(freq)
"""
}

# 4. Checksum CRC
MODULES["checksum_crc"] = {
    "name": "checksum_crc",
    "description": "CRC32 and Adler-32 in Python 3",
    "test_call": "test_checksum_crc()",
    "core": """
# ==================== Checksum and CRC ====================
class CRC32Engine:
    _table: List[int] = []

    @classmethod
    def _init_table(cls) -> None:
        if cls._table:
            return
        cls._table = [0] * 256
        for i in range(256):
            rem = i
            for _ in range(8):
                if rem & 1:
                    rem = (rem >> 1) ^ 0xEDB88320
                else:
                    rem >>= 1
            cls._table[i] = rem

    @classmethod
    def compute(cls, data: bytes) -> int:
        cls._init_table()
        crc = 0xFFFFFFFF
        for b in data:
            idx = (crc ^ b) & 0xFF
            crc = (crc >> 8) ^ cls._table[idx]
        return crc ^ 0xFFFFFFFF


class Adler32Engine:
    @staticmethod
    def compute(data: bytes) -> int:
        MOD = 65521
        a, b = 1, 0
        for byte in data:
            a = (a + byte) % MOD
            b = (b + a) % MOD
        return (b << 16) | a


def test_checksum_crc() -> None:
    sample = b"123456789"
    val = CRC32Engine.compute(sample)
    assert val == 0xCBF43926
    adl = Adler32Engine.compute(sample)
    assert adl != 0
""",
    "extended": """
class Fletcher16Engine:
    @staticmethod
    def compute(data: bytes) -> int:
        sum1, sum2 = 0, 0
        for b in data:
            sum1 = (sum1 + b) % 255
            sum2 = (sum2 + sum1) % 255
        return (sum2 << 8) | sum1
"""
}

# 5. RLE Compression
MODULES["compression_rle"] = {
    "name": "compression_rle",
    "description": "Byte Run-Length Encoding in Python 3",
    "test_call": "test_compression_rle()",
    "core": """
# ==================== RLE Compression ====================
class RLECodec:
    @staticmethod
    def compress(data: bytes) -> bytes:
        if not data:
            return b""
        out = bytearray()
        i = 0
        while i < len(data):
            byte_val = data[i]
            count = 1
            while i + 1 < len(data) and data[i + 1] == byte_val and count < 255:
                count += 1
                i += 1
            out.append(count)
            out.append(byte_val)
            i += 1
        return bytes(out)

    @staticmethod
    def decompress(comp: bytes) -> bytes:
        out = bytearray()
        for i in range(0, len(comp), 2):
            count = comp[i]
            val = comp[i + 1]
            out.extend([val] * count)
        return bytes(out)


def test_compression_rle() -> None:
    raw = b"AAAAABBBCCCDDDDDD"
    comp = RLECodec.compress(raw)
    decomp = RLECodec.decompress(comp)
    assert decomp == raw
""",
    "extended": """
class CompressionStats:
    @staticmethod
    def ratio(raw_sz: int, comp_sz: int) -> float:
        return comp_sz / raw_sz if raw_sz > 0 else 1.0
"""
}
