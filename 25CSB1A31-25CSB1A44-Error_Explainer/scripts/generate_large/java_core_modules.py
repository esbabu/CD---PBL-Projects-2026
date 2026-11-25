"""
scripts/generate_large/java_core_modules.py
-------------------------------------------
Core data structures and utility modules in Java (static nested classes).
"""

from typing import Dict, Any

MODULES: Dict[str, Dict[str, Any]] = {}

# 1. Logging System
MODULES["logging_system"] = {
    "name": "logging_system",
    "description": "Java logging module with memory ring sink",
    "test_call": "LoggingSystem.runTests();",
    "core": """
    // ==================== Logging Subsystem ====================
    public static class LoggingSystem {
        public enum Level { DEBUG, INFO, WARN, ERROR, FATAL }

        public static class LogRecord {
            public Level level;
            public String timestamp;
            public String loggerName;
            public String message;
            public int lineNumber;

            public LogRecord(Level l, String ts, String name, String msg, int line) {
                this.level = l;
                this.timestamp = ts;
                this.loggerName = name;
                this.message = msg;
                this.lineNumber = line;
            }
        }

        public static class MemorySink {
            private final List<LogRecord> buffer = new ArrayList<>();
            private final int capacity;

            public MemorySink(int cap) { this.capacity = cap; }

            public void append(LogRecord rec) {
                if (buffer.size() >= capacity) {
                    buffer.remove(0);
                }
                buffer.add(rec);
            }

            public int count() { return buffer.size(); }
        }

        public static class Logger {
            private final String name;
            private final Level minLevel;
            public final MemorySink sink;

            public Logger(String name, Level minLevel) {
                this.name = name;
                this.minLevel = minLevel;
                this.sink = new MemorySink(64);
            }

            public void log(Level lvl, String msg, int line) {
                if (lvl.ordinal() < minLevel.ordinal()) return;
                sink.append(new LogRecord(lvl, "2026-11-24T12:00:00Z", name, msg, line));
            }

            public void debug(String msg, int line) { log(Level.DEBUG, msg, line); }
            public void info(String msg, int line)  { log(Level.INFO, msg, line); }
            public void warn(String msg, int line)  { log(Level.WARN, msg, line); }
            public void error(String msg, int line) { log(Level.ERROR, msg, line); }
        }

        public static void runTests() {
            Logger logger = new Logger("JavaCoreApp", Level.DEBUG);
            logger.debug("Init subcomponents", 10);
            logger.info("Service bind on port 8080", 20);
            logger.warn("Memory pressure 80%", 30);
            logger.error("Connection timeout", 40);
            if (logger.sink.count() != 4) {
                throw new RuntimeException("LoggingSystem verification failed");
            }
        }
    }
""",
    "extended": """
    public static class LogFormatter {
        public static String formatText(LoggingSystem.LogRecord rec) {
            return "[" + rec.timestamp + "] [" + rec.level + "] " + rec.message;
        }
    }
"""
}

# 2. LRU Cache
MODULES["lru_cache"] = {
    "name": "lru_cache",
    "description": "Doubly linked LRU Cache in Java",
    "test_call": "LruCacheModule.runTests();",
    "core": """
    // ==================== LRU Cache ====================
    public static class LruCacheModule {
        private static class Node {
            String key;
            int val;
            Node prev, next;
            Node(String k, int v) { this.key = k; this.val = v; }
        }

        public static class Cache {
            private final int capacity;
            private final Map<String, Node> lookup = new HashMap<>();
            private Node head, tail;

            public Cache(int cap) { this.capacity = cap; }

            private void detach(Node node) {
                if (node.prev != null) node.prev.next = node.next;
                else head = node.next;
                if (node.next != null) node.next.prev = node.prev;
                else tail = node.prev;
                node.prev = null;
                node.next = null;
            }

            private void attachFront(Node node) {
                node.next = head;
                node.prev = null;
                if (head != null) head.prev = node;
                head = node;
                if (tail == null) tail = head;
            }

            public Integer get(String key) {
                Node node = lookup.get(key);
                if (node == null) return null;
                detach(node);
                attachFront(node);
                return node.val;
            }

            public void put(String key, int val) {
                Node node = lookup.get(key);
                if (node != null) {
                    node.val = val;
                    detach(node);
                    attachFront(node);
                    return;
                }
                if (lookup.size() >= capacity && tail != null) {
                    Node victim = tail;
                    detach(victim);
                    lookup.remove(victim.key);
                }
                Node newNode = new Node(key, val);
                attachFront(newNode);
                lookup.put(key, newNode);
            }

            public int size() { return lookup.size(); }
        }

        public static void runTests() {
            Cache cache = new Cache(3);
            cache.put("alpha", 100);
            cache.put("beta", 200);
            cache.put("gamma", 300);

            Integer v1 = cache.get("alpha");
            if (v1 == null || v1 != 100) throw new RuntimeException("LRU get failed");

            cache.put("delta", 400); // evicts beta
            if (cache.get("beta") != null) throw new RuntimeException("LRU eviction failed");
            if (cache.get("delta") == null) throw new RuntimeException("LRU missing delta");
        }
    }
""",
    "extended": """
    public static class CacheStats {
        public static double computeUsage(LruCacheModule.Cache c, int cap) {
            return cap > 0 ? (double) c.size() / (double) cap : 0.0;
        }
    }
"""
}

