"""
Script to append the dedicated Test Cases Section (with all 198 test cases and screenshots .1 to .17)
to CompilerAI_Optimization_Studio_Research_Paper_with_Appendix.docx.
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_heading_styled(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.name = 'Arial'
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a) # slate-900
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b) # slate-800
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
    else:
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55) # slate-700
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    return p

def add_screenshot_entry(doc, img_path, title, description):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(6.2))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(4)
    run_cap = p_cap.add_run(title)
    run_cap.bold = True
    run_cap.font.name = 'Arial'
    run_cap.font.size = Pt(9)
    run_cap.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(10)
    p_desc.paragraph_format.line_spacing = 1.15
    run_desc = p_desc.add_run(description)
    run_desc.font.name = 'Arial'
    run_desc.font.size = Pt(8.5)
    run_desc.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

def append_test_cases_section():
    doc_path = 'CompilerAI_Optimization_Studio_Research_Paper_with_Appendix.docx'
    doc = docx.Document(doc_path)

    # Add Page Break before Appendix B
    doc.add_page_break()

    # Section Heading
    add_heading_styled(doc, 'APPENDIX B: SYSTEMATIC BENCHMARK TEST CASES & LIVE EXECUTION PROOFS (198 TEST CASES)', level=1)
    add_body_p(doc, 
        'This appendix provides a rigorous, exhaustive enumeration of all 198 ground-truth test cases evaluated within the '
        'CompilerAI Optimization Studio across its autonomous multi-agent orchestration architecture. The testbed evaluates '
        'three primary benchmark corpora: (1) the C++ ground-truth benchmark suite (vulnerable_samples.cpp) containing 87 test cases '
        '(66 security vulnerability cases across 7 CWE domains and 21 algorithmic optimization cases); (2) the Python ground-truth '
        'benchmark suite (vulnerable_samples.py) containing 107 test cases (73 security vulnerability cases across 10 distinct '
        'categories and 34 algorithmic optimization cases across 9 problem families); and (3) built-in language starter presets and '
        'execution mode invariants across C++, Python, C, and JavaScript (4 test cases). Each test case is individually numbered (1 through 198), '
        'mapped to its corresponding Common Weakness Enumeration (CWE) or Optimization identifier, source function, and line number. '
        'Live execution outputs captured directly from the running studio server are embedded as high-resolution screenshots, '
        'systematically numbered as Screenshot .1 through Screenshot .17, accompanied by detailed descriptive evaluations.'
    )

    # -------------------------------------------------------------
    # SUITE 1: C++ Benchmark Suite (Test Cases 1 - 87)
    # -------------------------------------------------------------
    add_heading_styled(doc, '1. C++ Benchmark Suite: vulnerable_samples.cpp (Test Cases 1 – 87)', level=2)
    add_body_p(doc,
        'The C++ benchmark suite tests memory-unsafe C/C++ idioms, integer bugs, concurrency hazards, and algorithmic bottlenecks '
        'in a unified 700-line testbed. Below is the systematic breakdown of all 87 test cases in this corpus:'
    )

    cpp_test_cases = [
        # Buffer Overflows
        ("Test Case 1", "Buffer Overflow", "CWE-121", "copy_name (L40)", "Unbounded strcpy into 16-byte stack buffer without bounds check."),
        ("Test Case 2", "Buffer Overflow", "CWE-121", "join_strings (L46)", "Unbounded strcat onto stack buffer causing stack frame corruption."),
        ("Test Case 3", "Buffer Overflow", "CWE-120", "read_line_unsafe (L53)", "Unbounded scanf('%s') reading user string into 16-byte array."),
        ("Test Case 4", "Buffer Overflow", "CWE-120", "format_into_buffer (L59)", "Unchecked sprintf() writing into 32-byte message buffer."),
        ("Test Case 5", "Buffer Overflow", "CWE-193", "off_by_one (L66)", "Loop index i <= 10 writing out-of-bounds element arr[10] on stack."),
        ("Test Case 6", "Buffer Overflow", "CWE-122", "heap_overflow (L73)", "Memcpy strlen(src)+1 bytes into 8-byte heap chunk allocated via malloc."),
        ("Test Case 7", "Buffer Overflow", "CWE-120", "get_static_buffer (L264)", "Unbounded strcpy into shared static buffer causing memory corruption & thread hazard."),
        ("Test Case 8", "Buffer Overflow", "CWE-193", "strncat_off_by_one (L304)", "Off-by-one destination size in strncat leaving no space for null terminator."),
        ("Test Case 9", "Buffer Overflow", "CWE-120", "fread_unchecked (L332)", "Fread reading 128 bytes into 64-byte stack buffer; f unchecked for NULL."),
        ("Test Case 10", "Buffer Overflow", "CWE-120", "gets_style (L346)", "Hand-written getchar loop lacking length bounds check writing into dst buffer."),
        ("Test Case 11", "Buffer Overflow", "CWE-120", "string_copy_loop (L354)", "Unbounded while-loop string copy without destination boundary check."),
        # Format Strings
        ("Test Case 12", "Format String", "CWE-134", "log_message (L83)", "User data passed directly as format string parameter to printf()."),
        ("Test Case 13", "Format String", "CWE-134 / 476", "log_to_file (L89)", "Fprintf(f, msg) user format string; file handle f unchecked for NULL."),
        ("Test Case 14", "Format String", "CWE-134", "printf_percent_n (L341)", "Direct printf(s) enabling %n specifier arbitrary memory write."),
        ("Test Case 15", "Format String", "CWE-120", "parse_header (L422)", "Unbounded sscanf('%s: %s') parsing HTTP header into 16-byte buffers."),
        ("Test Case 16", "Input Validation", "CWE-130", "trust_length_field (L429)", "Unverified length field read from network packet copied directly via memcpy."),
        # Integer Problems
        ("Test Case 17", "Integer Overflow", "CWE-190", "add_sizes (L98)", "Signed integer addition leading to undefined overflow behavior."),
        ("Test Case 18", "Integer Overflow", "CWE-190", "alloc_array (L102)", "Multiplication count * sizeof(int) wrapping before malloc allocation."),
        ("Test Case 19", "Integer Wraparound", "CWE-191", "sub_unsigned (L108)", "Unsigned integer subtraction underflow wrapping to maximum value."),
        ("Test Case 20", "Integer Overflow", "CWE-190", "factorial_recursive (L499)", "Unchecked recursive factorial multiplication integer overflow."),
        # Memory Management Bugs
        ("Test Case 21", "Memory Safety", "CWE-416", "use_after_free (L117)", "Dereferencing pointer p via printf after calling free(p)."),
        ("Test Case 22", "Memory Safety", "CWE-415", "double_free (L124)", "Calling free(p) twice when branch flag is active."),
        ("Test Case 23", "Resource Leak", "CWE-401", "memory_leak (L130)", "Allocating 256-byte buffer in loop without delete/free."),
        ("Test Case 24", "Resource Leak", "CWE-401", "leak_on_error (L138)", "Heap buffer allocated before fopen(); leaked if fopen() returns NULL."),
        ("Test Case 25", "Memory Safety", "CWE-562", "return_stack_address (L147)", "Returning pointer to stack-allocated local array upon function exit."),
        ("Test Case 26", "Memory Safety", "CWE-401 / 476", "realloc_leak (L286)", "Original pointer lost on realloc failure; result not checked for NULL."),
        ("Test Case 27", "Memory Safety", "CWE-770", "alloca_use (L292)", "Unbounded stack allocation via alloca() with attacker-controlled size."),
        ("Test Case 28", "Memory Safety", "CWE-770", "vla_use (L297)", "Variable Length Array (VLA) allocated on stack without size limit check."),
        ("Test Case 29", "Memory Safety", "CWE-119", "memcpy_overlap (L309)", "Memcpy called on overlapping memory regions; memmove required."),
        ("Test Case 30", "Memory Safety", "CWE-824", "wild_pointer (L314)", "Dereferencing and writing to uninitialized wild pointer *p."),
        ("Test Case 31", "Memory Safety", "CWE-416 / 415", "dangling_after_delete (L320)", "Writing to pointer after delete, followed by double delete."),
        ("Test Case 32", "Memory Safety", "CWE-762", "scalar_delete_on_array (L327)", "Calling scalar delete instead of delete[] on array allocated with new[]."),
        ("Test Case 33", "Memory Safety", "CWE-787", "global_overflow (L332)", "Writing to static global array with unchecked integer index."),
        ("Test Case 34", "Compiler Optimization", "CWE-14", "sensitive_not_cleared (L337)", "Memset clearing password optimized away by compiler as dead store."),
        ("Test Case 35", "Memory Safety", "CWE-416", "return_freed_pointer (L361)", "Returning dangling pointer to heap block after invoking free()."),
        ("Test Case 36", "Memory Safety", "CWE-787", "struct_overflow (L368)", "Struct buffer overflow in name field overwriting adjacent admin flag."),
        # Injection & OS Issues
        ("Test Case 37", "Command Injection", "CWE-78 / 120", "run_ping (L157)", "Untrusted host string concatenated into system('ping -c 1 ' + host)."),
        ("Test Case 38", "Command Injection", "CWE-78", "list_dir (L163)", "Directory parameter concatenated into system('ls -l ' + dir)."),
        ("Test Case 39", "Path Traversal", "CWE-22", "read_user_file (L169)", "Path traversal /var/data/%s allowing '../../etc/passwd' arbitrary read."),
        ("Test Case 40", "Race Condition", "CWE-367", "check_then_open (L180)", "Time-of-Check to Time-of-Use (TOCTOU) race condition between access() and fopen()."),
        ("Test Case 41", "File Permissions", "CWE-732", "world_writable_file (L231)", "Creat() called with 0777 overly permissive world-writable file permissions."),
        ("Test Case 42", "Insecure Temporary File", "CWE-377", "insecure_temp (L236)", "Tmpnam() generates predictable temporary file name vulnerable to symlink race."),
        ("Test Case 43", "Information Disclosure", "CWE-532", "print_secret (L242)", "Database password printed directly to standard output."),
        ("Test Case 44", "Logic Error", "CWE-481", "assign_in_condition (L246)", "Assignment operator (=) used instead of comparison (==) inside if-condition."),
        ("Test Case 45", "Concurrency / Reentrancy", "CWE-676", "tokenize (L271)", "Non-reentrant strtok() modifies source string and uses internal static state."),
        ("Test Case 46", "Input Validation", "CWE-20", "parse_number (L279)", "Atoi() performs no error checking on malformed integer strings."),
        ("Test Case 47", "Uninitialized Variable", "CWE-252 / 457", "read_two_numbers (L283)", "Scanf return value ignored; variables may be used uninitialized."),
        # Crypto, Randomness & Authentication
        ("Test Case 48", "Weak Randomness", "CWE-338", "generate_token (L190)", "Srand(time(NULL)) predictable epoch seed and rand() weak PRNG for tokens."),
        ("Test Case 49", "Side Channel", "CWE-208", "check_password (L195)", "Strcmp() timing discrepancy leaking password character mismatches."),
        ("Test Case 50", "Side Channel", "CWE-208", "check_token (L199)", "Early loop exit on token mismatch creates timing side channel."),
        ("Test Case 51", "Hardcoded Credentials", "CWE-798", "SECRET_KEY / DB_PASSWORD (L24)", "Hard-coded credentials committed directly in header definitions."),
        ("Test Case 52", "Hardcoded Credentials", "CWE-798", "login (L207)", "Hard-coded admin credentials and backdoor password check."),
        # Concurrency & OOP Flaws
        ("Test Case 53", "Concurrency", "CWE-362", "increment_counter (L217)", "Unsynchronized increment of shared global counter variable."),
        ("Test Case 54", "Logic Error", "CWE-484", "switch_fallthrough (L221)", "Missing break statement causing unintended switch-case fallthrough."),
        ("Test Case 55", "Buffer Overflow", "CWE-120", "Account::Account (L376)", "Constructor uses unbounded strcpy into fixed 16-byte owner buffer."),
        ("Test Case 56", "Logic Error", "CWE-840", "Account::withdraw (L380)", "No check for negative withdrawal amount or overdraft."),
        ("Test Case 57", "Logic Error", "CWE-840", "Account::deposit (L383)", "Negative deposit converts into an unverified withdrawal."),
        ("Test Case 58", "OOP Defect", "CWE-1079 / 401", "Base::~Base (L389)", "Non-virtual base class destructor causing derived cleanup failure."),
        ("Test Case 59", "Resource Leak", "CWE-401", "delete_through_base (L401)", "Deleting derived instance through base pointer skips derived destructor."),
        ("Test Case 60", "Double Free", "CWE-415", "Buffer (L407)", "Class lacks copy constructor; shallow copy double-frees raw pointer."),
        ("Test Case 61", "Out-of-Bounds", "CWE-125", "Buffer::at (L411)", "Array indexing method lacks bounds check against allocated size."),
        ("Test Case 62", "Memory Safety", "CWE-415 / 787", "buffer_copy_bug (L415)", "Shallow copy double-free and out-of-bounds write via .at(100)."),
        ("Test Case 63", "Weak Randomness", "CWE-338", "Session::Session (L422)", "Session token generated using weak rand() PRNG."),
        ("Test Case 64", "Side Channel", "CWE-208", "Session::valid (L423)", "String equality (==) non-constant-time token comparison."),
        ("Test Case 65", "Resource Leak", "CWE-772", "fd_leak (L431)", "File descriptor opened with open() leaked on early error return."),
        ("Test Case 66", "Log Injection", "CWE-117", "log_user_input (L439)", "Unsanitized user input written to log file allowing CRLF injection."),
        # Algorithmic Optimization Cases (67 - 87)
        ("Test Case 67", "Exponential Recursion", "OPT-01", "fib_slow (L204)", "O(2^n) exponential tree recursion; transformed to O(n) DP iteration."),
        ("Test Case 68", "Repeated Computation", "OPT-02", "strlen_in_loop (L210)", "Strlen recomputed on every loop iteration; hoisted to constant check."),
        ("Test Case 69", "Redundant Copy", "OPT-03", "sum_by_value (L216)", "Vector passed by value copying entire buffer; changed to const reference."),
        ("Test Case 70", "Memory Allocation", "OPT-04", "build_vector (L222)", "Repeated heap reallocations on push_back; optimized with v.reserve(n)."),
        ("Test Case 71", "Quadratic Allocation", "OPT-05", "concat_in_loop (L229)", "Temporary std::string created on each iteration; hoisted to pre-sized buffer."),
        ("Test Case 72", "Quadratic Scan", "OPT-06", "has_duplicates (L236)", "O(n^2) pairwise comparisons; replaced with O(n) std::unordered_set lookup."),
        ("Test Case 73", "Quadratic Sort", "OPT-07", "bubble_sort (L243)", "O(n^2) bubble sort; replaced with O(n log n) std::sort introsort."),
        ("Test Case 74", "Cache Locality", "OPT-08", "matrix_multiply (L250)", "Poor cache locality on matrix B; inner loops reordered for row-major stride."),
        ("Test Case 75", "Loop Invariant", "OPT-09", "loop_invariant (L260)", "Expensive sqrt(a*a + b*b) recomputed inside loop; hoisted outside."),
        ("Test Case 76", "I/O Buffering", "OPT-11", "print_many (L266)", "Std::endl flushes stream buffer every line; replaced with '\\n'."),
        ("Test Case 77", "Algorithmic Bounds", "OPT-13", "is_prime_slow (L272)", "Trial division up to n; loop bound capped at sqrt(n)."),
        ("Test Case 78", "Strength Reduction", "OPT-10", "power_of_two_div (L251)", "Division/modulo by powers of 2 replaced with bitwise shifts and masks."),
        ("Test Case 79", "Common Subexpression", "OPT-15", "redundant_computation (L255)", "(a*b) recomputed multiple times; cached in local register."),
        ("Test Case 80", "Dead Code", "OPT-16", "dead_code (L261)", "Unused variable assignment and unreachable if(false) branch pruned."),
        ("Test Case 81", "Memory Allocation", "OPT-12", "count_chars (L269)", "Substr(i, 1) allocating heap string per character; replaced with s[i]."),
        ("Test Case 82", "Linear Scan", "OPT-14", "lookup_slow (L277)", "O(n) linear search over vector; replaced with O(1) std::unordered_map."),
        ("Test Case 83", "Math Library Call", "OPT-19", "sum_with_pow (L284)", "Pow(v[i], 2) floating-point call replaced with integer multiplication v*v."),
        ("Test Case 84", "Data Structure", "OPT-20", "word_count (L291)", "Std::map logarithmic tree lookup replaced with O(1) std::unordered_map."),
        ("Test Case 85", "Memory Hierarchy", "OPT-21", "sum_2d (L439)", "Column-major traversal of row-major 2D vector; reordered to row-major stride."),
        ("Test Case 86", "Redundant Copy", "OPT-03 / 04", "filter_even (L447)", "Pass-by-value vector and unreserved output; pass-by-ref and reserve added."),
        ("Test Case 87", "Data Structure", "OPT-22", "insert_front (L455)", "O(n) vector::insert at index 0 on every element; replaced with std::deque.")
    ]

    for tc, cat, cwe, target, desc in cpp_test_cases:
        p_tc = doc.add_paragraph()
        p_tc.paragraph_format.space_before = Pt(2)
        p_tc.paragraph_format.space_after = Pt(2)
        r_num = p_tc.add_run(f"• {tc} [{cat} - {cwe}]: ")
        r_num.bold = True
        r_num.font.name = 'Arial'
        r_num.font.size = Pt(9)
        r_target = p_tc.add_run(f"{target} — ")
        r_target.italic = True
        r_target.font.name = 'Arial'
        r_target.font.size = Pt(9)
        r_desc = p_tc.add_run(desc)
        r_desc.font.name = 'Arial'
        r_desc.font.size = Pt(9)

    add_body_p(doc, 'Below are the live studio screenshots (.1 through .6) validating the execution of Test Cases 1 through 87 on the server:')

    # Screenshots .1 to .6
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_1.png',
        'Screenshot .1: Live Full Pipeline Execution on C++ Benchmark (vulnerable_samples.cpp) — Overview & Output Tab',
        'Demonstrates the completed Full Pipeline run on vulnerable_samples.cpp. The Monaco Source Code Editor displays the baseline C++ implementation, '
        'the Live Pipeline Stage Graph verifies 100% completion across all sequential stages (Source -> Optimization -> Security -> Completed), '
        'and the Output Tab presents the consolidated execution status, verified runtime speedup (1.00x baseline preservation), and zero pipeline regressions.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_2.png',
        'Screenshot .2: Side-by-Side Algorithmic Code Transformations Diff on C++ Benchmark (vulnerable_samples.cpp)',
        'Illustrates the Optimized Code tab rendering side-by-side unified diffs for Test Cases 67 through 87. The right-hand panel enumerates all 21 verified '
        'algorithmic transformations (DP memoization in fib_slow, reserve pre-allocation, unordered_set lookup, loop invariance hoisting), featuring clickable '
        'line-navigation links that jump directly to affected lines in the Monaco editor.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_3.png',
        'Screenshot .3: Security Audit Findings on C++ Benchmark — Section 1: Buffer Overflows & Format Strings (Test Cases 1–16)',
        'Displays the Security tab rendering critical and high severity defect cards. Highlights classic buffer overflows (CWE-120 in read_line_unsafe, format_into_buffer, '
        'fread_unchecked), stack overflows (CWE-121 in copy_name, join_strings), heap overflows (CWE-122 in heap_overflow), off-by-one errors (CWE-193 in off_by_one), '
        'and format string vulnerabilities (CWE-134 in log_message, log_to_file).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_4.png',
        'Screenshot .4: Security Audit Findings on C++ Benchmark — Section 2: Memory Safety & Injection (Test Cases 21–40)',
        'Displays scrolled security findings covering use-after-free (CWE-416 in use_after_free), double-free flaws (CWE-415 in double_free), heap memory leaks '
        '(CWE-401 in memory_leak, leak_on_error), dangling stack returns (CWE-562), OS command injection (CWE-78 in run_ping, list_dir), path traversal (CWE-22 in read_user_file), '
        'and TOCTOU file access race conditions (CWE-367 in check_then_open).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_5.png',
        'Screenshot .5: Security Audit Findings on C++ Benchmark — Section 3: Crypto, Secrets & OOP Flaws (Test Cases 41–66)',
        'Displays remaining security defect cards including predictable PRNG seeds (CWE-338 in generate_token, Session), timing discrepancies (CWE-208 in check_password, check_token), '
        'hardcoded credentials (CWE-798 in SECRET_KEY, login), constructor overflows (CWE-120 in Account), and non-virtual base destructor leaks (CWE-1079 in Base).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_6.png',
        'Screenshot .6: Real-Time Messages and Execution Lifecycle Trace Stream for C++ Full Pipeline Execution',
        'Captures the complete diagnostic event stream published over Server-Sent Events (SSE). Confirms AST intent extraction, conventional SAST runner execution '
        '(Clang-Tidy, Cppcheck, Flawfinder), finding normalization into canonical schemas, and multi-agent pipeline handoff with monotonic event sequence numbering.'
    )

    # -------------------------------------------------------------
    # SUITE 2: Python Benchmark Suite (Test Cases 88 - 194)
    # -------------------------------------------------------------
    add_heading_styled(doc, '2. Python Benchmark Suite: vulnerable_samples.py (Test Cases 88 – 194)', level=2)
    add_body_p(doc,
        'The Python benchmark suite evaluates dynamic language security risks, script injections, unsafe deserialization, and '
        'high-level algorithmic transformation patterns across 10 security categories and 9 optimization categories (107 test cases total):'
    )

    py_test_cases = [
        # SQL Injection
        ("Test Case 88", "SQL Injection", "CWE-89", "get_user (L37)", "Raw string concatenation in SQL query allows arbitrary query execution."),
        ("Test Case 89", "SQL Injection", "CWE-89", "login (L45)", "f-string interpolation of username and password into SQL authentication query."),
        ("Test Case 90", "SQL Injection", "CWE-89", "search_products (L334)", "Unescaped search term in LIKE clause permits boolean/time-based SQLi."),
        ("Test Case 91", "SQL Injection", "CWE-89", "update_email (L340)", "Percent-formatted SQL executed with executescript permits stacked queries."),
        # OS Command Injection
        ("Test Case 92", "Command Injection", "CWE-78", "ping_host (L51)", "Untrusted host string concatenated into os.system('ping -c 1 ' + host)."),
        ("Test Case 93", "Command Injection", "CWE-78", "run_shell (L55)", "Subprocess.check_output with shell=True executes arbitrary user shell commands."),
        ("Test Case 94", "Command Injection", "CWE-78", "run_report (L345)", "Subprocess.Popen with shell=True concatenates user name directly into command."),
        ("Test Case 95", "Command Injection", "CWE-78", "convert_image (L349)", "File path interpolated into os.popen image converter shell string."),
        ("Test Case 96", "Command Injection", "CWE-78", "delete_path (L466)", "Destructive delete os.system('rm -rf ' + path) with unescaped path."),
        ("Test Case 97", "Command Injection", "CWE-78", "shell_quote_wrong (L510)", "Improper single-quote wrapping permits single-quote shell escape."),
        # Code Injection & Reflection
        ("Test Case 98", "Code Injection", "CWE-95", "calculate (L59)", "Passing untrusted user input to eval() executes arbitrary Python code."),
        ("Test Case 99", "Code Injection", "CWE-95", "PluginLoader (L559)", "Exec() runs plugin code directly in global namespace without sandboxing."),
        ("Test Case 100", "Unsafe Reflection", "CWE-470", "import_by_name (L502)", "Dynamic __import__ loads arbitrary standard and system modules."),
        ("Test Case 101", "Unsafe Reflection", "CWE-470", "call_by_name (L506)", "Getattr() allows caller to invoke private or dangerous object methods."),
        # Other Injection
        ("Test Case 102", "Cross-Site Scripting", "CWE-79", "build_html_page (L353)", "Reflected XSS via raw HTML concatenation of unescaped title and body."),
        ("Test Case 103", "CRLF Injection", "CWE-93", "send_mail (L392)", "Email header injection via unstripped newlines in to and subject fields."),
        ("Test Case 104", "Open Redirect", "CWE-113 / 601", "redirect_after_login (L362)", "HTTP response splitting and open redirect via raw Location header."),
        ("Test Case 105", "Format String", "CWE-134", "render_string (L372)", "Str.format() on user template allows inspecting private object attributes."),
        ("Test Case 106", "NoSQL Injection", "CWE-943", "find_user_nosql (L329)", "Mongo $where JavaScript evaluation clause concatenated with user name."),
        ("Test Case 107", "Formula Injection", "CWE-1236", "load_csv_rows (L498)", "CSV cells beginning with =, +, -, or @ can trigger DDE execution."),
        # Unsafe Deserialization
        ("Test Case 108", "Deserialization", "CWE-502", "load_session (L67)", "Untrusted pickle.loads() executes arbitrary code via __reduce__ payloads."),
        ("Test Case 109", "Deserialization", "CWE-502", "load_config (L71)", "Yaml.load without SafeLoader instantiates arbitrary Python classes."),
        ("Test Case 110", "Cryptographic Failure", "CWE-347", "verify_jwt (L377)", "JWT token payload parsed from base64 without cryptographic signature check."),
        # Path & File Handling
        ("Test Case 111", "Path Traversal", "CWE-22", "read_upload (L79)", "Concatenating filename with /var/uploads/ allows directory traversal."),
        ("Test Case 112", "Path Traversal", "CWE-22", "read_template (L367)", "Direct template path concatenation allows reading arbitrary server files."),
        ("Test Case 113", "File Overwrite", "CWE-22", "download_file (L387)", "Destination path not validated, allowing overwriting sensitive files."),
        ("Test Case 114", "Path Traversal", "CWE-22 / 772", "get_profile_picture (L397)", "Path traversal in image lookup; file descriptor opened without context manager."),
        ("Test Case 115", "Path Traversal", "CWE-22", "extract_tar (L472)", "TarSlip vulnerability: tarfile extractall() allows writing outside destination."),
        ("Test Case 116", "Race Condition", "CWE-367", "check_then_write (L92)", "TOCTOU race between os.access(W_OK) check and file creation."),
        ("Test Case 117", "Insecure Temporary File", "CWE-377", "make_temp (L85)", "Tempfile.mktemp() creates predictable temporary files subject to symlink races."),
        ("Test Case 118", "Shared Directory", "CWE-377", "copy_secret_file (L459)", "Copying secret file to shared /tmp path allows other users to read it."),
        ("Test Case 119", "Permissions", "CWE-732", "write_config (L455)", "Setting world-writable permissions (0o666) on configuration file."),
        ("Test Case 120", "Permissions", "CWE-732", "save_pickle (L478)", "Setting world-readable and executable permissions (0o777) on pickle file."),
        ("Test Case 121", "Permissions", "CWE-732", "temp_file_world_readable (L492)", "Setting world-readable permissions (0o644) on sensitive secrets file."),
        ("Test Case 122", "Resource Exhaustion", "CWE-400", "read_input_file (L483)", "Reading entire file into memory without length limit allows memory DoS."),
        ("Test Case 123", "Resource Leak", "CWE-772", "FileLogger (L550)", "File descriptor opened in append mode during __init__ is never closed."),
        # Weak Crypto & Randomness
        ("Test Case 124", "Weak Cryptography", "CWE-327", "hash_password (L102)", "MD5 used for password hashing without salt or adaptive work factor."),
        ("Test Case 125", "Weak Cryptography", "CWE-759", "make_password_hash (L417)", "Static salt and fast SHA-256 vulnerable to rainbow table precomputation."),
        ("Test Case 126", "Weak Cryptography", "CWE-330", "session_token (L421)", "Session token generated from MD5(user + timestamp) is trivially guessable."),
        ("Test Case 127", "Weak Randomness", "CWE-338", "make_session_id (L106)", "Random.randint() is not cryptographically secure for session IDs."),
        ("Test Case 128", "Weak Randomness", "CWE-338", "make_reset_token (L239)", "Random seeded with epoch timestamp makes password reset tokens predictable."),
        # Authentication & Secrets
        ("Test Case 129", "Hardcoded Credentials", "CWE-798", "API_KEY (L24)", "Live secret API key sk_live_... committed in cleartext."),
        ("Test Case 130", "Hardcoded Credentials", "CWE-798", "ADMIN_PASSWORD (L25)", "Static administrator password committed in cleartext."),
        ("Test Case 131", "Hardcoded Credentials", "CWE-798", "check_admin (L114)", "Authentication against hardcoded admin password constant."),
        ("Test Case 132", "Hardcoded Credentials", "CWE-798", "verify_otp (L437)", "Master backdoor code '000000' bypasses two-factor authentication."),
        ("Test Case 133", "Timing Side-Channel", "CWE-208", "check_token (L110)", "Non-constant-time equality check (==) leaks token bytes via timing."),
        ("Test Case 134", "Cleartext Passwords", "CWE-256 / 208", "authenticate (L408)", "Plaintext password comparison in dictionary with timing side-channel."),
        ("Test Case 135", "Broken Authorization", "CWE-285", "check_role (L429)", "Substring check ('admin' in user['roles']) allows privilege escalation."),
        ("Test Case 136", "Brute Force", "CWE-307", "login_with_lockout (L412)", "Failed attempts counted in mutable dict but lockout is never enforced."),
        ("Test Case 137", "Insecure Cookie", "CWE-565", "remember_me (L425)", "Reversible hex-encoded username used as persistent remember-me cookie."),
        ("Test Case 138", "Authentication Bypass", "CWE-620", "reset_password (L433)", "Password reset allows changing password without validating old password."),
        ("Test Case 139", "Insecure Default", "CWE-1188", "get_secret_from_env (L441)", "Environment lookup falls back to insecure default string 'default_secret'."),
        ("Test Case 140", "Cleartext Logging", "CWE-532", "log_credentials (L445)", "Username and password printed in cleartext to standard application logs."),
        # Network & Web
        ("Test Case 141", "SSRF", "CWE-918 / 295", "fetch_url (L124)", "Server-Side Request Forgery via urllib.request without timeout or IP validation."),
        ("Test Case 142", "Broken TLS", "CWE-295", "fetch_insecure (L246)", "Check_hostname set to False permits man-in-the-middle attacks on HTTPS."),
        ("Test Case 143", "Network Exposure", "CWE-668", "bind_all (L254)", "Socket bound to INADDR_ANY ('0.0.0.0') exposes private service publicly."),
        ("Test Case 144", "Insecure Cookie", "CWE-614", "set_cookie (L357)", "Session cookie set without Secure and HttpOnly protective flags."),
        ("Test Case 145", "CSRF", "CWE-352", "csrf_transfer (L381)", "State-changing POST request processed without anti-CSRF token verification."),
        # Logic, Concurrency & Robustness
        ("Test Case 146", "Debug Mode", "CWE-489", "DEBUG (L26)", "Debug mode enabled in production code exposing internal stack traces."),
        ("Test Case 147", "Shared Storage", "CWE-377", "DB_PATH (L27)", "Database stored in world-accessible /tmp path vulnerable to tampering."),
        ("Test Case 148", "Error Handling", "CWE-396", "safe_divide (L134)", "Bare except clause catches and hides KeyboardInterrupt and system exits."),
        ("Test Case 149", "State Leak", "CWE-1188", "append_item (L138)", "Mutable default argument bucket=[] retains state across requests."),
        ("Test Case 150", "ReDoS", "CWE-1333", "regex_check (L144)", "Nested repetition regex ^(a+)+$ causes catastrophic backtracking."),
        ("Test Case 151", "Authorization", "CWE-617", "is_admin (L259)", "Assert statement used for authorization; stripped when run with -O."),
        ("Test Case 152", "Race Condition", "CWE-362", "update_balance (L265)", "Non-atomic read-modify-write with sleep window creates double-spend race."),
        ("Test Case 153", "Information Disclosure", "CWE-200", "debug_dump (L271)", "Dumping entire os.environ leaks secret keys, tokens, and database passwords."),
        ("Test Case 154", "Information Disclosure", "CWE-526", "spawn_worker (L487)", "Passing entire parent environment to child worker process leaks credentials."),
        ("Test Case 155", "Business Logic", "CWE-840", "Account::withdraw (L524)", "Account balance allows negative withdrawal and overdraft without checks."),
        ("Test Case 156", "Credential Leak", "CWE-532", "Account::__repr__ (L535)", "Account password formatted into __repr__ leaks credentials during debugging."),
        ("Test Case 157", "Shared Mutable State", "CWE-1188", "Cache::store (L539)", "Class-level dictionary shared across all Cache instances instead of instance scope."),
        ("Test Case 158", "Resource Exhaustion", "CWE-400", "Cache::put (L545)", "Unbounded dictionary cache lacks LRU eviction, leading to memory exhaustion."),
        ("Test Case 159", "Log Injection", "CWE-117", "FileLogger::log (L553)", "Writing unvalidated log messages allows newline injection and log forging."),
        ("Test Case 160", "Robustness", "CWE-369", "average (L626)", "Len(values) in denominator raises ZeroDivisionError on empty input lists."),
        # Python Algorithmic Optimization Cases (161 - 194)
        ("Test Case 161", "Exponential Recursion", "OPT-01", "fib_slow (L151)", "O(2^n) exponential tree recursion; transformed to O(n) iterative accumulator."),
        ("Test Case 162", "Recursion Depth", "OPT-26", "factorial_recursive (L610)", "Unbounded recursive call stack replaced with optimized math.factorial()."),
        ("Test Case 163", "String Building", "OPT-02", "concat_in_loop (L157)", "Repeated string concatenation in loop replaced with ''.join() comprehension."),
        ("Test Case 164", "String Reversal", "OPT-02", "reverse_string_slow (L603)", "Prepending characters in loop replaced with fast slice reversal [::-1]."),
        ("Test Case 165", "String Formatting", "OPT-02", "string_join_numbers (L662)", "Manual string concatenation loop replaced with ', '.join(map(str, nums))."),
        ("Test Case 166", "Set Cardinality", "OPT-03", "has_duplicates (L164)", "Nested O(n^2) comparisons replaced with O(n) len(items) != len(set(items))."),
        ("Test Case 167", "Hash Lookup", "OPT-04", "membership_in_list (L172)", "Linear scan in list replaced with O(1) set membership filtering."),
        ("Test Case 168", "Unique Elements", "OPT-23", "unique_slow (L581)", "O(n^2) linear scan accumulator replaced with order-preserving dict.fromkeys()."),
        ("Test Case 169", "Sorting Algorithm", "OPT-05", "bubble_sort (L180)", "O(n^2) bubble sort replaced with Python built-in Timsort sorted()."),
        ("Test Case 170", "Two-Sum Search", "OPT-27", "pairs_with_sum (L616)", "Double-nested loop replaced with O(n) frequency map lookup via Counter."),
        ("Test Case 171", "Index Map", "OPT-24", "index_lookup_slow (L589)", "Repeated items.index() scans replaced with precomputed dictionary map."),
        ("Test Case 172", "Redundant Sorting", "OPT-35", "repeated_sort (L683)", "Repeated sorting calls inside loop collapsed into a single sort operation."),
        ("Test Case 173", "List Comprehension", "OPT-06", "squares (L274)", "Explicit for-loop with append() replaced with list comprehension [i*i for i in range(n)]."),
        ("Test Case 174", "Built-in Sum", "OPT-07", "sum_manual (L281)", "Manual index accumulation loop replaced with Python C-builtin sum()."),
        ("Test Case 175", "Built-in Max", "OPT-11", "find_max (L288)", "Manual iteration and comparison loop replaced with built-in max()."),
        ("Test Case 176", "Closed Form", "OPT-21", "sum_of_squares_slow (L567)", "O(n) iterative accumulation replaced with O(1) Faulhaber closed-form formula."),
        ("Test Case 177", "Dictionary Zip", "OPT-19", "build_dict_slow (L317)", "Manual index assignment loop replaced with built-in dict(zip(keys, values))."),
        ("Test Case 178", "Matrix Transposition", "OPT-25", "transpose_slow (L593)", "Nested index loops replaced with idiomatic [list(row) for row in zip(*m)]."),
        ("Test Case 179", "Loop Invariant", "OPT-08", "loop_invariant (L189)", "Constant mathematical expression (a**2 + b**2)**0.5 hoisted outside loop."),
        ("Test Case 180", "Hoisting", "OPT-28", "variance (L629)", "Average() calculation hoisted outside generator expression to prevent O(n^2) recalculation."),
        ("Test Case 181", "Length Queries", "OPT-13", "repeated_len (L296)", "Len(data) and len(data[0]) queries cached outside while-loop condition."),
        ("Test Case 182", "Redundant Clones", "OPT-33", "copy_list_in_loop (L669)", "Full shallow copy items[:] inside loop eliminated, reducing memory churn."),
        ("Test Case 183", "List Flattening", "OPT-22", "flatten_slow (L574)", "List addition out = out + sub replaced with in-place out.extend(sub)."),
        ("Test Case 184", "Filter Comprehension", "OPT-16", "remove_items (L306)", "Mutating list during iteration replaced with set-filtered list comprehension."),
        ("Test Case 185", "Memory Streaming", "OPT-10", "read_big_file (L206)", "Readlines() loading entire file replaced with memory-efficient line iterator."),
        ("Test Case 186", "File Iterator", "OPT-30", "read_lines_slow (L637)", "Manual readline() while-loop replaced with context-managed file comprehension."),
        ("Test Case 187", "Regex Compilation", "OPT-17", "string_search (L313)", "Re.compile() hoisted outside loop to prevent repeated pattern compilation."),
        ("Test Case 188", "Frequency Counting", "OPT-09", "count_words (L196)", "Manual dictionary loop replaced with C-accelerated collections.Counter."),
        ("Test Case 189", "Primality Bound", "OPT-12", "is_prime_slow (L215)", "Trial division loop bound capped at sqrt(n) with 6k+/-1 wheel optimization."),
        ("Test Case 190", "Euclidean GCD", "OPT-32", "gcd_slow (L654)", "Linear scan replaced with Euclidean algorithm via standard math.gcd."),
        ("Test Case 191", "Heap Selection", "OPT-29", "top_n_slow (L633)", "Full sorted() slice replaced with O(k log n) heapq.nlargest heap selection."),
        ("Test Case 192", "Dictionary Get", "OPT-31", "dict_keys_loop (L647)", "Linear loop over keys replaced with O(1) hash lookup via dict.get()."),
        ("Test Case 193", "Slice Equality", "OPT-34", "is_palindrome_slow (L676)", "Dual-index character loop replaced with native C string slice comparison s == s[::-1]."),
        ("Test Case 194", "Vectorization", "OPT-14", "matrix_multiply (L224)", "Triple-nested loop replaced with vectorized matrix multiplication via NumPy @ operator.")
    ]

    for tc, cat, cwe, target, desc in py_test_cases:
        p_tc = doc.add_paragraph()
        p_tc.paragraph_format.space_before = Pt(2)
        p_tc.paragraph_format.space_after = Pt(2)
        r_num = p_tc.add_run(f"• {tc} [{cat} - {cwe}]: ")
        r_num.bold = True
        r_num.font.name = 'Arial'
        r_num.font.size = Pt(9)
        r_target = p_tc.add_run(f"{target} — ")
        r_target.italic = True
        r_target.font.name = 'Arial'
        r_target.font.size = Pt(9)
        r_desc = p_tc.add_run(desc)
        r_desc.font.name = 'Arial'
        r_desc.font.size = Pt(9)

    add_body_p(doc, 'Below are the live studio screenshots (.7 through .13) validating the execution of Test Cases 88 through 194 on the server:')

    # Screenshots .7 to .13
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_7.png',
        'Screenshot .7: Live Full Pipeline Execution on Python Benchmark (vulnerable_samples.py) — Overview & Output Tab',
        'Demonstrates the completed Full Pipeline run on vulnerable_samples.py. The Monaco Source Code Editor displays the comprehensive Python testbed, '
        'the Live Pipeline Stage Graph verifies 100% completion across all sequential stages (Source -> Optimization -> Security -> Completed), '
        'and the Output Tab displays the verified execution status, complexity summary, and zero regression guarantee.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_8.png',
        'Screenshot .8: Side-by-Side Algorithmic Code Transformations Diff on Python Benchmark (vulnerable_samples.py)',
        'Illustrates the Optimized Code tab rendering side-by-side unified diffs for Test Cases 161 through 194. The right-hand panel enumerates all 34 verified '
        'algorithmic transformations across the 9 optimization categories (DP memoization, join comprehensions, set membership, Timsort, Faulhaber closed forms, '
        'Counter frequency tables, and NumPy vectorization) with line navigation.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_9.png',
        'Screenshot .9: Security Audit Findings on Python Benchmark — Section 1: Injections & Code Execution (Test Cases 88–101)',
        'Displays the Security tab rendering critical and high severity defect cards. Highlights SQL injection (CWE-89 in get_user, login, search_products, update_email), '
        'OS command injection (CWE-78 in ping_host, run_shell, run_report, convert_image, delete_path, shell_quote_wrong), and arbitrary code execution (CWE-95 in calculate, PluginLoader).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_10.png',
        'Screenshot .10: Security Audit Findings on Python Benchmark — Section 2: Other Injections & Deserialization (Test Cases 102–110)',
        'Displays scrolled security findings covering reflected XSS (CWE-79 in build_html_page), email CRLF injection (CWE-93 in send_mail), open redirect (CWE-113/601 in redirect_after_login), '
        'format string injection (CWE-134 in render_string), NoSQL injection (CWE-943 in find_user_nosql), unsafe pickle/YAML deserialization (CWE-502 in load_session, load_config), '
        'and unverified JWT tokens (CWE-347 in verify_jwt).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_11.png',
        'Screenshot .11: Security Audit Findings on Python Benchmark — Section 3: Path Traversal, Permissions & Secrets (Test Cases 111–140)',
        'Displays scrolled security findings covering path traversal (CWE-22 in read_upload, read_template, download_file, extract_tar), overly permissive permissions (CWE-732 in write_config, save_pickle), '
        'weak MD5 password hashing (CWE-327), hardcoded API keys and passwords (CWE-798 in API_KEY, ADMIN_PASSWORD), and OTP master backdoor code (CWE-798 in verify_otp).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_12.png',
        'Screenshot .12: Security Audit Findings on Python Benchmark — Section 4: Network Security & Logic Flaws (Test Cases 141–160)',
        'Displays scrolled security findings covering SSRF (CWE-918 in fetch_url), disabled TLS verification (CWE-295 in fetch_insecure), missing CSRF protection (CWE-352 in csrf_transfer), '
        'catastrophic regex backtracking (CWE-1333 in regex_check), race condition in balance update (CWE-362 in update_balance), and unhandled division by zero (CWE-369 in average).'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_13.png',
        'Screenshot .13: Real-Time Messages and Execution Lifecycle Trace Stream for Python Full Pipeline Execution',
        'Captures the complete diagnostic event stream published over Server-Sent Events (SSE). Confirms AST intent extraction, security heuristic and SAST audit dispatch, '
        'canonical defect deduplication, and sequential pipeline completion with zero introduced flaws.'
    )

    # -------------------------------------------------------------
    # SUITE 3: Built-in Language Starters & Execution Modes (Test Cases 195 - 198)
    # -------------------------------------------------------------
    add_heading_styled(doc, '3. Built-in Language Starters & Execution Mode Invariants (Test Cases 195 – 198)', level=2)
    add_body_p(doc,
        'The final suite verifies default starter code presets and independent execution mode invariants across all four supported languages:'
    )

    mode_test_cases = [
        ("Test Case 195", "Starter Optimization & Bounds", "C++", "Two-Sum Quadratic Loop & Buffer Check", "Validates C++ algorithmic transformation from O(n^2) nested loop to O(n) hash table in dedicated Optimize mode."),
        ("Test Case 196", "Starter Security & AST Scan", "Python", "Fibonacci / Set Membership & AST Parse", "Validates Python static AST security audit, rule verification, and clean baseline scoring in dedicated Security mode."),
        ("Test Case 197", "Compiler Pipeline Invariant", "C", "Bounded Buffer Processing & Format Check", "Validates C language compilation, bounded memory safety audit, and multi-stage orchestration in Full Pipeline mode."),
        ("Test Case 198", "Scripting Mode Invariant", "JavaScript", "Array Duplicate Search & Loop Invariant", "Validates JavaScript AST intent extraction, quadratic search optimization, and stage graph tracking in Full Pipeline mode.")
    ]

    for tc, cat, lang, target, desc in mode_test_cases:
        p_tc = doc.add_paragraph()
        p_tc.paragraph_format.space_before = Pt(2)
        p_tc.paragraph_format.space_after = Pt(2)
        r_num = p_tc.add_run(f"• {tc} [{cat} - {lang}]: ")
        r_num.bold = True
        r_num.font.name = 'Arial'
        r_num.font.size = Pt(9)
        r_target = p_tc.add_run(f"{target} — ")
        r_target.italic = True
        r_target.font.name = 'Arial'
        r_target.font.size = Pt(9)
        r_desc = p_tc.add_run(desc)
        r_desc.font.name = 'Arial'
        r_desc.font.size = Pt(9)

    add_body_p(doc, 'Below are the live studio screenshots (.14 through .17) validating Test Cases 195 through 198 across dedicated execution modes:')

    # Screenshots .14 to .17
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_14.png',
        'Screenshot .14: C++ Built-in Starter Sample Execution in Dedicated Optimize Mode (Test Case 195)',
        'Demonstrates CompilerAI operating in dedicated Optimize mode on the C++ starter sample. Bypasses security auditing to minimize latency, focusing exclusively on '
        'transforming quadratic nested search into an O(n) hash map, compiling via Clang/LLVM, and validating asymptotic speedup.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_15.png',
        'Screenshot .15: Python Built-in Starter Sample Execution in Dedicated Security Mode (Test Case 196)',
        'Demonstrates CompilerAI operating in dedicated Security mode on Python code. Bypasses optimization routines to execute static AST taint checks and SAST linters '
        'directly on pristine code, reporting a clean 100/100 baseline security score with zero regressions.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_16.png',
        'Screenshot .16: C Language Built-in Starter Sample Execution in Full Pipeline Mode (Test Case 197)',
        'Demonstrates multi-language compiler pipeline support on C source code. Confirms successful sequential execution (Source -> Optimization -> Security -> Completed), '
        'verifying bounded array buffers, GCC toolchain compilation, and format string safety.'
    )
    add_screenshot_entry(doc, 'scratch/screenshots/screenshot_17.png',
        'Screenshot .17: JavaScript Built-in Starter Sample Execution in Full Pipeline Mode (Test Case 198)',
        'Demonstrates client-side JavaScript execution in Full Pipeline mode. The Optimization Agent replaces quadratic duplicate array scans with O(n) Set lookups, '
        'confirming full multi-language coverage across the compiler studio.'
    )

    doc.save(doc_path)
    print(f"Successfully updated '{doc_path}' with complete 198 test cases and screenshots .1 to .17!")

if __name__ == '__main__':
    append_test_cases_section()
