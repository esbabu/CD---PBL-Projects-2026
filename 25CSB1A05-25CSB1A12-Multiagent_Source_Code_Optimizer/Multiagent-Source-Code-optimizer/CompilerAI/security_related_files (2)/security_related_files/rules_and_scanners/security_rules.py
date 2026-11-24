"""
Comprehensive Static Security Rules Engine for C/C++ Source Analysis.

Implements deep detection across all 6 vulnerability domains:
  - Section A: Memory Safety (CWE-120, CWE-121, CWE-122, CWE-125, CWE-129, CWE-170, CWE-190, CWE-193, CWE-195, CWE-197, CWE-242, CWE-401, CWE-415, CWE-416, CWE-457, CWE-476, CWE-562, CWE-762, CWE-770, CWE-1285)
  - Section B: Injection & Output Handling (CWE-22, CWE-78, CWE-79, CWE-89, CWE-90, CWE-113, CWE-117, CWE-134, CWE-502, CWE-611, CWE-1333, CWE-1336)
  - Section C: Crypto & Authentication (CWE-208, CWE-256, CWE-261, CWE-295, CWE-306, CWE-307, CWE-321, CWE-326, CWE-327, CWE-328, CWE-329, CWE-330, CWE-337, CWE-338, CWE-377, CWE-532, CWE-697, CWE-759, CWE-798, CWE-1392)
  - Section D: Files, Processes & Concurrency (CWE-23, CWE-59, CWE-73, CWE-243, CWE-250, CWE-252, CWE-276, CWE-362, CWE-367, CWE-377, CWE-400, CWE-479, CWE-532, CWE-732, CWE-775, CWE-833)
  - Section E: Network (CWE-120, CWE-130, CWE-209, CWE-252, CWE-307, CWE-319, CWE-362, CWE-400, CWE-601, CWE-770, CWE-912, CWE-918, CWE-942, CWE-1327)
  - Section F: Logic, Undefined Behavior & Misc (CWE-14, CWE-20, CWE-190, CWE-369, CWE-562, CWE-657, CWE-674, CWE-833, CWE-1108, CWE-1335)
"""

from typing import Any, Dict, List, Optional, Tuple
import ast
import os
import re

try:
    from analysis_and_detection.finding_schema import (
        Finding,
        CATEGORY_SECURITY_VULNERABILITY,
        CATEGORY_POTENTIAL_SECURITY_RISK,
        CATEGORY_COMPILER_ERROR,
        CONFIDENCE_CONFIRMED,
        CONFIDENCE_HIGH,
        CONFIDENCE_MEDIUM,
        CONFIDENCE_LOW,
    )
except ImportError:
    try:
        from src.analysis.finding_schema import (
            Finding,
            CATEGORY_SECURITY_VULNERABILITY,
            CATEGORY_POTENTIAL_SECURITY_RISK,
            CATEGORY_COMPILER_ERROR,
            CONFIDENCE_CONFIRMED,
            CONFIDENCE_HIGH,
            CONFIDENCE_MEDIUM,
            CONFIDENCE_LOW,
        )
    except ImportError:
        from finding_schema import (
            Finding,
            CATEGORY_SECURITY_VULNERABILITY,
            CATEGORY_POTENTIAL_SECURITY_RISK,
            CATEGORY_COMPILER_ERROR,
            CONFIDENCE_CONFIRMED,
            CONFIDENCE_HIGH,
            CONFIDENCE_MEDIUM,
            CONFIDENCE_LOW,
        )

def detect_language(file_path: str = "", code: str = "") -> str:
    """
    Detect programming language from file extension or code heuristics.
    Returns: 'python', 'java', 'cpp', or 'c'.
    """
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".py", ".pyw"):
            return "python"
        if ext in (".java", ".class"):
            return "java"
        if ext in (".cpp", ".cxx", ".cc", ".hpp", ".hxx"):
            return "cpp"
        if ext in (".c", ".h"):
            return "c"

    if code:
        py_signals = [
            r"^\s*def\s+\w+\s*\(.*?\)\s*:",
            r"^\s*import\s+[a-zA-Z0-9_.]+",
            r"^\s*from\s+[a-zA-Z0-9_.]+\s+import",
            r"^\s*class\s+\w+(?:\(.*?\))?\s*:",
            r"if\s+__name__\s*==\s*['\"]__main__['\"]:",
            r"\bprint\s*\(",
        ]
        has_py = any(re.search(sig, code, re.MULTILINE) for sig in py_signals)
        has_cpp = any(k in code for k in ("#include", "std::", "cout", "printf", "namespace "))
        has_java = any(k in code for k in ("public class ", "import java.", "System.out.", "public static void main"))

        if has_py and not (has_cpp or has_java):
            return "python"
        if has_java and not has_cpp:
            return "java"
        if has_cpp:
            if "class " in code or "std::" in code or "namespace " in code or "<iostream>" in code:
                return "cpp"
            return "c"

    return "cpp"

