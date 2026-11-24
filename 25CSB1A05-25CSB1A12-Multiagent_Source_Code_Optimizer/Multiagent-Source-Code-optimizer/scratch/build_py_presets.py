"""
Build preset data for vulnerable_samples.py to include in presets.py
"""
import json
import re

def main():
    with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
        py_source = f.read()

    with open('scratch/vulnerable_samples_optimized.py', 'r', encoding='utf-8') as f:
        py_optimized = f.read()

    # Verify line numbers
    source_lines = py_source.splitlines()

    # The 10 Security Categories requested by the user:
    # 1. SQL injection: CWE 89: get_user, login, search_products, update_email
    # 2. OS command injection: CWE 78: ping_host, run_shell, run_report, convert_image, delete_path, shell_quote_wrong
    # 3. Code and reflection: CWE 95, 470: calculate, PluginLoader, import_by_name, call_by_name
    # 4. Other injection: CWE 79, 93, 113, 134, 943, 1236: build_html_page, send_mail, redirect_after_login, render_string, find_user_nosql, load_csv_rows
    # 5. Unsafe parsing and deserialization: CWE 347, 502: load_session, load_config, verify_jwt
    # 6. Path and file handling: CWE 22, 367, 377, 400, 732, 772: read_upload, read_template, download_file, get_profile_picture, extract_tar, check_then_write, make_temp, copy_secret_file, write_config, save_pickle, temp_file_world_readable, read_input_file, FileLogger
    # 7. Weak crypto and randomness: CWE 327, 330, 338, 759: hash_password, make_password_hash, session_token, make_session_id, make_reset_token
    # 8. Authentication and secrets: CWE 208, 256, 285, 307, 532, 565, 620, 798, 1188: authenticate, check_token, check_admin, check_role, login_with_lockout, remember_me, reset_password, verify_otp, log_credentials, hard-coded keys (API_KEY, ADMIN_PASSWORD), get_secret_from_env
    # 9. Network and web: CWE 295, 352, 601, 614, 668, 918: fetch_url, fetch_insecure, csrf_transfer, set_cookie, bind_all
    # 10. Logic and robustness: CWE 200, 362, 369, 396, 400, 489, 526, 617, 840, 1188, 1333: debug_dump, update_balance, Account, Cache, average, safe_divide, spawn_worker, is_admin, append_item, regex_check, DEBUG, DB_PATH

    security_findings_raw = [
        # Cat 1: SQL injection (CWE-89)
        ("SQL injection", "CWE-89", "get_user", 37, "critical", "SQL Injection via Unsanitized Query Concatenation", "Raw string concatenation of untrusted input in SQL query allows arbitrary query execution."),
        ("SQL injection", "CWE-89", "login", 45, "critical", "SQL Injection in Authentication Query", "f-string interpolation of username and password into SQL statement enables authentication bypass."),
        ("SQL injection", "CWE-89", "search_products", 334, "high", "SQL Injection in LIKE Clause", "Unescaped user search term in LIKE pattern enables database extraction via boolean/time-based SQLi."),
        ("SQL injection", "CWE-89", "update_email", 340, "critical", "SQL Injection via executescript Format String", "Percent-formatted SQL executed with executescript permits stacked queries and database takeover."),

        # Cat 2: OS command injection (CWE-78)
        ("OS command injection", "CWE-78", "ping_host", 51, "critical", "Command Injection via os.system", "Untrusted host passed directly to os.system enables command chaining and remote shell."),
        ("OS command injection", "CWE-78", "run_shell", 55, "critical", "Command Injection via subprocess with shell=True", "Arbitrary command execution via shell=True with unvalidated user commands."),
        ("OS command injection", "CWE-78", "run_report", 345, "critical", "Command Injection in Background Process", "subprocess.Popen with shell=True concatenates user name directly into command line."),
        ("OS command injection", "CWE-78", "convert_image", 349, "critical", "Command Injection in os.popen Image Converter", "File path interpolated into os.popen shell string enables arbitrary command execution."),
        ("OS command injection", "CWE-78", "delete_path", 466, "critical", "Command Injection and Destructive Delete", "os.system with concatenated path enables arbitrary command injection and destructive deletion."),
        ("OS command injection", "CWE-78", "shell_quote_wrong", 510, "high", "Improper Shell Argument Quoting", "Single-quote wrapping without escaping permits single-quote injection and arbitrary command execution."),

        # Cat 3: Code and reflection (CWE-95, CWE-470)
        ("Code and reflection", "CWE-95", "calculate", 59, "critical", "Arbitrary Code Execution via eval()", "Passing untrusted mathematical expression to eval() permits arbitrary Python code execution."),
        ("Code and reflection", "CWE-95", "PluginLoader", 559, "critical", "Arbitrary Code Execution via exec()", "Plugin code executed directly in namespace without sandboxing or bytecode inspection."),
        ("Code and reflection", "CWE-470", "import_by_name", 502, "high", "Unsafe Reflection via Dynamic __import__", "Attacker-controlled module name passed to __import__ allows loading arbitrary standard/native modules."),
        ("Code and reflection", "CWE-470", "call_by_name", 506, "high", "Unrestricted Attribute Access and Method Invocation", "getattr() on arbitrary method name permits attacker to invoke private or destructive methods."),

        # Cat 4: Other injection (CWE-79, 93, 113, 134, 943, 1236)
        ("Other injection", "CWE-79", "build_html_page", 353, "high", "Reflected Cross-Site Scripting (XSS)", "Unescaped user input concatenated into HTML markup allows arbitrary script execution in client browsers."),
        ("Other injection", "CWE-93", "send_mail", 392, "medium", "Email Header Injection via CRLF", "Newline characters in subject or to fields permit injecting arbitrary SMTP headers and recipients."),
        ("Other injection", "CWE-113", "redirect_after_login", 362, "medium", "HTTP Response Splitting / Open Redirect", "Location header crafted directly from user URL enables header injection and open redirect."),
        ("Other injection", "CWE-134", "render_string", 372, "high", "Format String Injection in str.format()", "User-controlled template string passed to format() allows accessing private object attributes."),
        ("Other injection", "CWE-943", "find_user_nosql", 329, "high", "NoSQL Injection via $where Clause", "Concatenating user input into Mongo $where JavaScript evaluation clause permits query tampering."),
        ("Other injection", "CWE-1236", "load_csv_rows", 498, "low", "CSV Formula Injection", "Unsanitized spreadsheet cells starting with =, +, -, or @ can trigger DDE formula execution."),

        # Cat 5: Unsafe parsing and deserialization (CWE-347, CWE-502)
        ("Unsafe parsing and deserialization", "CWE-502", "load_session", 67, "critical", "Insecure Deserialization via pickle.loads", "Deserializing untrusted pickle blobs executes arbitrary code through __reduce__ payloads."),
        ("Unsafe parsing and deserialization", "CWE-502", "load_config", 71, "critical", "Unsafe YAML Loading without SafeLoader", "yaml.load without Loader=yaml.SafeLoader permits instantiation of arbitrary Python objects."),
        ("Unsafe parsing and deserialization", "CWE-347", "verify_jwt", 377, "critical", "Unverified JWT Token Signature", "Base64 decoding and JSON parsing JWT payload without cryptographic signature verification."),

        # Cat 6: Path and file handling (CWE-22, 367, 377, 400, 732, 772)
        ("Path and file handling", "CWE-22", "read_upload", 79, "high", "Path Traversal in Upload File Reader", "Filename concatenation with upload directory allows directory traversal using ../ sequences."),
        ("Path and file handling", "CWE-22", "read_template", 367, "high", "Path Traversal in Template Loader", "Direct path concatenation allows reading arbitrary server files outside templates directory."),
        ("Path and file handling", "CWE-22", "download_file", 387, "medium", "Arbitrary File Overwrite via Unvalidated Destination", "Destination path not validated, allowing overwriting critical system configuration files."),
        ("Path and file handling", "CWE-22", "get_profile_picture", 397, "high", "Path Traversal and Unclosed File Handle", "Unsanitized user identifier in image path allows file disclosure; file descriptor is never closed."),
        ("Path and file handling", "CWE-22", "extract_tar", 472, "critical", "Arbitrary File Overwrite via Tar Slip Traversal", "extractall() without path validation unpacks archives with ../ members outside target directory."),
        ("Path and file handling", "CWE-367", "check_then_write", 92, "medium", "Time-of-Check to Time-of-Use (TOCTOU) Race Condition", "os.access check followed by separate open creates a window for symlink substitution attacks."),
        ("Path and file handling", "CWE-377", "make_temp", 85, "high", "Insecure Temporary File Creation via mktemp", "mktemp generates predictable paths vulnerable to pre-creation symlink hijacking."),
        ("Path and file handling", "CWE-377", "copy_secret_file", 459, "medium", "Predictable Destination in Shared Directory", "Copying secret file to predictable /tmp path allows unprivileged local users to inspect it."),
        ("Path and file handling", "CWE-732", "write_config", 455, "high", "Overly Permissive File Permissions (0o666)", "Setting world-writable permissions (0o666) allows any local user to tamper with configuration."),
        ("Path and file handling", "CWE-732", "save_pickle", 478, "high", "World-Readable and Executable Permissions (0o777)", "File permissions set to 0o777 expose serialized state to modification by any local process."),
        ("Path and file handling", "CWE-732", "temp_file_world_readable", 492, "medium", "World-Readable Permissions on Sensitive File (0o644)", "Sensitive file created with 0o644 permissions allows inspection by all local accounts."),
        ("Path and file handling", "CWE-400", "read_input_file", 483, "medium", "Unbounded File Read Leading to Resource Exhaustion", "Reading file completely into memory without size limit enables memory exhaustion (DoS)."),
        ("Path and file handling", "CWE-772", "FileLogger", 550, "medium", "Unclosed File Descriptor in Logger Instance", "File opened in append mode during init is never closed, leading to descriptor leaks."),

        # Cat 7: Weak crypto and randomness (CWE-327, 330, 338, 759)
        ("Weak crypto and randomness", "CWE-327", "hash_password", 102, "high", "Use of Cryptographically Broken Hash Algorithm (MD5)", "MD5 is vulnerable to collision attacks and extremely fast GPU-based rainbow table cracking."),
        ("Weak crypto and randomness", "CWE-759", "make_password_hash", 417, "high", "Static Salt in Fast Password Hash", "Using a hardcoded static salt with single-round SHA-256 fails to protect against precomputation attacks."),
        ("Weak crypto and randomness", "CWE-330", "session_token", 421, "high", "Predictable Session Token Generation", "MD5 of username and timestamp produces easily guessable session tokens enabling session takeover."),
        ("Weak crypto and randomness", "CWE-338", "make_session_id", 106, "high", "Cryptographically Weak Pseudo-Random Number Generator", "random.randint is not cryptographically secure and can be predicted from PRNG state."),
        ("Weak crypto and randomness", "CWE-338", "make_reset_token", 239, "high", "Predictable PRNG Seed with Epoch Timestamp", "Seeding random with current time makes password reset tokens trivially brute-forceable."),

        # Cat 8: Authentication and secrets (CWE-208, 256, 285, 307, 532, 565, 620, 798, 1188)
        ("Authentication and secrets", "CWE-798", "API_KEY", 24, "critical", "Hardcoded Secret API Key", "Live API key committed directly into source code."),
        ("Authentication and secrets", "CWE-798", "ADMIN_PASSWORD", 25, "critical", "Hardcoded Administrative Password", "Static administrative password committed in plain text."),
        ("Authentication and secrets", "CWE-798", "check_admin", 114, "high", "Hardcoded Password Validation in check_admin", "Authentication check against hardcoded administrative password constant."),
        ("Authentication and secrets", "CWE-798", "verify_otp", 437, "critical", "Hardcoded Master Backdoor Code in OTP Verification", "Master code 000000 bypasses two-factor / OTP verification unconditionally."),
        ("Authentication and secrets", "CWE-208", "check_token", 110, "medium", "Timing Attack via Non-Constant-Time String Comparison", "Standard string equality terminates early on mismatch, leaking token characters via timing."),
        ("Authentication and secrets", "CWE-256", "authenticate", 408, "high", "Plaintext Password Comparison and Timing Leak", "Comparing passwords directly in plaintext exposes credentials and timing discrepancies."),
        ("Authentication and secrets", "CWE-285", "check_role", 429, "high", "Improper Role Authorization via Substring Check", "Checking substring in roles string allows privilege escalation."),
        ("Authentication and secrets", "CWE-307", "login_with_lockout", 412, "medium", "Unenforced Account Lockout Counter", "Failed login attempts are counted in mutable dict but lockout is never enforced, allowing brute force."),
        ("Authentication and secrets", "CWE-565", "remember_me", 425, "high", "Easily Reversible Remember-Me Cookie", "Encoding username with .hex() creates a trivial, tamperable cookie allowing identity forgery."),
        ("Authentication and secrets", "CWE-620", "reset_password", 433, "high", "Unauthenticated Password Reset", "Password reset replaces user password without validating old password or reset token."),
        ("Authentication and secrets", "CWE-1188", "get_secret_from_env", 441, "medium", "Insecure Fallback Default for Secret Key", "Missing environment variable falls back to insecure known default string default_secret."),
        ("Authentication and secrets", "CWE-532", "log_credentials", 445, "high", "Cleartext Credential Logging", "Sensitive user credentials printed directly to standard output / application logs."),

        # Cat 9: Network and web (CWE-295, 352, 601, 614, 668, 918)
        ("Network and web", "CWE-918", "fetch_url", 124, "high", "Server-Side Request Forgery (SSRF) and Unbounded Fetch", "Unvalidated URL passed to urlopen allows accessing internal metadata services and private subnets."),
        ("Network and web", "CWE-295", "fetch_insecure", 246, "high", "Disabled TLS Hostname Verification", "check_hostname set to False permits man-in-the-middle attacks on encrypted HTTPS traffic."),
        ("Network and web", "CWE-668", "bind_all", 254, "medium", "Server Socket Bound to All Network Interfaces (0.0.0.0)", "Binding to INADDR_ANY exposes internal management port to public network interfaces."),
        ("Network and web", "CWE-614", "set_cookie", 357, "medium", "Missing Secure and HttpOnly Flags on Session Cookie", "Session cookie set without Secure and HttpOnly flags exposes cookie to XSS theft and MITM sniffing."),
        ("Network and web", "CWE-352", "csrf_transfer", 381, "high", "Missing Cross-Site Request Forgery (CSRF) Protection", "State-changing POST request processed without validating an anti-CSRF token."),

        # Cat 10: Logic and robustness (CWE-200, 362, 369, 396, 400, 489, 526, 617, 840, 1188, 1333)
        ("Logic and robustness", "CWE-489", "DEBUG", 26, "medium", "Active Debug Mode in Production Code", "DEBUG flag set to True exposes internal stack traces and debugging endpoints."),
        ("Logic and robustness", "CWE-377", "DB_PATH", 27, "medium", "Database Stored in World-Accessible Shared Directory", "Placing SQLite database in /tmp allows local attackers to corrupt or overwrite database files."),
        ("Logic and robustness", "CWE-396", "safe_divide", 134, "low", "Catch-All Bare Exception Hides Critical Failures", "Bare except: catches system exit, memory errors, and interrupts, masking unexpected crashes."),
        ("Logic and robustness", "CWE-1188", "append_item", 138, "low", "Mutable Default Argument in Function Definition", "Using [] as default parameter retains state across calls, causing cross-request data leaks."),
        ("Logic and robustness", "CWE-1333", "regex_check", 144, "medium", "Catastrophic Regular Expression Backtracking (ReDoS)", "Nested repetition pattern ^(a+)+$ causes exponential backtracking on crafted input."),
        ("Logic and robustness", "CWE-617", "is_admin", 259, "high", "Authorization Enforcement via assert Statement", "assert statements are stripped when Python runs with optimization (-O), disabling auth checks."),
        ("Logic and robustness", "CWE-362", "update_balance", 265, "high", "Race Condition in Account Balance Update", "Non-atomic read-modify-write cycle with sleep creates window for double-spending."),
        ("Logic and robustness", "CWE-200", "debug_dump", 271, "high", "Information Disclosure via Environment Variable Dump", "Serializing os.environ exposes API keys, database credentials, and host configuration."),
        ("Logic and robustness", "CWE-526", "spawn_worker", 487, "medium", "Full Environment Inheritance in Child Process", "Passing entire parent environment to child process leaks sensitive secrets to worker tasks."),
        ("Logic and robustness", "CWE-840", "Account", 524, "high", "Unchecked Negative Withdrawal / Deposit Logic", "Withdrawal and deposit methods lack validation against negative values or overdraft."),
        ("Logic and robustness", "CWE-532", "Account", 535, "medium", "Password Leaked in Object Representation (__repr__)", "Plaintext account password formatted into __repr__ leaks credentials during debugging/logging."),
        ("Logic and robustness", "CWE-1188", "Cache", 539, "medium", "Shared Mutable Class Attribute in Cache", "Class-level dict store is shared across all Cache instances rather than scoped per instance."),
        ("Logic and robustness", "CWE-400", "Cache", 545, "medium", "Unbounded Cache Growth Leading to Memory Exhaustion", "Cache lacks eviction policy (LRU) or capacity limit, leading to uncontrolled memory growth."),
        ("Logic and robustness", "CWE-117", "FileLogger", 553, "medium", "Log Injection via Unsanitized Message Strings", "Writing unsanitized log entries permits log forging and splitting via newline characters."),
        ("Logic and robustness", "CWE-369", "average", 626, "low", "Divide by Zero on Empty Input Collection", "len(values) in denominator raises ZeroDivisionError when passed an empty list or tuple.")
    ]

    # Verify uniqueness of line numbers
    lines_seen = set()
    for cat, cwe, fn, lno, sev, title, desc in security_findings_raw:
        if lno in lines_seen:
            raise ValueError(f"DUPLICATE line {lno} for {fn}")
        lines_seen.add(lno)
        # Verify line in source
        actual_line = source_lines[lno - 1]
        print(f"Verified L{lno:3d} [{cwe:7s}]: {actual_line.strip()[:60]}")

    print(f"\nAll {len(security_findings_raw)} security findings have verified unique lines!")

if __name__ == '__main__':
    main()