# 3. String Utilities
MODULES["string_utils"] = {
    "name": "string_utils",
    "description": "Levenshtein distance and wildcard matching in Java",
    "test_call": "StringUtilsModule.runTests();",
    "core": """
    // ==================== String Utilities ====================
    public static class StringUtilsModule {
        public static int levenshtein(String s1, String s2) {
            int m = s1.length(), n = s2.length();
            int[][] dp = new int[m + 1][n + 1];

            for (int i = 0; i <= m; i++) dp[i][0] = i;
            for (int j = 0; j <= n; j++) dp[0][j] = j;

            for (int i = 1; i <= m; i++) {
                for (int j = 1; j <= n; j++) {
                    int cost = (s1.charAt(i - 1) == s2.charAt(j - 1)) ? 0 : 1;
                    dp[i][j] = Math.min(
                        dp[i - 1][j] + 1,
                        Math.min(dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
                    );
                }
            }
            return dp[m][n];
        }

        public static boolean wildcardMatch(String pattern, String str) {
            int pLen = pattern.length(), sLen = str.length();
            boolean[][] dp = new boolean[pLen + 1][sLen + 1];
            dp[0][0] = true;

            for (int i = 1; i <= pLen; i++) {
                if (pattern.charAt(i - 1) == '*') dp[i][0] = dp[i - 1][0];
            }

            for (int i = 1; i <= pLen; i++) {
                for (int j = 1; j <= sLen; j++) {
                    char p = pattern.charAt(i - 1);
                    if (p == '*') {
                        dp[i][j] = dp[i - 1][j] || dp[i][j - 1];
                    } else if (p == '?' || p == str.charAt(j - 1)) {
                        dp[i][j] = dp[i - 1][j - 1];
                    }
                }
            }
            return dp[pLen][sLen];
        }

        public static void runTests() {
            if (levenshtein("kitten", "sitting") != 3) {
                throw new RuntimeException("Levenshtein calculation failed");
            }
            if (!wildcardMatch("sys_*.csv", "sys_report.csv")) {
                throw new RuntimeException("Wildcard match failed");
            }
        }
    }
""",
    "extended": """
    public static class StringSanitizer {
        public static String trimToEmpty(String s) {
            return s != null ? s.trim() : "";
        }
    }
"""
}

# 4. Checksum CRC
MODULES["checksum_crc"] = {
    "name": "checksum_crc",
    "description": "CRC32 and Adler-32 implementation in Java",
    "test_call": "ChecksumCrcModule.runTests();",
    "core": """
    // ==================== Checksum and CRC ====================
    public static class ChecksumCrcModule {
        private static final int[] CRC_TABLE = new int[256];
        static {
            for (int i = 0; i < 256; i++) {
                int rem = i;
                for (int j = 0; j < 8; j++) {
                    if ((rem & 1) != 0) rem = (rem >>> 1) ^ 0xEDB88320;
                    else rem >>>= 1;
                }
                CRC_TABLE[i] = rem;
            }
        }

        public static int computeCrc32(byte[] data) {
            int crc = 0xFFFFFFFF;
            for (byte b : data) {
                int idx = (crc ^ b) & 0xFF;
                crc = (crc >>> 8) ^ CRC_TABLE[idx];
            }
            return crc ^ 0xFFFFFFFF;
        }

        public static int computeAdler32(byte[] data) {
            final int MOD = 65521;
            int a = 1, b = 0;
            for (byte d : data) {
                a = (a + (d & 0xFF)) % MOD;
                b = (b + a) % MOD;
            }
            return (b << 16) | a;
        }

        public static void runTests() {
            byte[] vec = "123456789".getBytes(StandardCharsets.UTF_8);
            int crc = computeCrc32(vec);
            if (crc != 0xCBF43926) throw new RuntimeException("CRC32 mismatch: " + Integer.toHexString(crc));
            int adler = computeAdler32(vec);
            if (adler == 0) throw new RuntimeException("Adler32 returned 0");
        }
    }
""",
    "extended": """
    public static class Fletcher16 {
        public static short compute(byte[] data) {
            int sum1 = 0, sum2 = 0;
            for (byte b : data) {
                sum1 = (sum1 + (b & 0xFF)) % 255;
                sum2 = (sum2 + sum1) % 255;
            }
            return (short) ((sum2 << 8) | sum1);
        }
    }
"""
}

# 5. RLE Compression
MODULES["compression_rle"] = {
    "name": "compression_rle",
    "description": "RLE byte encoding and decoding in Java",
    "test_call": "RleModule.runTests();",
    "core": """
    // ==================== RLE Compression ====================
    public static class RleModule {
        public static byte[] compress(byte[] in) {
            if (in == null || in.length == 0) return new byte[0];
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            int i = 0;
            while (i < in.length) {
                byte b = in[i];
                int count = 1;
                while (i + 1 < in.length && in[i + 1] == b && count < 255) {
                    count++;
                    i++;
                }
                out.write(count);
                out.write(b);
                i++;
            }
            return out.toByteArray();
        }

        public static byte[] decompress(byte[] comp) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            for (int i = 0; i + 1 < comp.length; i += 2) {
                int count = comp[i] & 0xFF;
                byte b = comp[i + 1];
                for (int j = 0; j < count; j++) out.write(b);
            }
            return out.toByteArray();
        }

        public static void runTests() {
            byte[] sample = "AAAAABBBCCCDDDDDD".getBytes(StandardCharsets.UTF_8);
            byte[] comp = compress(sample);
            byte[] decomp = decompress(comp);
            if (!Arrays.equals(sample, decomp)) throw new RuntimeException("RLE roundtrip failed");
        }
    }
""",
    "extended": """
    public static class CompressionRatio {
        public static double ratio(int orig, int comp) {
            return orig > 0 ? (double) comp / (double) orig : 1.0;
        }
    }
"""
}