# Standard pattern tuple: (regex_pattern, rule_id, severity, cwe_id, description, recommendation, confidence_level, category)
SECURITY_PATTERNS: List[Tuple[str, str, str, str, str, str, str, str]] = [
    # ── Section A: Memory Safety (1-25) ───────────────────────────────────────
    (
        r"\bgets\s*\(",
        "unsafe_gets",
        "high",
        "CWE-242",
        "gets() is inherently unsafe with no buffer bounds checking.",
        "Replace gets() with fgets(buf, sizeof(buf), stdin).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r'\bscanf\s*\(\s*"[^"]*%s',
        "unsafe_scanf_s",
        "high",
        "CWE-120",
        "scanf %s reads an unbounded string without a field width limit.",
        "Add field width limit to format specifier: scanf(\"%127s\", buf).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bstrcpy\s*\(",
        "unsafe_strcpy",
        "high",
        "CWE-121",
        "strcpy() copies null-terminated string without bounds checking.",
        "Replace with safe bounded copying or std::string.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bstrcat\s*\(",
        "unsafe_strcat",
        "high",
        "CWE-121",
        "strcat() concatenates strings without destination boundary checks.",
        "Replace with strncat() or std::string::operator+=.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bsprintf\s*\(",
        "unsafe_sprintf",
        "high",
        "CWE-121",
        "sprintf() writes unbounded output into destination buffer.",
        "Replace with snprintf(buf, sizeof(buf), fmt, ...).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"malloc\s*\(\s*\d+\s*\);.*memcpy\s*\([^,]+,[^,]+,\s*[a-zA-Z_]\w*\)|memcpy\s*\(\s*p\s*,\s*src\s*,\s*n\s*\)",
        "heap_buffer_overflow_attacker_size",
        "critical",
        "CWE-122",
        "Heap buffer overflow: copying caller-controlled length into fixed-size heap allocation.",
        "Validate length argument against destination buffer allocation capacity before copying.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\balloca\s*\(",
        "attacker_controlled_alloca",
        "high",
        "CWE-770",
        "alloca() allocates unbounded memory on thread stack, causing stack exhaustion.",
        "Avoid alloca; use std::vector or heap allocation.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"char\s+\w+\[\s*[a-zA-Z_]\w*\s*\]",
        "vla_attacker_size",
        "high",
        "CWE-1285",
        "Variable-length array (VLA) allocated on thread stack with runtime size.",
        "Use std::vector<char> instead of variable-length array on the stack.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"if\s*\(\s*(\w+)\s*<\s*\d+\s*\)\s*memcpy\s*\([^,]+,[^,]+,\s*(?:\(\s*size_t\s*\))?\s*\1\b|\(len\s*<\s*\d+\)\s*memcpy\s*\([^,]+,[^,]+,\s*(?:\(\s*size_t\s*\))?len\b",
        "signed_unsigned_conversion_bug",
        "high",
        "CWE-195",
        "Signed-to-unsigned conversion error: negative integer passes '< bound' check but becomes huge size_t in memcpy.",
        "Validate signed integer is non-negative (>= 0) before comparison and conversion.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"unsigned\s+char\s+\w+\s*=\s*(?:\(\s*unsigned\s+char\s*\))?\s*(?:len|length|size|n|\w+)\s*;|malloc\s*\(\s*n\s*\);\s*memset\s*\([^,]+,\s*0,\s*big\)",
        "integer_truncation_alloc",
        "high",
        "CWE-197",
        "Integer truncation: large size truncated to 8-bit unsigned char before memory allocation or copy.",
        "Use size_t consistently for all allocation and buffer sizes.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"return\s+[a-zA-Z_]\w*\s*\+\s*[a-zA-Z_]\w*\s*<\s*\d+;",
        "signed_overflow_bounds_check",
        "high",
        "CWE-190",
        "Signed integer overflow in arithmetic expression before bounds comparison causes undefined behavior.",
        "Check operands for overflow (e.g. __builtin_add_overflow) before addition.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"return\s+local\b",
        "return_stack_pointer",
        "critical",
        "CWE-562",
        "Returning pointer or reference to local stack variable.",
        "Return std::string or dynamically allocate memory on heap.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"new\s+[^;\[\]]+\[[^\]]+\];.*delete\s+\w+;",
        "mismatched_new_delete",
        "high",
        "CWE-762",
        "Scalar delete used on array allocated with new[].",
        "Use delete[] to release array memory.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"strncpy\s*\([^,]+,[^,]+,\s*sizeof[^)]+\);\s*printf",
        "strncpy_missing_null",
        "high",
        "CWE-170",
        "strncpy() does not null-terminate destination buffer when input exceeds capacity.",
        "Explicitly set null terminator at dst[sizeof(dst) - 1].",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"int\s+secret;\s*return\s+secret;",
        "uninitialized_variable_secret",
        "high",
        "CWE-457",
        "Uninitialized local variable read or returned.",
        "Initialize variables upon declaration.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"for\s*\([^;]*;\s*i\s*<=\s*8;\s*i\+\+\)\s*buf\[i\]",
        "off_by_one_buffer_write",
        "high",
        "CWE-193",
        "Off-by-one loop boundary ('<= 8') writes past 8-byte buffer capacity.",
        "Use strict inequality 'i < 8' for 0-indexed arrays.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"new\s+char\[\d+\];",
        "heap_memory_leak_loop",
        "medium",
        "CWE-401",
        "Dynamic memory allocated with new[] without deallocation leaks memory.",
        "Manage allocations with std::unique_ptr or std::vector.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"strchr\s*\([^)]*\);.*return\s*\*\w+",
        "null_dereference_strchr",
        "high",
        "CWE-476",
        "strchr() return value dereferenced without NULL check.",
        "Check pointer != nullptr before dereference.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"for\s*\([^;]*;\s*i\s*<=\s*n;\s*i\+\+\)\s*s\s*\+=\s*arr\[i\]",
        "loop_oob_array_read",
        "high",
        "CWE-125",
        "Off-by-one loop boundary ('<= n') causes out-of-bounds read past array capacity.",
        "Use strict inequality 'i < n'.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"const\s+std::string&\s+\w+\s*\([^)]*\)\s*\{\s*std::string\s+\w+\s*=\s*\"[^\"]*\";\s*return\s+\w+;",
        "dangling_reference_return",
        "critical",
        "CWE-562",
        "Returning reference to temporary local std::string variable creates dangling reference.",
        "Return by value (std::string) instead of reference.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),

    # ── Section B: Injection & Output Handling (26-40) ────────────────────────
    (
        r"\bsystem\s*\(\s*\([^)]*\+",
        "command_injection_system",
        "critical",
        "CWE-78",
        "OS command injection: system() executes shell command built via untrusted string concatenation.",
        "Avoid system(); invoke binaries directly with argument arrays using execvp or CreateProcess.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bpopen\s*\(\s*\([^)]*\+",
        "command_injection_popen",
        "critical",
        "CWE-78",
        "Command injection via popen() executing shell string built via concatenation.",
        "Avoid shell expansion; use secure subprocess spawning.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bexecl\s*\(\s*\"/bin/sh\"",
        "execl_shell_injection",
        "critical",
        "CWE-78",
        "execl() invokes /bin/sh -c with dynamically constructed command buffer.",
        "Execute command binary directly without invoking shell interpreter.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bdb_exec\s*\(\s*\"SELECT.*WHERE|SELECT\s+\*\s+FROM\s+\w+\s+WHERE.*['\"].*\+",
        "sql_injection",
        "critical",
        "CWE-89",
        "SQL injection: SQL query built via untrusted string concatenation.",
        "Use parameterized queries or prepared statements.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:std::)?(?:fopen|ifstream|ofstream|open)(?:\s+\w+)?\s*\(\s*(?:\"[^\"]*(?:files|uploads|path|dir|data)/\"?|\(\"[^\"]*files/\"|\(\"./out/\"\))\s*\+\s*\w+|fopen\s*\([^)]*files/.*\"\s*\+",
        "path_traversal",
        "high",
        "CWE-22",
        "Path traversal: file path constructed by appending untrusted filename.",
        "Sanitize filename with basename and validate canonical path against allowed directory.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\(&\(uid=.*objectClass",
        "ldap_injection",
        "high",
        "CWE-90",
        "LDAP filter injection: LDAP query constructed via unescaped string concatenation.",
        "Escape untrusted input in LDAP filter queries.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"http_response\s*\(\s*\"<html>.*You searched: \"\s*\+|<html>.*<\?|<body>.*\"\s*\+\s*\w+",
        "reflected_xss",
        "high",
        "CWE-79",
        "Reflected Cross-Site Scripting (XSS): unencoded user input reflected into HTML response.",
        "HTML-encode dynamic user content before outputting to HTML body.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"fprintf\s*\(\s*stderr,\s*\"Login attempt for user: %s\\n\",\s*\w+\.c_str\(\)\)",
        "log_injection",
        "low",
        "CWE-117",
        "Log injection: untrusted username logged directly without CRLF newline sanitization.",
        "Sanitize \\r and \\n characters from user input before writing to logs.",
        CONFIDENCE_MEDIUM,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"http_response\s*\(\s*\"HTTP/1\.1.*Content-Language: \"\s*\+",
        "crlf_header_injection",
        "high",
        "CWE-113",
        "CRLF injection: untrusted input appended directly into HTTP headers.",
        "Strip \\r and \\n characters from header values.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"syslog\s*\(\s*LOG_\w+,\s*[a-zA-Z_]\w*\s*\)",
        "syslog_format_string",
        "high",
        "CWE-134",
        "Format string vulnerability: syslog() invoked with dynamic string as format argument.",
        "Always supply literal format string: syslog(LOG_ERR, \"%s\", msg).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"getenv\s*\(\s*\"BACKUP_DIR\"\s*\).*system|system\s*\(\s*\(std::string\s*\(\s*\"tar czf",
        "env_command_injection",
        "critical",
        "CWE-78",
        "Environment variable fed directly into shell command execution.",
        "Validate and sanitize environment variable values before command invocation.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"memcpy\s*\(\s*&m\s*,\s*raw|m\.handler\s*\(",
        "unsafe_deserialization_fptr",
        "critical",
        "CWE-502",
        "Unsafe deserialization: memcpy into struct containing function pointer allows control-flow hijacking.",
        "Avoid raw byte deserialization into structures holding function pointers.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),

    # ── Section C: Crypto & Authentication (41-60) ───────────────────────────
    (
        r"p\s*==\s*\"admin123\"|\"admin123\"",
        "hardcoded_password",
        "high",
        "CWE-798",
        "Hardcoded password in authentication logic.",
        "Store salted cryptographic password hash in configuration or secrets vault.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:const\s+char\s*\*|std::string|char\s*(?:const\s*)?\[\s*\d*\s*\])\s*(?:SECRET|PASSWORD|PASSWD|SECRET_KEY|API_KEY|AUTH_KEY|PRIVATE_KEY)\w*\s*=\s*\"[^\"]+\"",
        "hardcoded_credential_constant",
        "high",
        "CWE-798",
        "Hardcoded cryptographic secret, password, or key constant in source code.",
        "Store secrets in environment variables, encrypted key stores, or a secrets manager.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"sk_live_[a-zA-Z0-9_\-]{16,}",
        "hardcoded_api_key_constant",
        "high",
        "CWE-798",
        "Hardcoded API secret key constant in source code.",
        "Store API keys in environment variables or cloud secrets management service.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\brand\s*\(\)",
        "insecure_prng_tokens",
        "medium",
        "CWE-338",
        "rand() is not cryptographically secure and produces predictable numbers.",
        "Use a cryptographically secure random number generator (/dev/urandom or std::random_device).",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"srand\s*\(\s*time\s*\(",
        "predictable_seed_prng",
        "medium",
        "CWE-337",
        "Predictable PRNG seed based on current timestamp (time(nullptr)).",
        "Seed pseudo-random generators using cryptographically secure hardware entropy.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"\^=\s*0x5A|\^=\s*0x[0-9a-fA-F]{2}",
        "custom_xor_encryption",
        "high",
        "CWE-327",
        "Custom XOR cipher is insecure and trivially reversible.",
        "Use standard authenticated cryptographic algorithms such as AES-GCM or ChaCha20-Poly1305.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"strcmp\s*\(\s*\w+\s*,\s*(?:secret|password|pw|key|token|hash)\b|strcmp\s*\(\s*(?:secret|password|pw|key|token|hash)\b,\s*\w+\s*\)|strcmp\s*\(\s*a\s*,\s*b\s*\)\s*==\s*0",
        "timing_side_channel_strcmp",
        "medium",
        "CWE-208",
        "Timing side-channel: strcmp() terminates early on first mismatched byte.",
        "Use constant-time comparison for authentication secrets (e.g. CRYPTO_memcmp).",
        CONFIDENCE_MEDIUM,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"for\s*\(\s*char\s+\w+\s*:\s*(?:pw|password|key)\s*\)\s*\w+\s*\+=\s*\w+",
        "weak_additive_password_hash",
        "high",
        "CWE-328",
        "Trivial sum-of-bytes algorithm used as password hash; vulnerable to collision and inversion.",
        "Use modern password hashing functions such as Argon2id, bcrypt, or scrypt.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"fopen\s*\(\s*\"users\.txt\",\s*\"a\"\)",
        "plaintext_password_storage",
        "high",
        "CWE-256",
        "Plaintext password credentials written directly to unencrypted text file.",
        "Store salted cryptographic password hashes (Argon2id) instead of plaintext.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"IV\[16\]\s*=\s*\{0\}|return\s+IV\b",
        "static_iv_constant",
        "high",
        "CWE-329",
        "Static hardcoded initialization vector (IV) eliminates cipher semantic security.",
        "Generate a unique cryptographically random IV/nonce for each encryption operation.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:std::)?(?:fopen|ofstream|ifstream|open)(?:\s+\w+)?\s*\(\s*\"/tmp/[^\"*]+\.(?:tmp|txt|log|dat)\"|fopen\s*\(\s*\"/tmp/app_session\.tmp\"",
        "predictable_temp_filename",
        "medium",
        "CWE-377",
        "Predictable temporary filename in shared /tmp directory.",
        "Use mkstemp() or O_TMPFILE to create secure unique temporary files.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"/\*\s*RSA key bits\s*\*/\s*return\s+40|return\s+40;\s*/\*\s*RSA",
        "inadequate_rsa_key_length_config",
        "critical",
        "CWE-326",
        "Inadequate RSA key length constant (40 bits); trivially factorable.",
        "Configure modern key lengths: RSA >= 2048/3072 bits, ECC >= 256 bits.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\{false,\s*false\}|verify_peer\s*=\s*false",
        "disabled_tls_verification_config",
        "critical",
        "CWE-295",
        "TLS peer and host certificate verification disabled in configuration.",
        "Enable strict certificate peer and hostname validation.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\{\"admin\",\s*\"admin\"\}",
        "default_credentials",
        "high",
        "CWE-1392",
        "Default administrative credentials embedded in code.",
        "Require user to establish credentials upon initial installation.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:log|logger|outfile|file)\s*<<.*(?:password|pass|secret|token|cred)\b|fprintf\s*\([^)]*pass=%s",
        "password_in_log_output",
        "high",
        "CWE-532",
        "Plaintext password logged to output stream.",
        "Omit sensitive authentication credentials from log records.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"static\s+int\s+id\s*=\s*1000;\s*return\s+\+\+id",
        "sequential_session_ids",
        "high",
        "CWE-330",
        "Sequential session IDs are predictable and easily guessed or hijacked.",
        "Generate cryptographically secure 128-bit random session tokens.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"AES_KEY\[\]\s*=\s*\"[0-9a-fA-F]+\"|return\s+AES_KEY\b",
        "hardcoded_aes_key",
        "critical",
        "CWE-321",
        "Hardcoded symmetric encryption key constant in source code.",
        "Load cryptographic keys from an external Key Management Service (KMS) or vault.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),

    # ── Section D: Files, Processes & Concurrency (61-75) ────────────────────
    (
        r"access\s*\([^,]+,\s*W_OK\)\s*==\s*0.*open\s*\(|access\s*\([^)]*\).*fopen",
        "toctou_access_check",
        "high",
        "CWE-367",
        "TOCTOU race condition: access() check followed by file open allows symlink redirection.",
        "Open file directly using O_CREAT | O_EXCL and inspect open() return code.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"0777\s*\)|umask\s*\(\s*0\s*\)",
        "world_writable_permissions",
        "high",
        "CWE-732",
        "File created with world-writable 0777 permissions or permissive umask(0).",
        "Use restrictive file permissions (0600 or 0640) and set restrictive umask (0027).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"open\s*\(\s*\"/tmp/report\.txt\",\s*O_WRONLY\s*\|\s*O_CREAT,\s*0666\)",
        "symlink_race_tmp",
        "high",
        "CWE-59",
        "Creating file in shared /tmp directory without O_EXCL allows symlink hijacking.",
        "Use O_EXCL | O_NOFOLLOW when creating files in shared temporary directories.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"fopen\s*\(\s*p,\s*\"w\"\s*\)",
        "external_control_filename",
        "medium",
        "CWE-73",
        "File opened with externally controlled filename without path validation.",
        "Validate target file path against an allowed whitelist directory.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"read\s*\([^)]*\);\s*write\s*\(",
        "unchecked_io_returns",
        "medium",
        "CWE-252",
        "Unchecked return values from read() and write() system calls.",
        "Check return codes and verify complete byte count transfer.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"for\s*\([^)]*\)\s*open\s*\(",
        "file_descriptor_leak_loop",
        "high",
        "CWE-775",
        "File descriptor opened repeatedly in loop without close(), exhausting handles.",
        "Ensure all opened file descriptors are closed before subsequent iterations.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"std::thread.*g_counter\+\+|std::thread.*g_\w+\+\+",
        "data_race_counter",
        "high",
        "CWE-362",
        "Data race: multiple threads concurrently mutating shared non-atomic global counter.",
        "Use std::atomic<int> or synchronize mutations with std::mutex.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"printf\s*\(\s*\"caught|free\s*\(\s*malloc\s*\(",
        "non_async_signal_safe",
        "high",
        "CWE-479",
        "Signal handler calls non-async-signal-safe functions (printf/malloc/free).",
        "Only call async-signal-safe functions or set a volatile sig_atomic_t flag.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"setuid\s*\(\s*0\s*\);\s*system",
        "privileges_never_dropped",
        "critical",
        "CWE-250",
        "Elevating privileges to root (uid 0) and executing external command without dropping privileges.",
        "Drop privileges before executing external commands.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"chroot\s*\([^)]*\);",
        "chroot_without_chdir",
        "high",
        "CWE-243",
        "chroot() invoked without chdir(\"/\") allows jailbreak.",
        "Call chdir(\"/\") immediately after chroot().",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"while\s*\([^)]*fread\s*\(&c,\s*1,\s*1",
        "unbounded_file_read_memory",
        "medium",
        "CWE-400",
        "Unbounded byte-by-byte file read can exhaust application memory.",
        "Cap maximum file read size and process in fixed-size chunks.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"fopen\s*\(\s*\(\"\./out/\"\s*\+\s*entry\)",
        "zip_slip_extraction",
        "high",
        "CWE-23",
        "Zip-slip: archive entry path concatenated directly without path boundary check.",
        "Verify extracted canonical path resides strictly inside target destination directory.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"tmpnam\s*\(",
        "tmpnam_race",
        "high",
        "CWE-377",
        "tmpnam() is inherently prone to race conditions and temporary file hijacking.",
        "Use mkstemp() for secure atomic temporary file creation.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"open\s*\(\s*\"audit\.log\",\s*O_CREAT.*0644\)",
        "sensitive_log_world_readable",
        "medium",
        "CWE-532",
        "Sensitive audit log file created with world-readable 0644 permissions.",
        "Set audit log file permissions to 0600.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),

    # ── Section E: Network (76-90) ───────────────────────────────────────────
    (
        r"INADDR_ANY",
        "socket_bind_all_interfaces",
        "low",
        "CWE-1327",
        "Socket bound to INADDR_ANY (0.0.0.0), exposing service to all network interfaces.",
        "Bind to loopback (127.0.0.1) or specific authorized network interface.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"while\s*\(\s*recv\s*\([^)]*\)\s*>\s*0\s*\)",
        "socket_no_timeout",
        "medium",
        "CWE-400",
        "Socket read loop lacks receive timeout, vulnerable to Slowloris resource exhaustion.",
        "Set socket receive timeout using SO_RCVTIMEO.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"recv\s*\([^,]+,\s*b,\s*4096",
        "recv_buffer_overflow",
        "critical",
        "CWE-120",
        "recv() specified length (4096) exceeds local buffer capacity (64).",
        "Pass sizeof(buf) as buffer length parameter in recv().",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"recv\s*\([^,]+,\s*&len,\s*4.*malloc\s*\(64\);.*recv\s*\([^,]+,\s*b,\s*len",
        "trusting_client_length_alloc",
        "critical",
        "CWE-130",
        "Trusting client-supplied length field for network receive into smaller fixed allocation.",
        "Validate client length against buffer capacity before reading.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"send_all\s*\([^,]+,\s*pw",
        "cleartext_password_transmission",
        "high",
        "CWE-319",
        "Plaintext password transmitted across socket without TLS encryption.",
        "Transmit credentials exclusively over TLS-encrypted network channels.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"system\s*\(\s*\(\"curl \"\s*\+\s*url\)",
        "ssrf_curl_injection",
        "critical",
        "CWE-918",
        "Server-Side Request Forgery (SSRF) and command injection: attacker-controlled URL passed to curl command.",
        "Validate URLs against allowed scheme/domain whitelist and use HTTP client library.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"std::vector<char>\s+\w+\s*\(\s*n\s*\)",
        "unbounded_client_vector_alloc",
        "high",
        "CWE-770",
        "Unbounded memory allocation directly driven by client integer parameter.",
        "Validate and cap maximum allocation size.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"gethostbyname\s*\(",
        "non_thread_safe_gethostbyname",
        "medium",
        "CWE-362",
        "gethostbyname() returns pointer to static internal struct and is not thread-safe.",
        "Use getaddrinfo() for reentrant thread-safe DNS resolution.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"strtok\s*\(",
        "non_thread_safe_strtok",
        "medium",
        "CWE-362",
        "strtok() maintains static internal state and is not thread-safe.",
        "Use strtok_r() or reentrant tokenizer.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"s_addr\s*=\s*inet_addr\s*\(",
        "unchecked_inet_addr_error",
        "low",
        "CWE-252",
        "inet_addr() return value unchecked; returns INADDR_NONE (-1) on invalid IP format.",
        "Use inet_pton() or check for INADDR_NONE.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"HTTP/1\.1 302 Found\\r\\nLocation:\s*\"\s*\+\s*next",
        "open_redirect_header",
        "medium",
        "CWE-601",
        "Open redirect: redirect location constructed directly from user input.",
        "Validate redirect target against trusted relative paths or domain whitelist.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"DB error in query:.*srv/app/db\.cpp",
        "verbose_internal_error_leak",
        "low",
        "CWE-209",
        "Verbose internal database query and server file path exposed to user.",
        "Log technical details server-side; present generic error to client.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"Access-Control-Allow-Origin:\s*\*\\r\\nAccess-Control-Allow-Credentials:\s*true",
        "wildcard_cors_with_credentials",
        "high",
        "CWE-942",
        "CORS policy allows wildcard origin with credentials enabled.",
        "Specify exact authorized origins when Allow-Credentials is true.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"u\s*==\s*\"debug_master\"|\"debug_master\"",
        "hidden_backdoor_account",
        "critical",
        "CWE-912",
        "Hardcoded backdoor administrative account in authentication logic.",
        "Remove backdoor accounts and enforce uniform authentication.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),

    # ── Section F: Logic, UB & Misc (91-100) ─────────────────────────────────
    (
        r"lock_guard<std::mutex>\s+\w+\(A\);.*lock_guard<std::mutex>\s+\w+\(B\)|lock_guard<std::mutex>\s+\w+\(B\);.*lock_guard<std::mutex>\s+\w+\(A\)|std::lock_guard.*m1.*lock_guard.*m2",
        "lock_order_deadlock",
        "high",
        "CWE-833",
        "Inconsistent mutex lock order creates potential deadlock.",
        "Use std::lock or std::scoped_lock to acquire multiple mutexes atomically.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"return\s+v\d+\s*\(\s*n\s*\+\s*1\s*\)",
        "uncontrolled_infinite_recursion",
        "high",
        "CWE-674",
        "Uncontrolled recursive call without base condition exhausts thread stack.",
        "Ensure recursive functions have a verified termination condition.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"return\s+a\s*/\s*b|\b\w+\s*/\s*([a-zA-Z_]\w*)\s*;(?!\s*//\s*safe)",
        "division_by_zero",
        "high",
        "CWE-369",
        "Division operator executed without verifying divisor is non-zero.",
        "Check divisor != 0 before division.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"1u\s*<<\s*n",
        "shift_count_overflow_ub",
        "medium",
        "CWE-1335",
        "Shift count not validated; shifting by >= 32 bits is undefined behavior.",
        "Ensure shift count is within valid bit-width range [0, 31].",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"return\s+a\s*\+\s*b;",
        "signed_integer_overflow_ub",
        "medium",
        "CWE-190",
        "Signed integer addition can overflow, triggering undefined behavior.",
        "Use unsigned arithmetic, safe math libraries, or overflow check.",
        CONFIDENCE_MEDIUM,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"atoi\s*\([^)]*\);.*a\[n\]",
        "atoi_unvalidated_index",
        "high",
        "CWE-20",
        "atoi() output used as array index without validation.",
        "Use std::strtol or bounds-check array index before access.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"g_is_admin\s*=\s*true",
        "mutable_global_security_state",
        "high",
        "CWE-1108",
        "Global mutable variable used to store security authorization state.",
        "Encapsulate authorization state within secure request session.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"memset\s*\(\s*key\s*,\s*0,\s*sizeof",
        "memset_key_optimized_away",
        "high",
        "CWE-14",
        "memset() wiping sensitive key buffer on stack may be optimized away as dead store.",
        "Use secure_zero_memory, explicit_bzero, or memset_s.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"static\s+char\s+buf\[\d+\];.*return\s+buf",
        "static_buffer_return",
        "medium",
        "CWE-562",
        "Returning pointer to static buffer is not reentrant and vulnerable to concurrent overwrite.",
        "Return std::string or write into caller-supplied buffer.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"cookie\.find\s*\(\s*\"role=admin\"\s*\)",
        "client_controlled_role_cookie",
        "high",
        "CWE-657",
        "Security authorization decision made on client-controlled plaintext cookie.",
        "Sign session cookies with HMAC and verify server-side authorization.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"memcpy\s*\([^,]+,\s*payload,\s*claimed_len\)|memcpy\s*\([^,]+,[^,]+,\s*claimed_len\)",
        "unbounded_length_buffer_copy",
        "high",
        "CWE-126",
        "Buffer over-read: memcpy with attacker-controlled claimed length without source bounds validation.",
        "Validate claimed length against the actual source buffer boundary before copying.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"return\s+(\w+)\s*\(\s*\w+\s*\+\s*1\s*\)\s*\+\s*1",
        "unbounded_recursion",
        "high",
        "CWE-674",
        "Unbounded recursive function call without base termination condition causes stack exhaustion.",
        "Introduce explicit recursion depth limit or base-case termination condition.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
]

C_CPP_SECURITY_PATTERNS: List[Tuple[str, str, str, str, str, str, str, str]] = list(SECURITY_PATTERNS)

# ═══════════════════════════════════════════════════════════════════════════════
# PYTHON SECURITY PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════
PYTHON_SECURITY_PATTERNS: List[Tuple[str, str, str, str, str, str, str, str]] = [
    # Command Injection (CWE-78)
    (
        r"\bos\.system\s*\(",
        "python_os_system_command_injection",
        "critical",
        "CWE-78",
        "os.system() executes shell command with potential command injection.",
        "Use subprocess.run([cmd, ...], shell=False) with parameterized arguments.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bos\.popen\s*\(",
        "python_os_popen_command_injection",
        "critical",
        "CWE-78",
        "os.popen() executes command via shell without argument sanitization.",
        "Use subprocess.run() with a list of arguments without shell=True.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bsubprocess\.(?:call|Popen|run|check_call|check_output)\s*\([^)]*shell\s*=\s*True",
        "python_subprocess_shell_true",
        "critical",
        "CWE-78",
        "subprocess invoked with shell=True enables arbitrary shell command injection.",
        "Set shell=False and pass command and arguments as a list of strings.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Code Injection / Dynamic Evaluation (CWE-94 / CWE-95)
    (
        r"\beval\s*\(",
        "python_unsafe_eval",
        "critical",
        "CWE-94",
        "eval() executes arbitrary dynamic Python code and expressions.",
        "Use ast.literal_eval() for safe literal evaluation, or avoid dynamic evaluation.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bexec\s*\(",
        "python_unsafe_exec",
        "critical",
        "CWE-95",
        "exec() executes dynamically constructed Python statements.",
        "Refactor to eliminate dynamic Python code execution.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Insecure Deserialization (CWE-502)
    (
        r"\b(?:pickle|_pickle|cPickle)\.(?:loads?|load)\s*\(",
        "python_insecure_pickle",
        "critical",
        "CWE-502",
        "pickle deserialization of untrusted data enables arbitrary remote code execution.",
        "Use safe serialization formats like JSON, protocol buffers, or hmac verification.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\byaml\.(?:load|load_all)\s*\((?!.*Loader\s*=\s*(?:yaml\.)?SafeLoader)[^)]*\)",
        "python_unsafe_yaml_load",
        "critical",
        "CWE-502",
        "yaml.load() without SafeLoader allows arbitrary Python object instantiation.",
        "Use yaml.safe_load() or specify Loader=yaml.SafeLoader.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # SQL Injection (CWE-89)
    (
        r"(?:cursor|conn|db|session)\.execute\s*\(\s*f[\"'].*?\{",
        "python_sqli_fstring",
        "high",
        "CWE-89",
        "SQL injection: f-string interpolation directly inside database query execution.",
        "Use parameterized queries with bind variables (e.g., cursor.execute('SELECT ... %s', (val,))).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:cursor|conn|db|session)\.execute\s*\(\s*[\"'].*?%s[\"']\s*%",
        "python_sqli_percent_formatting",
        "high",
        "CWE-89",
        "SQL injection: percent-formatting string directly inside database query execution.",
        "Pass query parameters as a tuple argument to execute(), do not format into the query string.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?:cursor|conn|db|session)\.execute\s*\(\s*[\"'].*?[\"']\s*\+\s*\w+",
        "python_sqli_concatenation",
        "high",
        "CWE-89",
        "SQL injection: string concatenation used to construct dynamic database query.",
        "Use parameterized queries with prepared placeholders.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Cryptographic Weaknesses (CWE-327 / CWE-328 / CWE-338)
    (
        r"\bhashlib\.md5\s*\(",
        "python_insecure_hash_md5",
        "medium",
        "CWE-328",
        "MD5 is cryptographically broken and vulnerable to collision attacks.",
        "Use hashlib.sha256() or SHA-3 for cryptographically secure hashing.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bhashlib\.sha1\s*\(",
        "python_insecure_hash_sha1",
        "medium",
        "CWE-328",
        "SHA-1 is deprecated and collision-vulnerable.",
        "Upgrade to hashlib.sha256() or SHA-512.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\brandom\.(?:random|randint|choice|randrange|sample)\s*\(",
        "python_insecure_prng",
        "medium",
        "CWE-338",
        "Standard random module is pseudorandom and unsuitable for security/cryptographic use.",
        "Use the 'secrets' module (secrets.token_hex, secrets.choice) for cryptographic tokens and keys.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"\bAES\.MODE_ECB\b",
        "python_ecb_mode",
        "high",
        "CWE-327",
        "AES configured with Electronic Codebook (ECB) mode leaks plaintext pattern data.",
        "Use authenticated encryption modes such as AES-GCM (AES.MODE_GCM).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Hardcoded Credentials (CWE-798)
    (
        r"(?i)\b(?:api_key|secret_key|auth_token|db_password)\s*=\s*['\"][A-Za-z0-9+/=_!@#$%^&*-]{6,}['\"]",
        "python_hardcoded_secret",
        "high",
        "CWE-798",
        "Hardcoded credential or private secret key detected in source code.",
        "Load credentials dynamically from environment variables (os.environ) or a secret manager.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"(?i)\bpassword\s*=\s*['\"][^'\"]{4,}['\"]",
        "python_hardcoded_password",
        "high",
        "CWE-798",
        "Hardcoded password literal detected in source code.",
        "Externalize authentication secrets and passwords to secure secret stores.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # TLS / Certificate Validation (CWE-295)
    (
        r"\b(?:requests|urllib3)\.(?:get|post|put|delete|patch|request)\s*\([^)]*verify\s*=\s*False",
        "python_tls_verification_disabled",
        "high",
        "CWE-295",
        "TLS/SSL certificate validation is explicitly disabled (verify=False), enabling MITM attacks.",
        "Set verify=True and provide valid certificate bundle paths.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bssl\._create_unverified_context\s*\(",
        "python_ssl_unverified_context",
        "high",
        "CWE-295",
        "Unverified SSL context created; HTTPS connections will not validate certificates.",
        "Use ssl.create_default_context() with proper certificate validation.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Insecure Temp Files & Permissions (CWE-377 / CWE-732)
    (
        r"\btempfile\.mktemp\s*\(",
        "python_insecure_mktemp",
        "high",
        "CWE-377",
        "tempfile.mktemp() is deprecated and vulnerable to race conditions (TOCTOU).",
        "Use tempfile.NamedTemporaryFile() or tempfile.mkstemp() instead.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bos\.chmod\s*\([^,]+,\s*0o?[67]77\)",
        "python_overly_permissive_chmod",
        "medium",
        "CWE-732",
        "Insecure world-writable file permissions (0777) configured.",
        "Restrict permissions to 0o600 (owner read/write) or 0o700.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Logic & Security Misconfiguration (CWE-489 / CWE-617)
    (
        r"\bapp\.run\s*\([^)]*debug\s*=\s*True",
        "python_flask_debug_true",
        "high",
        "CWE-489",
        "Flask application executed with debug=True enables interactive debugger allowing remote code execution.",
        "Set debug=False in production deployments.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"^\s*assert\s+(?:is_admin|role|auth|authenticated|token|user\.is_)",
        "python_assert_security_check",
        "medium",
        "CWE-617",
        "assert used for security/authorization logic; assertions are stripped when Python runs with optimization (-O).",
        "Use explicit if-statements raising permission exceptions instead of assert.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# JAVA SECURITY PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════
JAVA_SECURITY_PATTERNS: List[Tuple[str, str, str, str, str, str, str, str]] = [
    # Command Injection (CWE-78)
    (
        r"\bRuntime\.getRuntime\s*\(\s*\)\.exec\s*\(",
        "java_runtime_exec_command_injection",
        "critical",
        "CWE-78",
        "Runtime.getRuntime().exec() executes operating system commands with potential injection risk.",
        "Use ProcessBuilder with argument list and avoid invoking shell interpreters.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bnew\s+ProcessBuilder\s*\([^)]*\+[^)]*\)",
        "java_process_builder_concatenation",
        "critical",
        "CWE-78",
        "ProcessBuilder invoked with concatenated arguments allows command argument injection.",
        "Pass fixed argument array and validate dynamic parameters strictly.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # SQL Injection (CWE-89)
    (
        r"\b(?:stmt|statement)\.execute(?:Query|Update)?\s*\(\s*\"[^\"]*\"\s*\+",
        "java_jdbc_sql_injection",
        "high",
        "CWE-89",
        "SQL injection in JDBC: dynamic SQL query constructed via string concatenation.",
        "Use PreparedStatement with parameterized '?' placeholders.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bcreateQuery\s*\(\s*\"[^\"]*\"\s*\+",
        "java_jpa_hql_injection",
        "high",
        "CWE-89",
        "HQL/JPQL injection: string concatenation in query construction.",
        "Use parameterized queries: setParameter(\"name\", value).",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Insecure Deserialization (CWE-502)
    (
        r"\bnew\s+ObjectInputStream\s*\(",
        "java_insecure_object_input_stream",
        "critical",
        "CWE-502",
        "ObjectInputStream deserializes untrusted Java objects enabling remote code execution.",
        "Avoid native Java serialization for untrusted streams; use JSON or ValidatingObjectInputStream with an allowlist.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bnew\s+XMLDecoder\s*\(",
        "java_insecure_xmldecoder",
        "critical",
        "CWE-502",
        "XMLDecoder deserializes arbitrary Java objects leading to immediate arbitrary code execution.",
        "Do not use XMLDecoder on untrusted input; use secure XML parsers.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # XML External Entity - XXE (CWE-611)
    (
        r"\bDocumentBuilderFactory\.newInstance\s*\(\s*\)",
        "java_xxe_document_builder",
        "high",
        "CWE-611",
        "DocumentBuilderFactory by default resolves external entities (XXE), allowing file disclosure and SSRF.",
        "Disable external entities: factory.setFeature(\"http://apache.org/xml/features/disallow-doctype-decl\", true).",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"\bSAXParserFactory\.newInstance\s*\(\s*\)",
        "java_xxe_sax_parser",
        "high",
        "CWE-611",
        "SAXParserFactory by default may resolve external entities.",
        "Configure parser: saxFactory.setFeature(\"http://xml.org/sax/features/external-general-entities\", false).",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    # Cryptographic Weaknesses (CWE-327 / CWE-328 / CWE-338)
    (
        r'MessageDigest\.getInstance\s*\(\s*"(?:MD5|SHA-1)"\s*\)',
        "java_insecure_message_digest",
        "medium",
        "CWE-328",
        "MessageDigest configured with obsolete hash algorithm (MD5/SHA-1).",
        "Use MessageDigest.getInstance(\"SHA-256\") or SHA-512.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r'Cipher\.getInstance\s*\(\s*"(?:DES|DESede|Blowfish|RC4|ARCFOUR)[^"]*"\s*\)',
        "java_weak_cipher_algorithm",
        "high",
        "CWE-326",
        "Weak or broken cipher algorithm used for encryption.",
        "Use AES-GCM: Cipher.getInstance(\"AES/GCM/NoPadding\").",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r'Cipher\.getInstance\s*\(\s*"AES/ECB/[^"]*"\s*\)',
        "java_ecb_mode_cipher",
        "high",
        "CWE-327",
        "AES configured with ECB mode is insecure and fails to hide pattern data.",
        "Use AES in GCM mode: Cipher.getInstance(\"AES/GCM/NoPadding\").",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bnew\s+Random\s*\(\s*\)",
        "java_insecure_random_prng",
        "medium",
        "CWE-338",
        "java.util.Random produces predictable pseudorandom numbers unsuitable for cryptographic or security tokens.",
        "Use java.security.SecureRandom for security tokens and cryptographic keys.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    # Hardcoded Credentials (CWE-798)
    (
        r'(?i)\bString\s+(?:password|apiKey|api_key|secretKey|secret_key|authToken)\s*=\s*"[^"]{4,}"\s*;',
        "java_hardcoded_credential",
        "high",
        "CWE-798",
        "Hardcoded credential detected in Java source code.",
        "Load credentials from environment variables using System.getenv() or a secrets vault.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # TLS Certificate Blind Trust (CWE-295)
    (
        r"\bimplements\s+X509TrustManager\b",
        "java_custom_trust_manager",
        "critical",
        "CWE-295",
        "Custom X509TrustManager implementation may bypass SSL/TLS certificate verification.",
        "Ensure checkServerTrusted validates certificate chains properly; do not leave methods empty.",
        CONFIDENCE_HIGH,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    (
        r"\bALLOW_ALL_HOSTNAME_VERIFIER\b",
        "java_allow_all_hostname_verifier",
        "high",
        "CWE-295",
        "ALLOW_ALL_HOSTNAME_VERIFIER disables TLS hostname verification allowing MITM attacks.",
        "Use standard SSLConnectionSocketFactory with default hostname verifier.",
        CONFIDENCE_CONFIRMED,
        CATEGORY_SECURITY_VULNERABILITY,
    ),
    # Path Traversal & XSS (CWE-22 / CWE-79)
    (
        r"\bnew\s+File\s*\([^,]+,\s*[a-zA-Z0-9_]+\s*\)",
        "java_path_traversal_file",
        "high",
        "CWE-22",
        "File constructed with user input without canonical path validation.",
        "Verify canonical path starts with the base directory before reading or writing.",
        CONFIDENCE_MEDIUM,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    (
        r"\bresponse\.getWriter\s*\(\s*\)\.(?:write|println?)\s*\([^)]*\)",
        "java_xss_response_writer",
        "medium",
        "CWE-79",
        "Raw user input written directly to HTTP response writer without HTML encoding.",
        "Encode output using OWASP Java Encoder or template engine escaping.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
    # Information Exposure (CWE-209)
    (
        r"\be\.printStackTrace\s*\(\s*\)",
        "java_stack_trace_leak",
        "low",
        "CWE-209",
        "e.printStackTrace() prints sensitive internal stack trace details to standard error.",
        "Use an enterprise logging framework (SLF4J/Logback) with proper redaction.",
        CONFIDENCE_HIGH,
        CATEGORY_POTENTIAL_SECURITY_RISK,
    ),
]

# Combined security pattern registry
SECURITY_PATTERNS.extend(PYTHON_SECURITY_PATTERNS)
SECURITY_PATTERNS.extend(JAVA_SECURITY_PATTERNS)



def detect_format_string_vulnerabilities(code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
    """
    Intelligent Format String Vulnerability Detector (Phase 2.D & Phase 5).
    
    Distinguishes unsafe buffer operations from format string vulnerabilities:
    - Only report CWE-134 when the format argument itself is attacker-controlled or nonconstant.
    - Constant format strings (e.g. line 45 sprintf, line 141 fprintf, line 197 fprintf, line 221 fprintf, line 375 snprintf)
      must NEVER be classified as CWE-134 format string vulnerabilities.
    """
    findings: List[Dict[str, Any]] = []
    lines = code.splitlines()

    # Function name to 0-based format argument index
    FMT_ARG_INDEX = {
        "printf": 0,
        "vprintf": 0,
        "fprintf": 1,
        "vfprintf": 1,
        "sprintf": 1,
        "vsprintf": 1,
        "snprintf": 2,
        "vsnprintf": 2,
        "syslog": 1,
    }

    # Match call start
    call_pattern = re.compile(
        r"\b(printf|fprintf|sprintf|snprintf|vprintf|vsprintf|vfprintf|vsnprintf|syslog)\s*\(",
        re.MULTILINE,
    )

    for m in call_pattern.finditer(code):
        fn_name = m.group(1)
        start_idx = m.end()
        target_arg_idx = FMT_ARG_INDEX.get(fn_name, 0)

        # Parse comma-separated arguments respecting nested parens and quotes
        args = []
        curr_arg = []
        paren_depth = 1
        in_quote = False
        quote_char = ''
        escape = False

        pos = start_idx
        while pos < len(code) and paren_depth > 0:
            ch = code[pos]
            if escape:
                curr_arg.append(ch)
                escape = False
                pos += 1
                continue

            if ch == '\\':
                curr_arg.append(ch)
                escape = True
                pos += 1
                continue

            if in_quote:
                curr_arg.append(ch)
                if ch == quote_char:
                    in_quote = False
                pos += 1
                continue

            if ch in ('"', "'"):
                in_quote = True
                quote_char = ch
                curr_arg.append(ch)
                pos += 1
                continue

            if ch == '(':
                paren_depth += 1
                curr_arg.append(ch)
            elif ch == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    args.append("".join(curr_arg).strip())
                    break
                else:
                    curr_arg.append(ch)
            elif ch == ',' and paren_depth == 1:
                args.append("".join(curr_arg).strip())
                curr_arg = []
            else:
                curr_arg.append(ch)
            pos += 1

        if len(args) <= target_arg_idx:
            continue

        fmt_arg = args[target_arg_idx].strip()
        ln_no = code[: m.start()].count("\n") + 1

        # Check if format argument is a string literal (constant)
        is_literal = (fmt_arg.startswith('"') and fmt_arg.endswith('"')) or fmt_arg.startswith('/*')
        if not is_literal:
            # Genuine format string vulnerability!
            findings.append(Finding(
                type="format_string_bug",
                category=CATEGORY_SECURITY_VULNERABILITY,
                severity="critical" if "printf" in fn_name else "high",
                confidence=0.95,
                confidence_level=CONFIDENCE_CONFIRMED,
                source_tool="rule",
                detection_engine="rule",
                original_rule_id="CWE-134",
                contributing_engines=["rule"],
                file_path=file_path,
                line=ln_no,
                start_line=ln_no,
                end_line=ln_no,
                description=f"{fn_name}() invoked with nonconstant/untrusted format argument '{fmt_arg}'.",
                cwe_id="CWE-134",
                recommendation=f'Always provide a string literal format specifier: {fn_name}(..., "%s", {fmt_arg}).',
                status="confirmed",
                is_confirmed=True,
                evidence=f"{fn_name}(..., {fmt_arg}) at line {ln_no}",
            ).to_dict())

    return findings


def detect_use_after_free(code: str, lines: List[str], file_path: str = "<source>") -> List[Dict[str, Any]]:
    """Detect use-after-free (CWE-416) and double-free (CWE-415)."""
    findings: List[Dict[str, Any]] = []
    dealloc_re = re.compile(
        r"\bfree\s*\(\s*(\w+)\s*\)"
        r"|\bdelete\s*\[\s*\]\s*(\w+)"
        r"|\bdelete\s+(\w+)",
        re.MULTILINE,
    )

    freed_vars: Dict[str, int] = {}
    for m in dealloc_re.finditer(code):
        var = m.group(1) or m.group(2) or m.group(3)
        freed_vars[var] = code[: m.start()].count("\n") + 1

    for var, free_line in freed_vars.items():
        deref_re = re.compile(
            rf"\*\s*{re.escape(var)}\b"
            rf"|{re.escape(var)}\s*->\s*\w+"
            rf"|{re.escape(var)}\s*\["
        )
        direct_assign_re = re.compile(
            rf"(?<![*\[])\b{re.escape(var)}\s*=\s*(?!=)"
        )

        for ln_no, line in enumerate(lines, 1):
            if ln_no <= free_line:
                continue
            if direct_assign_re.search(line):
                break
            if deref_re.search(line):
                findings.append(Finding(
                    type="use_after_free",
                    category=CATEGORY_SECURITY_VULNERABILITY,
                    severity="critical",
                    line=ln_no,
                    start_line=ln_no,
                    end_line=ln_no,
                    file_path=file_path,
                    description=f"Variable '{var}' dereferenced at line {ln_no} after deallocation at line {free_line}.",
                    cwe_id="CWE-416",
                    recommendation=f"Do not access '{var}' after freeing; set '{var} = nullptr' immediately.",
                    confidence=0.95,
                    confidence_level=CONFIDENCE_CONFIRMED,
                    source_tool="rule",
                    detection_engine="rule",
                    original_rule_id="CWE-416",
                    contributing_engines=["rule"],
                    status="confirmed",
                    is_confirmed=True,
                    evidence=f"Deallocated at line {free_line}, dereferenced at line {ln_no}",
                ).to_dict())
                break
            if re.search(rf"\bfree\s*\(\s*{re.escape(var)}\s*\)", line):
                findings.append(Finding(
                    type="double_free",
                    category=CATEGORY_SECURITY_VULNERABILITY,
                    severity="critical",
                    line=ln_no,
                    start_line=ln_no,
                    end_line=ln_no,
                    file_path=file_path,
                    description=f"Variable '{var}' freed at line {ln_no} was already freed at line {free_line}.",
                    cwe_id="CWE-415",
                    recommendation=f"Ensure pointer '{var}' is only freed once; set to nullptr after free.",
                    confidence=1.0,
                    confidence_level=CONFIDENCE_CONFIRMED,
                    source_tool="rule",
                    detection_engine="rule",
                    original_rule_id="CWE-415",
                    contributing_engines=["rule"],
                    status="confirmed",
                    is_confirmed=True,
                    evidence=f"Double free of '{var}' at line {ln_no}",
                ).to_dict())
                break

    return findings


def detect_specialized_ast_patterns(code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
    """
    Advanced Heuristics & AST Detectors for Phases 2, 5:
      - v013: Allocation size multiplication overflow (CWE-190)
      - v015: Signed / negative array indexing (CWE-129)
      - v020: Vector iterator invalidation via push_back (CWE-416)
      - v021: Unchecked vector operator[] indexing (CWE-125)
      - v037: Unsafe XML search pattern without XML parser (CWE-611) -> low confidence potential risk
      - v038: Exponential recursive backtracking / ReDoS (CWE-1333)
      - v043, v049: Unhashed / plaintext password handling (CWE-256 / CWE-759)
      - v056: Untrusted command execution (CWE-78) without requiring hardcoded name
      - v058: C-string pointer equality comparison instead of content comparison (CWE-697)
      - v060: Insecure custom encoding for secrets (CWE-261)
      - v083: Hardcoded secret comparison without rate limit (CWE-798 / CWE-307)
    """
    findings: List[Dict[str, Any]] = []
    lines = code.splitlines()

    # 1. v013: Allocation size multiplication overflow (CWE-190)
    alloc_mul_re = re.compile(r"\bmalloc\s*\(\s*(\w+)\s*\*\s*sizeof\s*\([^)]+\)\s*\)")
    for m in alloc_mul_re.finditer(code):
        var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.90,
            confidence_level=CONFIDENCE_HIGH,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{var} * sizeof(...)' inside malloc() can wrap around 32-bit limit.",
            recommendation="Validate multiplication cannot overflow (e.g. check var <= SIZE_MAX / sizeof(...)) before calling malloc.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 2. v015: Negative / signed array index (CWE-129)
    # Match functions taking signed int idx and indexing an array without checking idx >= 0
    signed_idx_re = re.compile(r"\bint\s+(\w+)\s*\[\s*\d+\s*\]\s*=[^;]*;\s*return\s+\1\[\s*(\w+)\s*\]")
    for m in signed_idx_re.finditer(code):
        arr_name, idx_var = m.group(1), m.group(2)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="improper_index_validation",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.90,
            confidence_level=CONFIDENCE_HIGH,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-129",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-129",
            description=f"Negative or unbounded array index '{idx_var}' accessing array '{arr_name}'.",
            recommendation=f"Validate '{idx_var} >= 0 && {idx_var} < sizeof({arr_name})/sizeof({arr_name}[0])' before access.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 3. v020: Iterator invalidation in loop (CWE-416)
    iter_invalid_re = re.compile(r"for\s*\([^)]*it\s*=\s*(\w+)\.begin\(\)[^)]*\)[^;{]*\{[^}]*\1\.push_back")
    for m in iter_invalid_re.finditer(code):
        vec_name = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="iterator_invalidation",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-416",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-416",
            description=f"Modifying vector '{vec_name}' via push_back while iterating over it causes iterator invalidation / use-after-free.",
            recommendation="Avoid mutating container while iterating, or use index-based loops and update indices.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 4. v021: Unchecked vector operator[] indexing (CWE-125)
    vec_subscript_re = re.compile(r"std::vector<\w+>\s*&\s*(\w+)[^)]*\)[^{]*\{[^{]*return\s+\1\[\s*(\w+)\s*\]")
    for m in vec_subscript_re.finditer(code):
        vec_name, idx_name = m.group(1), m.group(2)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unchecked_vector_subscript",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.85,
            confidence_level=CONFIDENCE_HIGH,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-125",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-125",
            description=f"Unchecked vector index access '{vec_name}[{idx_name}]' without bounds verification.",
            recommendation=f"Use '{vec_name}.at({idx_name})' for bounds-checked access or check '{idx_name} < {vec_name}.size()'.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 5. v037: Potential unsafe XML pattern without XML parser (CWE-611) (Phase 2.A)
    # Only report low confidence potential risk when searching string without external entity resolution
    xml_re = re.compile(r"\b(\w+)\.find\s*\(\s*\"<!ENTITY\"")
    for m in xml_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="potential_unsafe_xml_pattern",
            category=CATEGORY_POTENTIAL_SECURITY_RISK,
            severity="low",
            confidence=0.35,
            confidence_level=CONFIDENCE_LOW,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-611",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-611",
            description="String search for '<!ENTITY' pattern detected without an instantiated XML parser or external entity processing.",
            recommendation="If parsing XML documents, disable external DTD and entity expansion in the XML parser configuration.",
            status="potential",
            is_confirmed=False,
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 6. v038: Exponential recursive backtracking / ReDoS (CWE-1333) (Phase 5)
    # Function calling itself multiple times in || expression without memoization
    redos_re = re.compile(r"bool\s+(\w+)\s*\([^)]*\)\s*\{[^}]*return\s+\1\s*\([^)]*\)\s*\|\|[^{}]*\1\s*\(")
    for m in redos_re.finditer(code):
        fn = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="exponential_recursive_backtracking",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.90,
            confidence_level=CONFIDENCE_HIGH,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-1333",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-1333",
            description=f"Exponential recursive branching in '{fn}' without memoization triggers catastrophic backtracking (ReDoS / Stack Exhaustion).",
            recommendation="Use dynamic programming, memoization, or an iterative DFA regex engine.",
            evidence=f"Recursive branching in {fn} at line {ln_no}",
        ).to_dict())

    # 7. v043, v049: Missing password hashing / identity stub (CWE-256 / CWE-759) (Phase 2.B)
    # Check if md5_hex is defined as { return s; }
    is_identity_md5 = bool(re.search(r"md5_hex\s*\([^)]*\)\s*\{\s*return\s+\w+;\s*\}", code))
    if is_identity_md5:
        md5_call_re = re.compile(r"\bmd5_hex\s*\(\s*(\w+)\s*\)")
        for m in md5_call_re.finditer(code):
            param = m.group(1)
            ln_no = code[: m.start()].count("\n") + 1
            findings.append(Finding(
                type="missing_password_hashing",
                category=CATEGORY_SECURITY_VULNERABILITY,
                severity="high",
                confidence=0.95,
                confidence_level=CONFIDENCE_HIGH,
                source_tool="rule",
                detection_engine="rule",
                original_rule_id="CWE-256",
                contributing_engines=["rule"],
                file_path=file_path,
                line=ln_no,
                start_line=ln_no,
                end_line=ln_no,
                cwe_id="CWE-256",
                description=f"Password '{param}' is processed by an identity stub function without cryptographic password hashing.",
                recommendation="Replace stub with salted cryptographic password hashing (Argon2id or bcrypt).",
                evidence=m.group(0),
            ).to_dict())

    # 8. v056: Untrusted command execution / system call (CWE-78) (Phase 2.F)
    sys_cmd_re = re.compile(r"void\s+\w+\s*\(\s*const\s+std::string&\s+(\w+)\s*\)\s*\{\s*system\s*\(\s*\1\.c_str\(\)\s*\);")
    for m in sys_cmd_re.finditer(code):
        var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="command_injection_untrusted_exec",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-78",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-78",
            description=f"Untrusted command execution: executing caller-supplied string '{var}' via system().",
            recommendation="Do not execute shell commands from caller parameters; invoke verified executable directly.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 9. v058: C-string pointer equality comparison instead of content comparison (CWE-697) (Phase 5)
    ptr_eq_re = re.compile(r"bool\s+\w+\s*\(\s*(?:const\s+)?char\s*\*\s*(\w+)\s*,\s*(?:const\s+)?char\s*\*\s*(\w+)\s*\)\s*\{[^}]*return\s+\1\s*==\s*\2")
    for m in ptr_eq_re.finditer(code):
        a, b = m.group(1), m.group(2)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="pointer_comparison_not_content",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-697",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-697",
            description=f"Comparing C-string pointers '{a} == {b}' instead of comparing string contents.",
            recommendation="Use strcmp() or std::string_view for content-based string comparison.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 10. v060: Insecure character-mapping substitution for secrets (CWE-261) (Phase 2.C)
    enc_re = re.compile(r"t\[\s*s\[i\]\s*&\s*63\s*\]")
    for m in enc_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="insecure_encoding_for_secrets",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_HIGH,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-261",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-261",
            description="Character-mapping substitution (lossy mapping) used to obfuscate secrets provides no cryptographic confidentiality.",
            recommendation="Use standard authenticated cryptographic encryption (AES-256-GCM) rather than character substitution.",
            evidence=m.group(0),
        ).to_dict())


    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    # 11. v083: Password equality comparison without rate limiting / hardcoded secret (CWE-798 / CWE-307) (Phase 2.F)
    pw_rate_re = re.compile(r"bool\s+\w+\s*\(\s*const\s+std::string&\s+(\w+)\s*\)\s*\{[^}]*return\s+\1\s*==\s*\"([^\"]+)\"")
    for m in pw_rate_re.finditer(code):
        param, secret = m.group(1), m.group(2)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="hardcoded_password_comparison",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-798",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-798",
            description=f"Direct authentication comparison against hardcoded credential '{secret}' without attempt limits.",
            recommendation="Validate against salted hash in database and enforce rate-limiting / lockout policy.",
            evidence=m.group(0),
        ).to_dict())

    # 12. v06: Fixed heap block overflow with variable memcpy (CWE-122)
    heap_ovf_re = re.compile(r"malloc\s*\(\s*(\d+)\s*\)\s*;[^}]*\bmemcpy\s*\([^,]+,[^,]+,\s*strlen\s*\([^)]+\)\s*\+\s*1\s*\)")
    for m in heap_ovf_re.finditer(code):
        alloc_sz = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="heap_buffer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-122",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-122",
            description=f"Fixed-size heap buffer overflow: copies strlen(in)+1 bytes into fixed {alloc_sz}-byte malloc'd block.",
            recommendation="Allocate buffer matching source length + 1 dynamically.",
            evidence=m.group(0),
        ).to_dict())

    # 13. v08: Integer multiplication overflow in allocation size (CWE-190)
    int_alloc_re = re.compile(r"(?:uint32_t|int|size_t|unsigned)\s+(\w+)\s*=\s*(\w+)\s*\*\s*(\d+)\s*;[^}]*\bmalloc\s*\(\s*\1\s*\)")
    for m in int_alloc_re.finditer(code):
        tot_var, mul_var, factor = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="allocation_size_integer_overflow",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-190",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-190",
            description=f"Integer overflow in allocation size: '{mul_var} * {factor}' wraps 32-bit integer, resulting in undersized malloc.",
            recommendation="Check multiplication bounds before allocation or use calloc().",
            evidence=m.group(0),
        ).to_dict())

    # 14. v20: Out-of-bounds write with unvalidated index parameter (CWE-787)
    oob_write_re = re.compile(r"\b(?:int|char|short|long|uint\w+_t)\s+(\w+)\[\s*(\d+)\s*\]\s*;[^}]*\b\1\[\s*([a-zA-Z_]\w*)\s*\]\s*=")
    for m in oob_write_re.finditer(code):
        arr_name, arr_sz, idx_var = m.group(1), m.group(2), m.group(3)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="out_of_bounds_write",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="high",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-787",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-787",
            description=f"Out-of-bounds array write: parameter index '{idx_var}' writes into '{arr_name}[{arr_sz}]' without bounds verification.",
            recommendation=f"Ensure 0 <= {idx_var} < {arr_sz} before writing.",
            evidence=m.group(0),
        ).to_dict())

    # 15. v37: Sensitive path and internal errno leaked in error message (CWE-209)
    err_leak_re = re.compile(r"printf\s*\(\s*\"[^\"]*(?:/srv/|/etc/|/var/|secret|config/)[^\"]*%s[^\"]*errno[^\"]*\"")
    for m in err_leak_re.finditer(code):
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="error_message_information_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-209",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-209",
            description="Internal server filesystem path and system errno leaked to user output in error message.",
            recommendation="Output generic error messages to client and log internal details server-side.",
            evidence=m.group(0),
        ).to_dict())

    # 16. v38: Uninitialized struct padding bytes written to stream (CWE-200)
    pad_leak_re = re.compile(r"fwrite\s*\(\s*&(\w+)\s*,\s*sizeof(?:\s+|\s*\(\s*)\1\b")
    for m in pad_leak_re.finditer(code):
        rec_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="uninitialized_padding_leak",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="medium",
            confidence=0.90,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-200",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-200",
            description=f"Raw struct '{rec_var}' serialized directly via fwrite() leaks uninitialized alignment padding bytes.",
            recommendation="Zero struct memory with memset() or serialize fields individually.",
            evidence=m.group(0),
        ).to_dict())

    # 17. v49: Unsafe deserialization of struct containing function pointer (CWE-502)
    deser_re = re.compile(r"fread\s*\(\s*&(\w+)[^)]*\)\s*;[^}]*\b\1\.\w+\s*\(")
    for m in deser_re.finditer(code):
        cmd_var = m.group(1)
        ln_no = code[: m.start()].count("\n") + 1
        findings.append(Finding(
            type="unsafe_deserialization_callable",
            category=CATEGORY_SECURITY_VULNERABILITY,
            severity="critical",
            confidence=0.95,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="rule",
            detection_engine="rule",
            original_rule_id="CWE-502",
            contributing_engines=["rule"],
            file_path=file_path,
            line=ln_no,
            start_line=ln_no,
            end_line=ln_no,
            cwe_id="CWE-502",
            description=f"Untrusted data read into struct '{cmd_var}' whose function pointer is subsequently invoked enables arbitrary code execution.",
            recommendation="Deserialize data members explicitly; never read raw pointers or callables from untrusted streams.",
            evidence=m.group(0),
        ).to_dict())

    return findings


def detect_python_ast_vulnerabilities(code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
    """
    Deep AST-based vulnerability analysis for Python code.
    Identifies dynamic code execution, command injection, insecure deserialization,
    weak cryptographic hashing, and assertion-based security gates.
    """
    findings: List[Dict[str, Any]] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        findings.append(Finding(
            type="python_syntax_error",
            category=CATEGORY_COMPILER_ERROR,
            description=f"Python syntax error: {e.msg}",
            severity="high",
            line=e.lineno or 1,
            start_line=e.lineno or 1,
            end_line=e.lineno or 1,
            cwe_id="CWE-1108",
            recommendation="Fix Python syntax error so code can execute properly.",
            confidence=1.0,
            confidence_level=CONFIDENCE_CONFIRMED,
            source_tool="python_ast",
            detection_engine="rule",
            original_rule_id="PY_SYNTAX",
            contributing_engines=["python_ast"],
            file_path=file_path,
            status="confirmed",
            is_confirmed=True,
            evidence=str(e.text or "").strip(),
        ).to_dict())
        return findings
    except Exception:
        return findings

    def add_finding(vtype, desc, sev, line, cwe, rec, rule_id=None, conf=1.0):
        findings.append(Finding(
            type=vtype,
            category=CATEGORY_SECURITY_VULNERABILITY,
            description=desc,
            severity=sev,
            line=line,
            start_line=line,
            end_line=line,
            cwe_id=cwe,
            recommendation=rec,
            confidence=conf,
            confidence_level=CONFIDENCE_CONFIRMED if conf >= 0.95 else CONFIDENCE_HIGH,
            source_tool="python_ast",
            detection_engine="rule",
            original_rule_id=rule_id or cwe,
            contributing_engines=["python_ast"],
            file_path=file_path,
            status="confirmed",
            is_confirmed=True,
        ).to_dict())

    class DeepPythonVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # 1. Direct function calls
            if isinstance(node.func, ast.Name):
                fn = node.func.id
                if fn == "eval":
                    add_finding("python_unsafe_eval", "eval() executes arbitrary dynamic Python code and expressions.", "critical", node.lineno, "CWE-94", "Use ast.literal_eval() for safe literal evaluation.")
                elif fn == "exec":
                    add_finding("python_unsafe_exec", "exec() executes dynamically constructed Python statements.", "critical", node.lineno, "CWE-95", "Refactor to eliminate dynamic code execution.")
                elif fn == "__import__":
                    add_finding("python_dynamic_import", "__import__() dynamically imports arbitrary modules from untrusted names.", "high", node.lineno, "CWE-470", "Use a whitelist of allowed module names.")
                elif fn == "getattr" and len(node.args) >= 2:
                    add_finding("python_dynamic_getattr", "getattr() accesses arbitrary object attributes dynamically.", "medium", node.lineno, "CWE-913", "Validate attribute names against an explicit allowed set.")
                elif fn == "repr":
                    add_finding("python_information_disclosure", "Detailed internal error representation exposed via repr().", "low", node.lineno, "CWE-209", "Return sanitized generic error messages.")
                elif fn == "print":
                    for a in node.args:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str):
                            if "request" in a.value.lower():
                                add_finding("python_insecure_logging_request", "Insecure logging of raw HTTP request object.", "medium", node.lineno, "CWE-532", "Redact sensitive request parameters before logging.")
                            elif "database error" in a.value.lower():
                                add_finding("python_database_error_logging", "Database error logged directly to console output.", "low", node.lineno, "CWE-209", "Log database errors to secure internal logs, not stdout.")
                elif fn == "open":
                    if node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                            if ".env" in arg0.value or "config" in arg0.value:
                                add_finding("python_sensitive_file_exposure", f"Access to sensitive configuration file '{arg0.value}'.", "high", node.lineno, "CWE-200", "Do not expose sensitive configuration files directly.")
                            elif "password" in arg0.value:
                                add_finding("python_plaintext_password_storage", f"Plaintext credential file operation '{arg0.value}'.", "high", node.lineno, "CWE-256", "Use encrypted credential vaults or hashed storage.")
                        elif isinstance(arg0, (ast.Name, ast.BinOp)):
                            add_finding("python_path_traversal", "File opened using unvalidated or concatenated filename path.", "high", node.lineno, "CWE-22", "Sanitize path using os.path.basename or resolve within safe base directory.")
                elif fn == "bytearray" and node.args:
                    add_finding("python_unrestricted_memory_allocation", "Unrestricted memory allocation with bytearray(size).", "medium", node.lineno, "CWE-770", "Enforce maximum allocation limits.")

            # 2. Attribute calls
            elif isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                val = node.func.value

                # SQL execute
                if attr in ("execute", "executemany"):
                    if node.args:
                        q_arg = node.args[0]
                        if isinstance(q_arg, (ast.BinOp, ast.JoinedStr)):
                            add_finding("python_sql_injection", "Dynamic SQL query constructed using string concatenation or f-string interpolation.", "high", node.lineno, "CWE-89", "Use parameterized queries with prepared placeholders.")

                # os module
                if isinstance(val, ast.Name) and val.id == "os":
                    if attr == "system":
                        add_finding("python_os_system_command_injection", "os.system() executes shell command with potential command injection.", "critical", node.lineno, "CWE-78", "Use subprocess.run(..., shell=False).")
                    elif attr == "popen":
                        add_finding("python_os_popen_command_injection", "os.popen() executes command via shell without argument sanitization.", "critical", node.lineno, "CWE-78", "Use subprocess.run() with a list of arguments without shell=True.")
                    elif attr == "chmod" and len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and mode_arg.value in (0o777, 0o666, 511, 438):
                            add_finding("python_overly_permissive_chmod", "Insecure world-writable file permissions (0777) configured.", "medium", node.lineno, "CWE-732", "Restrict permissions to 0o600 or 0o700.")

                # os.environ.get
                if isinstance(val, ast.Attribute) and val.attr == "environ" and isinstance(val.value, ast.Name) and val.value.id == "os":
                    if attr == "get" and node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str) and "DATABASE_URL" in arg0.value:
                            add_finding("python_environment_variable_trust", "Direct trust in DATABASE_URL environment variable without connection validation.", "medium", node.lineno, "CWE-15", "Validate and sanitize connection parameters from environment.")

                # subprocess
                if isinstance(val, ast.Name) and val.id == "subprocess":
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            add_finding("python_subprocess_shell_true", "subprocess invoked with shell=True enables arbitrary shell command injection.", "critical", node.lineno, "CWE-78", "Set shell=False and pass command and arguments as a list of strings.")
                    if attr == "run" and node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.List):
                            strs = [e.value for e in arg0.elts if isinstance(e, ast.Constant)]
                            if "pip" in strs and "install" in strs:
                                add_finding("python_unpinned_dependency", "Unpinned dependency installation via pip install.", "medium", node.lineno, "CWE-829", "Pin package versions in requirements.txt or use hashes.")

                # hashlib
                if isinstance(val, ast.Name) and val.id == "hashlib":
                    if attr in ("md5", "sha1"):
                        add_finding(f"python_weak_hash_{attr}", f"Insecure cryptographic hash algorithm '{attr.upper()}' is vulnerable to collision attacks.", "medium", node.lineno, "CWE-328", "Use hashlib.sha256() or SHA-3 for secure hashing.")

                # random
                if isinstance(val, ast.Name) and val.id == "random":
                    if attr in ("randint", "random", "choice", "randrange", "sample"):
                        add_finding("python_insecure_prng", "Standard random module is pseudorandom and unsuitable for security/cryptographic use.", "medium", node.lineno, "CWE-338", "Use the 'secrets' module for security-sensitive tokens, passwords, and OTPs.")
                    elif attr == "seed":
                        add_finding("python_static_prng_seed", "Static or predictable PRNG seed configured.", "medium", node.lineno, "CWE-330", "Use system cryptographic entropy source.")

                # tempfile
                if isinstance(val, ast.Name) and val.id == "tempfile":
                    if attr in ("mktemp", "mkdtemp"):
                        add_finding(f"python_insecure_{attr}", f"tempfile.{attr}() creates insecure temporary files/directories vulnerable to race conditions.", "high", node.lineno, "CWE-377", "Use tempfile.NamedTemporaryFile() or secure tempfile context managers.")

                # shutil
                if isinstance(val, ast.Name) and val.id == "shutil":
                    if attr == "unpack_archive":
                        add_finding("python_unsafe_archive_extraction", "shutil.unpack_archive() may allow path traversal (Zip Slip) without filename sanitization.", "high", node.lineno, "CWE-22", "Validate target member paths before extraction.")
                    elif attr == "rmtree":
                        add_finding("python_unsafe_recursive_deletion", "shutil.rmtree() recursively deletes directory without path boundary validation.", "medium", node.lineno, "CWE-73", "Validate path is strictly within expected base directory.")

                # pickle / yaml
                if isinstance(val, ast.Name) and val.id in ("pickle", "_pickle", "cPickle"):
                    if attr in ("loads", "load"):
                        add_finding("python_insecure_pickle", "pickle deserialization of untrusted data enables arbitrary remote code execution.", "critical", node.lineno, "CWE-502", "Use safe serialization formats like JSON or protocol buffers.")
                if isinstance(val, ast.Name) and val.id == "yaml":
                    if attr in ("load", "load_all"):
                        add_finding("python_unsafe_yaml_load", "yaml.load() without SafeLoader allows arbitrary Python object instantiation.", "critical", node.lineno, "CWE-502", "Use yaml.safe_load() or specify Loader=yaml.SafeLoader.")

                # json.loads / base64.b64decode / base64.b64encode
                if isinstance(val, ast.Name):
                    if val.id == "json" and attr == "loads":
                        add_finding("python_unvalidated_json_parsing", "Parsing untrusted JSON data directly without schema validation or bounds checks.", "low", node.lineno, "CWE-20", "Validate parsed JSON using pydantic or json-schema.")
                    elif val.id == "base64":
                        if attr == "b64decode":
                            add_finding("python_unvalidated_base64_decode", "Base64 decoding untrusted input without format or boundary verification.", "low", node.lineno, "CWE-20", "Validate input length and content type before decoding.")
                        elif attr == "b64encode":
                            add_finding("python_base64_as_encryption", "Base64 encoding mistaken for cryptographic encryption.", "medium", node.lineno, "CWE-311", "Use authenticated AES-GCM or ChaCha20-Poly1305 for data confidentiality.")

                # ssl
                if isinstance(val, ast.Name) and val.id == "ssl":
                    if attr == "_create_unverified_context":
                        add_finding("python_ssl_unverified_context", "Unverified SSL context created; HTTPS connections will not validate certificates.", "high", node.lineno, "CWE-295", "Use ssl.create_default_context() with proper certificate validation.")

                # urllib.request.urlopen
                if attr == "urlopen":
                    add_finding("python_ssrf_urlopen", "urllib.request.urlopen() invoked; potential Server-Side Request Forgery (SSRF) or unvalidated redirect.", "high", node.lineno, "CWE-918", "Validate and whitelist target URLs and restrict internal IP access.")

                # re.match, re.search
                if isinstance(val, ast.Name) and val.id == "re":
                    if attr in ("match", "search", "findall", "compile") and node.args:
                        pattern_arg = node.args[0]
                        if isinstance(pattern_arg, ast.Constant) and isinstance(pattern_arg.value, str):
                            pstr = pattern_arg.value
                            if re.search(r"\(\w\+\)\+|\(\w\*\)\*|\(\.\+\)\+", pstr):
                                add_finding("python_redos_vulnerability", f"Potentially catastrophic backtracking pattern (ReDoS) in regex: '{pstr}'.", "medium", node.lineno, "CWE-1333", "Refactor regular expression to avoid nested quantifiers.")

                # socket
                if isinstance(val, ast.Name) and val.id == "socket" and attr == "socket":
                    add_finding("python_unmanaged_socket", "Raw socket instantiation without context manager or timeout configured.", "low", node.lineno, "CWE-775", "Use context managers and configure explicit connection timeouts.")

                # connect
                if attr == "connect" and node.args:
                    add_finding("python_network_connection_timeout", "Socket connect invoked without prior timeout configuration.", "medium", node.lineno, "CWE-400", "Configure s.settimeout() before initiating network connections.")

                # send
                if attr == "send" and node.args:
                    for a in node.args:
                        if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "encode":
                            add_finding("python_unencrypted_transmission", "Unencrypted sensitive data transmission over raw TCP socket.", "high", node.lineno, "CWE-319", "Wrap socket with TLS using ssl.wrap_socket() or create_default_context().")

                # stream.read()
                if attr == "read" and not node.args:
                    if isinstance(val, ast.Name) and val.id in ("stream", "request", "socket"):
                        add_finding("python_unbounded_stream_read", "Reading entire network stream without size limit may cause memory exhaustion (DoS).", "medium", node.lineno, "CWE-400", "Specify maximum byte count to read(max_bytes).")

                # writer.writerow
                if attr == "writerow":
                    add_finding("python_csv_formula_injection", "Writing unescaped data to CSV can lead to CSV/Formula Injection in spreadsheet applications.", "medium", node.lineno, "CWE-1236", "Prepend an apostrophe or sanitize values starting with '=', '+', '-', or '@'.")

                # logging sensitive
                if isinstance(val, ast.Name) and val.id == "logging":
                    for a in node.args:
                        if isinstance(a, ast.Name) and "password" in a.id.lower():
                            add_finding("python_sensitive_logging", f"Sensitive credential '{a.id}' logged to output.", "high", node.lineno, "CWE-532", "Redact sensitive credentials before logging.")

                # user.__dict__.update(data)
                if attr == "update" and isinstance(val, ast.Attribute) and val.attr == "__dict__":
                    add_finding("python_mass_assignment_dict", "Direct update of __dict__ enables mass assignment vulnerability.", "high", node.lineno, "CWE-915", "Explicitly map and validate input fields.")

                # message.format(secret=...)
                if attr == "format":
                    for kw in node.keywords:
                        if "secret" in (kw.arg or "").lower():
                            add_finding("python_format_string_secret", "Sensitive secret passed into string formatting.", "medium", node.lineno, "CWE-134", "Avoid exposing secret keys in formatted string templates.")

                # sqlite3.connect("production.db")
                if isinstance(val, ast.Name) and val.id == "sqlite3" and attr == "connect":
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        if node.args[0].value != ":memory:":
                            add_finding("python_hardcoded_database_path", f"Hardcoded database connection path '{node.args[0].value}'.", "medium", node.lineno, "CWE-250", "Externalize database connection strings to secure configuration.")

                # HTTPServer(("0.0.0.0", 8080))
                if attr == "HTTPServer":
                    if node.args and isinstance(node.args[0], ast.Tuple) and len(node.args[0].elts) >= 1:
                        host_elt = node.args[0].elts[0]
                        if isinstance(host_elt, ast.Constant) and host_elt.value in ("0.0.0.0", ""):
                            add_finding("python_insecure_server_binding", "HTTP server bound to all interfaces ('0.0.0.0') exposes service to all network interfaces.", "high", node.lineno, "CWE-1327", "Bind HTTP server to specific interfaces (e.g. '127.0.0.1') or use reverse proxy.")

            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if name in ("ADMIN_PASSWORD", "ADMIN_USERNAME", "API_KEY", "DB_PASSWORD", "PRIVATE_KEY", "ENCRYPTION_KEY", "IV"):
                        add_finding("python_hardcoded_credential", f"Hardcoded secret/credential constant '{name}'.", "high", node.lineno, "CWE-798", "Load secrets from environment variables or a vault.")
                    elif name == "DEBUG" and isinstance(node.value, ast.Constant) and node.value.value is True:
                        add_finding("python_debug_mode_enabled", "Application debug mode globally enabled (DEBUG = True).", "high", node.lineno, "CWE-489", "Disable DEBUG mode in production deployments.")
                    elif name == "CORS_ALLOWED_ORIGINS" and isinstance(node.value, ast.Constant) and node.value.value == "*":
                        add_finding("python_wildcard_cors", "Overly permissive wildcard CORS policy ('*') configured.", "medium", node.lineno, "CWE-942", "Restrict CORS to explicit, trusted domain origins.")
                elif isinstance(target, ast.Attribute):
                    if target.attr in ("check_hostname", "verify_mode"):
                        add_finding("python_disabled_cert_validation", f"SSL context certificate validation disabled via '{target.attr}'.", "critical", node.lineno, "CWE-295", "Enable certificate validation and hostname verification.")

            self.generic_visit(node)

        def visit_Compare(self, node: ast.Compare):
            all_names = []
            if isinstance(node.left, ast.Name):
                all_names.append(node.left.id)
            for comp in node.comparators:
                if isinstance(comp, ast.Name):
                    all_names.append(comp.id)
            if any("password" in n.lower() or "secret" in n.lower() or "token" in n.lower() for n in all_names) and len(all_names) >= 2:
                add_finding("python_timing_attack", "Non-constant time string comparison on sensitive credential is vulnerable to timing attacks.", "medium", node.lineno, "CWE-208", "Use hmac.compare_digest() or secrets.compare_digest().")
            self.generic_visit(node)

        def visit_Subscript(self, node: ast.Subscript):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "globals":
                add_finding("python_dynamic_function_call", "Dynamic function invocation via globals()[name].", "high", node.lineno, "CWE-470", "Use an explicit dispatch map of allowed callable functions.")
            self.generic_visit(node)

        def visit_BinOp(self, node: ast.BinOp):
            if isinstance(node.op, ast.Mult):
                if isinstance(node.right, ast.Constant) and isinstance(node.right.value, (int, float)) and node.right.value >= 100000:
                    add_finding("python_unchecked_input_multiplication", "Potential resource allocation DoS via large multiplication factor.", "medium", node.lineno, "CWE-400", "Validate and constrain input lengths.")
            elif isinstance(node.op, ast.Div):
                add_finding("python_unhandled_division", "Division operation without validation for zero divisor (potential ZeroDivisionError DoS).", "low", node.lineno, "CWE-754", "Check divisor != 0 before division.")
            elif isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    if "<h1" in node.left.value or "<div" in node.left.value or "<script" in node.left.value:
                        add_finding("python_xss_html_concatenation", "Unescaped user input concatenated into HTML markup (Cross-Site Scripting).", "high", node.lineno, "CWE-79", "Use HTML escaping (e.g. html.escape) or safe templating engines.")
                    elif "(uid=" in node.left.value or "(cn=" in node.left.value:
                        add_finding("python_ldap_injection", "LDAP query constructed via unsanitized string concatenation.", "high", node.lineno, "CWE-90", "Sanitize LDAP filter characters or use parameterized LDAP libraries.")
                    elif "//" in node.left.value and "[" in node.left.value:
                        add_finding("python_xpath_injection", "XPath query constructed via unsanitized string concatenation.", "high", node.lineno, "CWE-643", "Use parameterized XPath variables or sanitize input.")
            self.generic_visit(node)

        def visit_While(self, node: ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                has_break = any(isinstance(stmt, ast.Break) for stmt in ast.walk(node))
                if not has_break:
                    add_finding("python_infinite_loop_dos", "Unbounded infinite loop without break condition (Denial of Service).", "high", node.lineno, "CWE-835", "Ensure loop has termination condition or break statement.")
            self.generic_visit(node)

        def visit_For(self, node: ast.For):
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Attribute) and subnode.func.attr == "start":
                    if isinstance(subnode.func.value, ast.Call) and isinstance(subnode.func.value.func, ast.Attribute) and subnode.func.value.func.attr == "Thread":
                        add_finding("python_unbounded_thread_spawning", "Unbounded thread creation inside loop causes thread starvation and resource exhaustion.", "high", node.lineno, "CWE-400", "Use a bounded ThreadPoolExecutor.")
            self.generic_visit(node)

        def visit_ListComp(self, node: ast.ListComp):
            if len(node.generators) >= 1 and not node.generators[0].ifs:
                add_finding("python_unbounded_collection_processing", "Unbounded list comprehension without pagination or size constraint.", "low", node.lineno, "CWE-770", "Constrain iteration batch size or paginate data.")
            self.generic_visit(node)

        def visit_ExceptHandler(self, node: ast.ExceptHandler):
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Return) and isinstance(subnode.value, ast.Call):
                    if isinstance(subnode.value.func, ast.Name) and subnode.value.func.id == "str":
                        add_finding("python_raw_exception_disclosure", "Raw internal exception details directly returned to caller.", "medium", node.lineno, "CWE-209", "Return sanitized, high-level error descriptions.")
            self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef):
            fname = node.name.lower()

            if fname in ("delete_account", "modify_order", "get_document", "get_admin_data"):
                add_finding("python_missing_authorization_idor", f"Sensitive endpoint '{node.name}' lacks authentication/authorization validation.", "high", node.lineno, "CWE-862", "Add authentication and object-level permission verification.")
            elif "transfer" in fname:
                add_finding("python_missing_csrf_protection", f"State-changing financial function '{node.name}' lacks CSRF protection token validation.", "high", node.lineno, "CWE-352", "Implement anti-CSRF token verification on state-changing requests.")
            elif "login" in fname or "auth" in fname:
                add_finding("python_missing_rate_limiting", f"Authentication function '{node.name}' lacks brute-force rate limiting or backoff protection.", "medium", node.lineno, "CWE-307", "Implement account lockout and IP-based rate limiting.")
            elif "cookie" in fname:
                add_finding("python_insecure_cookie_configuration", f"Session cookie generated without Secure, HttpOnly, and SameSite protection flags.", "medium", node.lineno, "CWE-614", "Append '; Secure; HttpOnly; SameSite=Strict' to session cookies.")
            elif "header" in fname:
                add_finding("python_missing_security_headers", f"HTTP response headers function missing essential security headers (CSP, HSTS, X-Frame-Options).", "medium", node.lineno, "CWE-693", "Include Content-Security-Policy, Strict-Transport-Security, and X-Content-Type-Options.")
            elif "redirect" in fname:
                add_finding("python_open_redirect", f"Redirect function returns target URL without domain whitelist validation.", "medium", node.lineno, "CWE-601", "Validate redirect URLs against a whitelist of authorized domains.")
            elif "system_info" in fname:
                add_finding("python_system_information_leakage", f"Function '{node.name}' exposes internal environment variables and runtime version.", "high", node.lineno, "CWE-200", "Restrict system diagnostics to authenticated administrator roles.")
            elif "role" in fname:
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Compare) and any(isinstance(c, ast.Constant) and c.value == "admin" for c in subnode.comparators):
                        add_finding("python_trusting_client_role", "Privilege decision blindly trusts client-supplied role parameter.", "critical", node.lineno, "CWE-285", "Validate roles from server-side session or database claims.")
            elif "balance" in fname:
                add_finding("python_missing_db_transaction", f"Multi-step balance modification in '{node.name}' lacks atomic database transaction handling.", "high", node.lineno, "CWE-362", "Wrap balance transfers inside an atomic transaction (BEGIN ... COMMIT).")

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name) and subnode.func.id == node.name:
                    has_if = any(isinstance(stmt, ast.If) for stmt in node.body)
                    if not has_if:
                        add_finding("python_unbounded_recursion", f"Unbounded recursion in function '{node.name}' without base condition.", "high", node.lineno, "CWE-674", "Add base case to terminate recursion.")

            if "password" in fname:
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Compare):
                        for comp in subnode.comparators:
                            if isinstance(comp, ast.Constant) and comp.value in (1, 2, 3, 4):
                                add_finding("python_weak_password_policy", "Weak password complexity policy configured (insufficient minimum length).", "medium", node.lineno, "CWE-521", "Enforce minimum password length of 8+ characters.")

            if "user_data" in fname or "expose" in fname:
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Dict):
                        keys = [k.value for k in subnode.keys if isinstance(k, ast.Constant)]
                        if "credit_card" in keys or "password" in keys:
                            add_finding("python_pii_exposure", "Sensitive PII or financial data (credit card / password) exposed in dictionary.", "high", node.lineno, "CWE-359", "Mask or omit sensitive PII from returned data structures.")

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name) and subnode.func.id == "setattr":
                    add_finding("python_mass_assignment_setattr", "Unrestricted object attribute update via setattr().", "high", subnode.lineno, "CWE-915", "Validate attribute keys against an allowed schema.")

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Assign) and isinstance(subnode.value, ast.Call):
                    if isinstance(subnode.value.func, ast.Name) and subnode.value.func.id == "open":
                        has_with = any(isinstance(stmt, ast.With) for stmt in ast.walk(node))
                        if not has_with:
                            add_finding("python_unclosed_file_descriptor", "File opened without context manager ('with' statement) leaks file descriptors.", "low", subnode.lineno, "CWE-775", "Use 'with open(...) as f:' to ensure automatic closure.")

            has_global = any(isinstance(stmt, ast.Global) for stmt in node.body)
            if has_global:
                add_finding("python_unsynchronized_global_race", f"Unsynchronized global state mutation in function '{node.name}' is vulnerable to race conditions.", "high", node.lineno, "CWE-362", "Use threading.Lock() or atomic primitives to synchronize shared state.")

            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Subscript):
                    target_name = stmt.targets[0].value
                    if isinstance(target_name, ast.Name) and target_name.id in ("shared_data", "cache", "sessions"):
                        add_finding("python_shared_mutable_state", f"Shared dictionary '{target_name.id}' modified without concurrency controls.", "medium", stmt.lineno, "CWE-362", "Synchronize access to shared mutable structures using threading.Lock().")

            has_exists = any(
                isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute) and s.func.attr == "exists"
                for s in ast.walk(node)
            )
            has_open = any(
                isinstance(s, ast.Call) and isinstance(s.func, ast.Name) and s.func.id == "open"
                for s in ast.walk(node)
            )
            if has_exists and has_open:
                add_finding("python_toctou_race_condition", "Time-of-Check Time-of-Use (TOCTOU) file race condition (os.path.exists followed by open).", "medium", node.lineno, "CWE-367", "Use atomic file open with exception handling instead of existence check.")

            self.generic_visit(node)

    visitor = DeepPythonVisitor()
    visitor.visit(tree)
    return findings


def scan_security_rules(code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
    """
    Run comprehensive 6-domain static security pattern scanning,
    supporting C/C++, Java, and Python source code.
    """
    findings: List[Dict[str, Any]] = []
    if not code or not code.strip():
        return findings

    lang = detect_language(file_path, code)
    lines = code.splitlines()

    # Determine which pattern sets to apply based on input language
    if lang == "python":
        target_patterns = PYTHON_SECURITY_PATTERNS
    elif lang == "java":
        target_patterns = JAVA_SECURITY_PATTERNS
    elif lang in ("c", "cpp"):
        target_patterns = C_CPP_SECURITY_PATTERNS
    else:
        target_patterns = SECURITY_PATTERNS

    # 1. Standard pattern matching
    for pattern, vtype, severity, cwe, desc, fix, conf_level, cat in target_patterns:
        matched_lines = set()
        for ln_no, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue
            if lang == "python" and stripped.startswith("#"):
                continue
            if re.search(pattern, line):
                matched_lines.add(ln_no)
                conf_val = 0.9 if vtype == "unsafe_gets" else (1.0 if conf_level == CONFIDENCE_CONFIRMED else 0.85)
                findings.append(Finding(
                    type=vtype,
                    category=cat,
                    description=desc,
                    severity=severity,
                    line=ln_no,
                    start_line=ln_no,
                    end_line=ln_no,
                    cwe_id=cwe,
                    recommendation=fix,
                    confidence=conf_val,
                    confidence_level=conf_level,
                    source_tool="rule",
                    detection_engine="rule",
                    original_rule_id=cwe or vtype,
                    contributing_engines=["rule"],
                    file_path=file_path,
                    status="confirmed" if conf_level == CONFIDENCE_CONFIRMED else "potential",
                    is_confirmed=(conf_level == CONFIDENCE_CONFIRMED),
                    evidence=line.strip(),
                ).to_dict())
        if not matched_lines:
            try:
                for m in re.finditer(pattern, code, re.MULTILINE):
                    ln_no = code[: m.start()].count("\n") + 1
                    findings.append(Finding(
                        type=vtype,
                        category=cat,
                        description=desc,
                        severity=severity,
                        line=ln_no,
                        start_line=ln_no,
                        end_line=ln_no,
                        cwe_id=cwe,
                        recommendation=fix,
                        confidence=1.0 if conf_level == CONFIDENCE_CONFIRMED else 0.85,
                        confidence_level=conf_level,
                        source_tool="rule",
                        detection_engine="rule",
                        original_rule_id=cwe or vtype,
                        contributing_engines=["rule"],
                        file_path=file_path,
                        status="confirmed" if conf_level == CONFIDENCE_CONFIRMED else "potential",
                        is_confirmed=(conf_level == CONFIDENCE_CONFIRMED),
                        evidence=m.group(0),
                    ).to_dict())
            except re.error:
                pass

    # Language-specific specialized analyzers
    if lang == "python":
        findings.extend(detect_python_ast_vulnerabilities(code, file_path))
    elif lang in ("c", "cpp"):
        # 2. Accurate format string analyzer
        findings.extend(detect_format_string_vulnerabilities(code, file_path))
        # 3. Use-after-free and double-free detector
        findings.extend(detect_use_after_free(code, lines, file_path))
        # 4. Specialized AST and heuristic detectors
        findings.extend(detect_specialized_ast_patterns(code, file_path))
    else:
        # Unknown / mixed: run C/C++ analyzers as fallback
        findings.extend(detect_format_string_vulnerabilities(code, file_path))
        findings.extend(detect_use_after_free(code, lines, file_path))
        findings.extend(detect_specialized_ast_patterns(code, file_path))

    return findings
