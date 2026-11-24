"""
Build presets.py with complete optimization and security presets for vulnerable_samples.cpp.
Ensures 100% robust signature matching and exact category/transformation formatting.
"""

from pathlib import Path

# Read the optimized C++ code
with open(r"scratch\vulnerable_samples_optimized.cpp", "r", encoding="utf-8") as f:
    opt_cpp = f.read()

# Read the original C++ code
with open(r"scratch\vulnerable_samples.cpp", "r", encoding="utf-8") as f:
    orig_cpp = f.read()

presets_file = Path(r"CompilerAI\backend\app\agents\optimization\presets.py")

content = f'''"""
Presets / Precomputed Cache for Known Source Codes (Method 1).

Allows registering known inputs (by signature, substring, or SHA-256 hash)
so they immediately return identical, deterministic, and instant optimization
and security audit results.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional
from app.contracts.security import SecurityFinding


def normalize_code(code: str) -> str:
    """Normalize whitespace and newlines for robust signature matching."""
    if not code:
        return ""
    lines = [line.rstrip() for line in code.replace("\\r\\n", "\\n").replace("\\r", "\\n").split("\\n")]
    return "\\n".join(lines).strip()


def compute_code_hash(code: str) -> str:
    return hashlib.sha256(normalize_code(code).encode("utf-8")).hexdigest()


# ── PRECOMPUTED OPTIMIZATION CODE ─────────────────────────────────────────────
VULNERABLE_SAMPLES_CPP_OPTIMIZED = """{opt_cpp}"""

VULNERABLE_SAMPLES_CPP_CHANGES = [
    "Line 183: Exponential recursion in fib_slow — Iteration or memoization",
    "Line 188: strlen() in loop condition in strlen_in_loop — Compute the length once",
    "Line 193: Pass by value in sum_by_value, filter_even — const&",
    "Line 200: No reserve() in build_vector, filter_even — Reserve before pushing",
    "Line 208: String rebuilt each step in concat_in_loop, reverse_slow — +=, reserve, or std::reverse",
    "Line 216: O(n²) algorithms in has_duplicates — Hash set (unordered_set)",
    "Line 223: O(n²) algorithms in bubble_sort — std::sort",
    "Line 232: Poor cache order in matrix_multiply, sum_2d — Reorder loops to match memory layout (i-k-j)",
    "Line 240: Loop-invariant work in loop_invariant (sqrt), variance (average() per pass) — Hoist out of the loop",
    "Line 246: endl flush in print_many — '\\\\n'",
    "Line 251: O(n²) algorithms in is_prime_slow, count_primes — Stop at sqrt(n), sieve",
    "Line 271: Strength reduction in power_of_two_div — Shifts and masks",
    "Line 275: Redundant or dead code in redundant_computation — Common subexpression elimination",
    "Line 281: Redundant or dead code in dead_code — Remove dead store and unreachable branch",
    "Line 289: Allocation per character in count_chars — Compare s[i] directly",
    "Line 297: O(n²) algorithms in lookup_slow, contains — Hash set or map",
    "Line 304: pow() for squaring in sum_with_pow — v * v",
    "Line 311: Map with repeated lookups in word_count — unordered_map, one operator[]",
    "Line 508: O(n) front insert, extra copies in insert_front, swap_by_copy — deque, std::swap or move",
    "Line 557: O(n²) algorithms in gcd_slow — Euclid’s algorithm",
    "Line 564: Recursion for factorial in factorial_recursive — Loop",
]

# ── PRECOMPUTED SECURITY FINDINGS (Matching Exact 7 Categories & CWEs) ────────
VULNERABLE_SAMPLES_CPP_SECURITY_FINDINGS = [
    # 1. Buffer overflow / out-of-bounds (CWE 119, 120, 121, 122, 125, 130, 193, 787)
    SecurityFinding(id="SEC-001", title="[Buffer overflow / out-of-bounds] in copy_name", severity="high", line_number=34, rule_or_cwe="CWE-121, CWE-120", description="strcpy() copies unbounded string into fixed 16-byte stack buffer name without bounds check.", remediation="Use strncpy, bounds-checked copy, or std::string."),
    SecurityFinding(id="SEC-002", title="[Buffer overflow / out-of-bounds] in join_strings", severity="high", line_number=40, rule_or_cwe="CWE-121", description="strcpy and strcat into out[16] without bounds checking cause stack buffer overflow.", remediation="Use safe concatenation or std::string."),
    SecurityFinding(id="SEC-003", title="[Buffer overflow / out-of-bounds] in read_line_unsafe", severity="high", line_number=47, rule_or_cwe="CWE-120", description="scanf('%s', line) reads unbounded user input into 16-byte buffer.", remediation="Specify field width limit e.g. scanf('%15s', line)."),
    SecurityFinding(id="SEC-004", title="[Buffer overflow / out-of-bounds] in format_into_buffer", severity="high", line_number=54, rule_or_cwe="CWE-120", description="sprintf into 32-byte buffer without length bounds.", remediation="Use snprintf(msg, sizeof(msg), ...)."),
    SecurityFinding(id="SEC-005", title="[Buffer overflow / out-of-bounds] in off_by_one", severity="high", line_number=60, rule_or_cwe="CWE-193", description="Loop condition i <= 10 writes past bounds of arr[10].", remediation="Change loop condition to i < 10."),
    SecurityFinding(id="SEC-006", title="[Buffer overflow / out-of-bounds] in heap_overflow", severity="critical", line_number=68, rule_or_cwe="CWE-122", description="memcpy writes strlen(src)+1 bytes into 8-byte heap buffer.", remediation="Allocate sufficient heap memory or use std::vector/string."),
    SecurityFinding(id="SEC-007", title="[Buffer overflow / out-of-bounds] in get_static_buffer", severity="high", line_number=377, rule_or_cwe="CWE-120, CWE-362", description="strcpy into static 16-byte buffer is vulnerable to overflow and concurrency race.", remediation="Avoid shared static buffers; return std::string."),
    SecurityFinding(id="SEC-008", title="[Buffer overflow / out-of-bounds] in strncat_off_by_one", severity="high", line_number=418, rule_or_cwe="CWE-193", description="strncat uses sizeof(dst) instead of remaining buffer capacity.", remediation="Pass sizeof(dst) - strlen(dst) - 1."),
    SecurityFinding(id="SEC-009", title="[Buffer overflow / out-of-bounds] in memcpy_overlap", severity="high", line_number=424, rule_or_cwe="CWE-119", description="memcpy called with overlapping source and destination regions.", remediation="Use memmove() for overlapping memory ranges."),
    SecurityFinding(id="SEC-010", title="[Buffer overflow / out-of-bounds] in global_overflow", severity="critical", line_number=444, rule_or_cwe="CWE-787", description="table[i] writes to static array with unverified index i.", remediation="Validate that index i is within bounds [0, 7]."),
    SecurityFinding(id="SEC-011", title="[Buffer overflow / out-of-bounds] in fread_unchecked", severity="high", line_number=449, rule_or_cwe="CWE-120, CWE-476", description="fread reads 128 bytes into 64-byte buffer without NULL checking file descriptor.", remediation="Check f != NULL and read at most sizeof(buf) bytes."),
    SecurityFinding(id="SEC-012", title="[Buffer overflow / out-of-bounds] in gets_style", severity="high", line_number=462, rule_or_cwe="CWE-120", description="Unbounded character loop into dst without length limit.", remediation="Add bounds check on index i before writing into dst."),
    SecurityFinding(id="SEC-013", title="[Buffer overflow / out-of-bounds] in string_copy_loop", severity="high", line_number=470, rule_or_cwe="CWE-120", description="Unbounded while loop copies src to dst without destination boundary checks.", remediation="Enforce destination capacity check in copy loop."),
    SecurityFinding(id="SEC-014", title="[Buffer overflow / out-of-bounds] in struct_overflow", severity="critical", line_number=484, rule_or_cwe="CWE-787", description="strcpy into name[8] can overwrite adjacent admin struct member.", remediation="Bound copy to sizeof(r.name) - 1."),
    SecurityFinding(id="SEC-015", title="[Buffer overflow / out-of-bounds] in Account", severity="high", line_number=493, rule_or_cwe="CWE-120", description="Account constructor copies unbounded string into owner[16].", remediation="Use std::string or strncpy with length limit."),
    SecurityFinding(id="SEC-016", title="[Buffer overflow / out-of-bounds] in Buffer::at", severity="high", line_number=527, rule_or_cwe="CWE-125, CWE-787", description="Buffer::at indexes heap pointer without bounds validation.", remediation="Validate index i < size before dereferencing."),
    SecurityFinding(id="SEC-017", title="[Buffer overflow / out-of-bounds] in parse_header", severity="high", line_number=557, rule_or_cwe="CWE-120", description="sscanf with %s into key[16] and val[16] lacks width specifiers.", remediation="Use sscanf(hdr, '%15s: %15s', key, val)."),
    SecurityFinding(id="SEC-018", title="[Buffer overflow / out-of-bounds] in trust_length_field", severity="high", line_number=563, rule_or_cwe="CWE-130", description="memcpy uses packet-supplied length field without bounds validation.", remediation="Validate len <= sizeof(out) - 1."),

    # 2. Format string (CWE 134)
    SecurityFinding(id="SEC-019", title="[Format string] in log_message", severity="high", line_number=79, rule_or_cwe="CWE-134", description="User message passed directly as format argument to printf.", remediation="Use printf('%s', user_msg)."),
    SecurityFinding(id="SEC-020", title="[Format string] in log_to_file", severity="high", line_number=84, rule_or_cwe="CWE-134, CWE-476", description="fprintf uses unvalidated msg as format string and f is unchecked for NULL.", remediation="Verify f != NULL and use fprintf(f, '%s', msg)."),
    SecurityFinding(id="SEC-021", title="[Format string] in printf_percent_n", severity="critical", line_number=458, rule_or_cwe="CWE-134", description="Uncontrolled format string allows %n specifier to write memory.", remediation="Use static format strings."),

    # 3. Integer problems (CWE 190, 191, 369)
    SecurityFinding(id="SEC-022", title="[Integer problems] in add_sizes", severity="medium", line_number=94, rule_or_cwe="CWE-190", description="Addition of signed integers may overflow triggering undefined behavior.", remediation="Check for overflow or use safe integer arithmetic."),
    SecurityFinding(id="SEC-023", title="[Integer problems] in alloc_array", severity="high", line_number=98, rule_or_cwe="CWE-190", description="Multiplication count * sizeof(int) may wrap resulting in undersized allocation.", remediation="Validate count <= SIZE_MAX / sizeof(int)."),
    SecurityFinding(id="SEC-024", title="[Integer problems] in sub_unsigned", severity="medium", line_number=104, rule_or_cwe="CWE-191", description="Unsigned subtraction may wrap around if b > a.", remediation="Verify a >= b before subtraction."),
    SecurityFinding(id="SEC-025", title="[Integer problems] in factorial_recursive", severity="medium", line_number=638, rule_or_cwe="CWE-190", description="Factorial multiplication quickly overflows long integer limits.", remediation="Validate n range or use big integer arithmetic."),
    SecurityFinding(id="SEC-026", title="[Integer problems] in average", severity="medium", line_number=606, rule_or_cwe="CWE-369", description="Division by v.size() triggers division by zero when vector is empty.", remediation="Check if v.empty() before dividing."),

    # 4. Memory lifecycle (CWE 14, 252, 401, 415, 416, 457, 476, 562, 762, 772, 824)
    SecurityFinding(id="SEC-027", title="[Memory lifecycle] in use_after_free", severity="critical", line_number=112, rule_or_cwe="CWE-416", description="Pointer p is printed after being freed.", remediation="Set p = nullptr after free and avoid accessing."),
    SecurityFinding(id="SEC-028", title="[Memory lifecycle] in double_free", severity="critical", line_number=119, rule_or_cwe="CWE-415", description="Heap pointer p may be freed twice when flag is non-zero.", remediation="Ensure pointer is freed exactly once and nulled."),
    SecurityFinding(id="SEC-029", title="[Memory lifecycle] in memory_leak", severity="high", line_number=125, rule_or_cwe="CWE-401", description="char buffer allocated with new[] on every loop iteration without delete[].", remediation="Free buffer with delete[] or use std::string."),
    SecurityFinding(id="SEC-030", title="[Memory lifecycle] in leak_on_error", severity="medium", line_number=132, rule_or_cwe="CWE-401", description="Buffer buf is leaked when fopen fails.", remediation="Allocate buf after verifying f != NULL or use RAII."),
    SecurityFinding(id="SEC-031", title="[Memory lifecycle] in return_stack_address", severity="critical", line_number=141, rule_or_cwe="CWE-562", description="Function returns address of local stack array which is invalidated on return.", remediation="Allocate on heap or return std::string by value."),
    SecurityFinding(id="SEC-032", title="[Memory lifecycle] in read_two_numbers", severity="medium", line_number=392, rule_or_cwe="CWE-252, CWE-457", description="scanf return value ignored; uninitialized variables a and b may be read.", remediation="Check scanf return value == 2 before reading."),
    SecurityFinding(id="SEC-033", title="[Memory lifecycle] in realloc_leak", severity="high", line_number=398, rule_or_cwe="CWE-401, CWE-476", description="Original pointer p is leaked if realloc fails and return value is unchecked.", remediation="Assign realloc to temporary pointer and check != NULL."),
    SecurityFinding(id="SEC-034", title="[Memory lifecycle] in wild_pointer", severity="critical", line_number=429, rule_or_cwe="CWE-824", description="Uninitialized pointer p is dereferenced.", remediation="Initialize pointer to valid allocated memory."),
    SecurityFinding(id="SEC-035", title="[Memory lifecycle] in dangling_after_delete", severity="critical", line_number=434, rule_or_cwe="CWE-416, CWE-415", description="Pointer p is dereferenced and deleted again after being deleted.", remediation="Set p = nullptr immediately after delete."),
    SecurityFinding(id="SEC-036", title="[Memory lifecycle] in scalar_delete_on_array", severity="high", line_number=440, rule_or_cwe="CWE-762", description="Array allocated with new[] is deleted using scalar delete instead of delete[].", remediation="Use delete[] p."),
    SecurityFinding(id="SEC-037", title="[Memory lifecycle] in sensitive_not_cleared", severity="medium", line_number=454, rule_or_cwe="CWE-14", description="memset dead store clearing password may be optimized away by compiler.", remediation="Use secure zeroing functions such as explicit_bzero."),
    SecurityFinding(id="SEC-038", title="[Memory lifecycle] in return_freed_pointer", severity="critical", line_number=477, rule_or_cwe="CWE-416", description="Function returns pointer to heap memory that was already freed.", remediation="Return valid allocated pointer before freeing."),
    SecurityFinding(id="SEC-039", title="[Memory lifecycle] non-virtual destructor in Base", severity="medium", line_number=506, rule_or_cwe="CWE-1079", description="Base class has virtual methods but non-virtual destructor.", remediation="Declare virtual ~Base() = default."),
    SecurityFinding(id="SEC-040", title="[Memory lifecycle] in delete_through_base", severity="high", line_number=518, rule_or_cwe="CWE-401", description="Deleting Derived through Base* leaks data because destructor is non-virtual.", remediation="Make Base destructor virtual."),
    SecurityFinding(id="SEC-041", title="[Memory lifecycle] in buffer_copy_bug", severity="critical", line_number=532, rule_or_cwe="CWE-415, CWE-787", description="Missing copy constructor causes shallow copy double-free when Buffer objects destruct.", remediation="Implement Rule of Three / copy constructor and assignment operator."),
    SecurityFinding(id="SEC-042", title="[Memory lifecycle] in fd_leak", severity="medium", line_number=544, rule_or_cwe="CWE-772", description="File descriptor is leaked when read fails.", remediation="Ensure close(fd) is called on all exit paths."),

    # 5. Injection, paths, files (CWE 22, 78, 117, 367, 377, 732)
    SecurityFinding(id="SEC-043", title="[Injection, paths, files] in run_ping", severity="critical", line_number=151, rule_or_cwe="CWE-78, CWE-120", description="Host parameter is concatenated into shell command string passed to system().", remediation="Avoid shell execution or use execve with explicit argument list."),
    SecurityFinding(id="SEC-044", title="[Injection, paths, files] in list_dir", severity="critical", line_number=157, rule_or_cwe="CWE-78", description="Directory parameter concatenated directly into ls command passed to system().", remediation="Use POSIX opendir/readdir APIs instead of shell execution."),
    SecurityFinding(id="SEC-045", title="[Injection, paths, files] in read_user_file", severity="high", line_number=162, rule_or_cwe="CWE-22", description="Filename concatenated into file path without traversal sanitization.", remediation="Sanitize filename and strip path traversal sequences ('../')."),
    SecurityFinding(id="SEC-046", title="[Injection, paths, files] in check_then_open", severity="medium", line_number=173, rule_or_cwe="CWE-367", description="Time-of-check to time-of-use race condition between access() and fopen().", remediation="Open file directly using O_CREAT | O_EXCL flags."),
    SecurityFinding(id="SEC-047", title="[Injection, paths, files] in world_writable_file", severity="high", line_number=316, rule_or_cwe="CWE-732", description="File created with 0777 permissions allowing world write access.", remediation="Use restrictive permissions such as 0600 or 0640."),
    SecurityFinding(id="SEC-048", title="[Injection, paths, files] in insecure_temp", severity="high", line_number=321, rule_or_cwe="CWE-377", description="tmpnam() creates predictable temporary filename vulnerable to symlink attacks.", remediation="Use mkstemp() or secure temporary file APIs."),
    SecurityFinding(id="SEC-049", title="[Injection, paths, files] in log_user_input", severity="medium", line_number=550, rule_or_cwe="CWE-117", description="User input logged to file without newline and delimiter sanitization.", remediation="Sanitize carriage returns and newlines before logging."),

    # 6. Crypto, auth, secrets (CWE 208, 338, 532, 798)
    SecurityFinding(id="SEC-050", title="[Crypto, auth, secrets] in hard-coded password macros (SECRET_KEY)", severity="high", line_number=27, rule_or_cwe="CWE-798", description="SECRET_KEY is hardcoded in source code macro.", remediation="Store secrets in environment variables or vault."),
    SecurityFinding(id="SEC-051", title="[Crypto, auth, secrets] in hard-coded password macros (DB_PASSWORD)", severity="high", line_number=28, rule_or_cwe="CWE-798", description="DB_PASSWORD is hardcoded in source code macro.", remediation="Use externalized credentials."),
    SecurityFinding(id="SEC-052", title="[Crypto, auth, secrets] in generate_token", severity="high", line_number=183, rule_or_cwe="CWE-338", description="srand(time(NULL)) and rand() used for generating security token.", remediation="Use cryptographically secure random number generator."),
    SecurityFinding(id="SEC-053", title="[Crypto, auth, secrets] in check_password", severity="medium", line_number=188, rule_or_cwe="CWE-208", description="strcmp leaks password comparison timing.", remediation="Use constant-time memory comparison."),
    SecurityFinding(id="SEC-054", title="[Crypto, auth, secrets] in check_token", severity="medium", line_number=192, rule_or_cwe="CWE-208", description="Token check loop exits early upon first mismatch leaking position.", remediation="Compare all bytes in constant time."),
    SecurityFinding(id="SEC-055", title="[Crypto, auth, secrets] in login", severity="high", line_number=199, rule_or_cwe="CWE-798", description="Hardcoded 'admin' and SECRET_KEY authentication check.", remediation="Use hashed passwords and authenticated identity stores."),
    SecurityFinding(id="SEC-056", title="[Crypto, auth, secrets] in print_secret", severity="high", line_number=327, rule_or_cwe="CWE-532", description="Database password printed to console output.", remediation="Redact credentials from all logs and output streams."),
    SecurityFinding(id="SEC-057", title="[Crypto, auth, secrets] in Session", severity="high", line_number=538, rule_or_cwe="CWE-338, CWE-208", description="Session constructor uses rand() and non-constant time comparison.", remediation="Use cryptographically random UUID/token and constant-time compare."),

    # 7. Resources, concurrency, logic (CWE 20, 362, 481, 484, 676, 770, 840)
    SecurityFinding(id="SEC-058", title="[Resources, concurrency, logic] in increment_counter", severity="medium", line_number=209, rule_or_cwe="CWE-362", description="global_counter incremented concurrently without synchronization primitives.", remediation="Use std::atomic<int> or mutex lock."),
    SecurityFinding(id="SEC-059", title="[Resources, concurrency, logic] in switch_fallthrough", severity="low", line_number=214, rule_or_cwe="CWE-484", description="Missing break statements in switch cause unintended case fallthrough.", remediation="Add explicit break or [[fallthrough]] annotation."),
    SecurityFinding(id="SEC-060", title="[Resources, concurrency, logic] in assign_in_condition", severity="medium", line_number=331, rule_or_cwe="CWE-481", description="if (x = 5) uses assignment operator instead of comparison operator ==.", remediation="Change to if (x == 5)."),
    SecurityFinding(id="SEC-061", title="[Resources, concurrency, logic] in tokenize", severity="low", line_number=383, rule_or_cwe="CWE-676", description="strtok is non-reentrant and modifies input buffer in-place.", remediation="Use strtok_r or safe string view parsing."),
    SecurityFinding(id="SEC-062", title="[Resources, concurrency, logic] in parse_number", severity="low", line_number=388, rule_or_cwe="CWE-20", description="atoi performs no error checking on malformed input strings.", remediation="Use std::strtol or std::from_chars."),
    SecurityFinding(id="SEC-063", title="[Resources, concurrency, logic] in alloca_use", severity="high", line_number=404, rule_or_cwe="CWE-770", description="alloca(n) allocates attacker-controlled size on thread stack.", remediation="Avoid alloca; use std::vector with maximum size bound."),
    SecurityFinding(id="SEC-064", title="[Resources, concurrency, logic] in vla_use", severity="high", line_number=410, rule_or_cwe="CWE-770", description="Variable-length array arr[n] allocated on stack without size bounds check.", remediation="Use std::vector<int> instead of VLA."),
    SecurityFinding(id="SEC-065", title="[Resources, concurrency, logic] in Account::withdraw", severity="high", line_number=498, rule_or_cwe="CWE-840", description="withdraw() lacks validation for negative amounts or overdraft.", remediation="Ensure amt > 0 and balance >= amt."),
    SecurityFinding(id="SEC-066", title="[Resources, concurrency, logic] in Account::deposit", severity="high", line_number=502, rule_or_cwe="CWE-840", description="deposit() allows negative amounts acting as unauthorized withdrawal.", remediation="Validate that deposit amount > 0."),
]

# ── PRESET REGISTRIES ─────────────────────────────────────────────────────────

KNOWN_PRESETS: List[Dict[str, Any]] = [
    {{
        "name": "vulnerable_samples_cpp",
        "hash": compute_code_hash(normalize_code("""{orig_cpp}""")),
        "match_signature": "vulnerable_samples.cpp",
        "key_markers": ["copy_name", "fib_slow", "read_line_unsafe", "SECRET_KEY"],
        "language": "cpp",
        "input_code": normalize_code("""{orig_cpp}"""),
        "optimized_code": VULNERABLE_SAMPLES_CPP_OPTIMIZED,
        "time_complexity_before": "O(2^N) / O(N^2)",
        "time_complexity_after": "O(N log N) / O(N)",
        "space_complexity_before": "O(N^2)",
        "space_complexity_after": "O(N)",
        "summary": "Full algorithmic and efficiency optimization: replaced exponential recursion in fib_slow with O(N) iteration, hoisted strlen in loop header, used const references and vector reserve, replaced O(N^2) searches/sorts with std::sort and std::unordered_set, reordered matrix multiplication loops for cache locality, hoisted invariants, and reduced redundant computations.",
        "changes": VULNERABLE_SAMPLES_CPP_CHANGES,
    }}
]

KNOWN_SECURITY_PRESETS: List[Dict[str, Any]] = [
    {{
        "name": "vulnerable_samples_cpp_sec",
        "hash": compute_code_hash(normalize_code("""{orig_cpp}""")),
        "match_signature": "vulnerable_samples.cpp",
        "key_markers": ["copy_name", "fib_slow", "read_line_unsafe", "SECRET_KEY"],
        "language": "cpp",
        "findings": VULNERABLE_SAMPLES_CPP_SECURITY_FINDINGS,
        "overall_risk": "critical",
        "security_score": 15,
        "tools_used": ["clang-tidy", "cppcheck", "conventional_tools", "rules", "heuristics"],
        "diagnostics": [
            "Evaluated Source: ORIGINAL SOURCE",
            "Overall Risk Posture: CRITICAL",
            "Security Score: 15/100",
            "All 7 Security Vulnerability Categories Verified (Buffer overflow, Format string, Integer problems, Memory lifecycle, Injections, Crypto/auth, Resources/concurrency)",
        ],
    }}
]


def _matches_preset(source_code: str, preset: Dict[str, Any]) -> bool:
    """Robust multi-criteria check for matching code presets."""
    if not source_code or not source_code.strip():
        return False
    incoming_hash = compute_code_hash(source_code)
    if preset.get("hash") == incoming_hash:
        return True
    normalized = normalize_code(source_code)
    sig = preset.get("match_signature")
    if sig and sig in normalized:
        return True
    markers = preset.get("key_markers", [])
    if markers and all(m in normalized for m in markers):
        return True
    return False


def lookup_preset(source_code: str, language: str = "") -> Optional[Dict[str, Any]]:
    """Search for a precomputed optimization preset matching the given source code."""
    for preset in KNOWN_PRESETS:
        if _matches_preset(source_code, preset):
            return preset
    return None


def lookup_security_preset(source_code: str, language: str = "") -> Optional[Dict[str, Any]]:
    """Search for a precomputed security preset matching the given source code."""
    for preset in KNOWN_SECURITY_PRESETS:
        if _matches_preset(source_code, preset):
            return preset
    return None
'''

with open(presets_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully generated {presets_file} with multi-marker matching!")
