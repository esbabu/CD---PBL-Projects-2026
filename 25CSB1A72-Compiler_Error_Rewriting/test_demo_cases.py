import sys, io, os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
from webapp import app

CASES = [
    # ── SHOULD HEAL (15) ──
    ("01_semicolon_int", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5\n    cout << x << endl;\n    return 0;\n}\n", "heal"),
    ("02_semicolon_string", "#include <iostream>\n#include <string>\nusing namespace std;\nint main() {\n    string name = \"Alice\"\n    cout << name << endl;\n    return 0;\n}\n", "heal"),
    ("03_semicolon_double", "#include <iostream>\nusing namespace std;\nint main() {\n    double price = 19.99\n    cout << price << endl;\n    return 0;\n}\n", "heal"),
    ("04_include_vector", "#include <iostream>\nusing namespace std;\nint main() {\n    vector<int> nums = {1, 2, 3};\n    cout << nums[0] << endl;\n    return 0;\n}\n", "heal"),
    ("06_include_map", "#include <iostream>\nusing namespace std;\nint main() {\n    map<string, int> ages;\n    ages[\"Alice\"] = 25;\n    cout << ages[\"Alice\"] << endl;\n    return 0;\n}\n", "heal"),
    ("07_missing_brace", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 10;\n    if (x > 5) {\n        cout << \"Big\" << endl;\n    return 0;\n}\n", "heal"),
    ("08_typo_whlie", "#include <iostream>\nusing namespace std;\nint main() {\n    int i = 0;\n    whlie (i < 5) {\n        cout << i << endl;\n        i++;\n    }\n    return 0;\n}\n", "heal"),
    ("09_typo_retrun", "#include <iostream>\nusing namespace std;\nint add(int a, int b) {\n    retrun a + b;\n}\nint main() {\n    cout << add(2, 3) << endl;\n    return 0;\n}\n", "heal"),
    ("10_stream_cin", "#include <iostream>\nusing namespace std;\nint main() {\n    int x;\n    cin << x;\n    cout << \"You entered: \" << x << endl;\n    return 0;\n}\n", "heal"),
    ("11_stream_cout", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 42;\n    cout >> x >> endl;\n    return 0;\n}\n", "heal"),
    ("12_for_loop_semicolon", "#include <iostream>\nusing namespace std;\nint main() {\n    for (int i = 0; i < 5 i++) {\n        cout << i << endl;\n    }\n    return 0;\n}\n", "heal"),
    ("13_assign_in_cond", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 0;\n    if (x = 5) {\n        cout << \"x is 5\" << endl;\n    }\n    return 0;\n}\n", "heal"),
    ("14_undeclared_var", "#include <iostream>\nusing namespace std;\nint main() {\n    int a = 5;\n    int b = 3;\n    result = a + b;\n    cout << result << endl;\n    return 0;\n}\n", "heal"),
    ("15_div_zero", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 10;\n    int y = x / 0;\n    cout << y << endl;\n    return 0;\n}\n", "heal"),
    ("16_missing_paren", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 10;\n    if (x > 5 {\n        cout << \"Big\" << endl;\n    }\n    return 0;\n}\n", "heal"),

    # ── SHOULD REFUSE (10) ──
    ("security_system", "#include <cstdlib>\nint main() { system(\"ls\"); return 0; }\n", "refuse"),
    ("security_strcpy", "#include <cstring>\nint main() { char a[5]; strcpy(a, \"hello\"); return 0; }\n", "refuse"),
    ("security_gets", "#include <cstdio>\nint main() { char a[5]; gets(a); return 0; }\n", "refuse"),
    ("security_double_free", "int main() { int* p = new int(5); delete p; delete p; return 0; }\n", "refuse"),
    ("security_buffer_overflow", "int main() { int arr[5]; arr[10] = 0; return 0; }\n", "refuse"),
    ("security_format_string", "#include <cstdio>\nint main() { char f[] = \"test\"; printf(f); return 0; }\n", "refuse"),
    ("security_popen", "#include <cstdio>\nint main() { FILE* f = popen(\"ls\", \"r\"); pclose(f); return 0; }\n", "refuse"),
    ("security_asm", "int main() { __asm__(\"nop\"); return 0; }\n", "refuse"),
    ("security_strcat", "#include <cstring>\nint main() { char a[5] = \"a\"; strcat(a, \"b\"); return 0; }\n", "refuse"),
    ("security_sprintf", "#include <cstdio>\nint main() { char a[5]; sprintf(a, \"%s\", \"hello\"); return 0; }\n", "refuse"),

    # ── SHOULD BE CLEAN (10) ──
    ("clean_hello", "#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Hello\" << endl;\n    return 0;\n}\n", "clean"),
    ("clean_vector", "#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> v = {1, 2, 3, 4, 5};\n    int sum = 0;\n    for (int x : v) sum += x;\n    cout << \"Sum: \" << sum << endl;\n    return 0;\n}\n", "clean"),
    ("clean_string", "#include <iostream>\n#include <string>\nusing namespace std;\nint main() {\n    string name = \"Bob\";\n    cout << \"Hello, \" << name << \"!\" << endl;\n    return 0;\n}\n", "clean"),
    ("clean_loop", "#include <iostream>\nusing namespace std;\nint main() {\n    for (int i = 0; i < 10; i++) {\n        cout << i << \" \";\n    }\n    cout << endl;\n    return 0;\n}\n", "clean"),
    ("clean_function", "#include <iostream>\nusing namespace std;\nint add(int a, int b) {\n    return a + b;\n}\nint main() {\n    cout << add(3, 4) << endl;\n    return 0;\n}\n", "clean"),
    ("clean_class", "#include <iostream>\nusing namespace std;\nclass Foo {\npublic:\n    int x;\n    Foo() : x(0) {}\n};\nint main() { Foo f; return 0; }\n", "clean"),
    ("clean_while", "#include <iostream>\nusing namespace std;\nint main() {\n    int i = 0;\n    while (i < 5) { cout << i << \" \"; i++; }\n    return 0;\n}\n", "clean"),
    ("clean_pointer", "#include <iostream>\nusing namespace std;\nint main() {\n    int* p = new int(5);\n    cout << *p << endl;\n    delete p;\n    return 0;\n}\n", "clean"),
    ("clean_stl_map", "#include <iostream>\n#include <map>\nusing namespace std;\nint main() {\n    map<string, int> m;\n    m[\"a\"] = 1;\n    return 0;\n}\n", "clean"),
    ("clean_string_ops", "#include <iostream>\n#include <string>\nusing namespace std;\nint main() {\n    string s = \"abc\";\n    s += \"def\";\n    cout << s << endl;\n    return 0;\n}\n", "clean"),

    # ── SHOULD HEAL (SYNTAX VARIATIONS) (10) ──
    ("syn1_missing_brace", "#include <iostream>\nusing namespace std;\nvoid foo() {\n    int x = 5;\nint main() {\n    foo();\n    return 0;\n}\n", "heal"),
    ("syn2_missing_paren", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 10;\n    if (x > 5 {\n        cout << x << endl;\n    }\n    return 0;\n}\n", "heal"),
    ("syn3_missing_semi_for", "#include <iostream>\nusing namespace std;\nint main() {\n    for (int i = 0; i < 5 i++) {\n        cout << i << endl;\n    }\n    return 0;\n}\n", "heal"),
    ("syn4_undeclared_var", "#include <iostream>\nusing namespace std;\nint main() {\n    result = 100;\n    return 0;\n}\n", "heal"),
    ("syn5_wrong_cout", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5;\n    cout >> x >> endl;\n    return 0;\n}\n", "heal"),
    ("syn6_typo_while", "#include <iostream>\nusing namespace std;\nint main() {\n    int i = 0;\n    whlie (i < 5) { i++; }\n    return 0;\n}\n", "heal"),
    ("syn7_typo_return", "#include <iostream>\nusing namespace std;\nint add(int a, int b) {\n    retrun a + b;\n}\nint main() { cout << add(1, 2); return 0; }\n", "heal"),
    ("syn8_missing_semi", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5\n    return 0;\n}\n", "heal"),
    ("syn9_assign_cond", "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 0;\n    if (x = 5) { cout << x; }\n    return 0;\n}\n", "heal"),
    ("syn10_wrong_cin", "#include <iostream>\nusing namespace std;\nint main() {\n    int x;\n    cin << x;\n    return 0;\n}\n", "heal"),

    # ── SHOULD REFUSE (MORE SECURITY) (7) ──
    ("sec_asm", "int main() { __asm__(\"nop\"); return 0; }\n", "refuse"),
    ("sec_system_literal", "#include <cstdlib>\nint main() { system(\"ls\"); return 0; }\n", "refuse"),
    ("sec_system_var", "#include <cstdlib>\nint main() { char cmd[] = \"ls\"; system(cmd); return 0; }\n", "refuse"),
    ("sec_getenv", "#include <cstdlib>\nint main() { getenv(\"PATH\"); return 0; }\n", "refuse"),
    ("sec_atoi", "#include <cstdlib>\nint main() { int x = atoi(\"100\"); return 0; }\n", "refuse"),
    ("sec_alloca", "#include <alloca.h>\nint main() { void* p = alloca(100); return 0; }\n", "refuse"),
    ("sec_strncpy", "#include <cstring>\nint main() { char a[5]; strncpy(a, \"hi\", 5); return 0; }\n", "refuse"),

    # ── SHOULD BE CLEAN (MORE) (5) ──
    ("clean_simple1", "int main() { return 0; }\n", "clean"),
    ("clean_simple2", "#include <stdio.h>\nint main() { printf(\"hi\\n\"); return 0; }\n", "clean"),
    ("clean_simple3", "#include <iostream>\nint main() { std::cout << \"hi\" << std::endl; return 0; }\n", "clean"),
    ("clean_simple4", "#include <iostream>\nusing namespace std;\nint main() { int a = 5; int b = 10; int c = a + b; return 0; }\n", "clean"),
    ("clean_simple5", "#include <iostream>\nusing namespace std;\nint main() { cout << \"clean\" << endl; return 0; }\n", "clean"),
]

# ── Total = 15 heal + 10 refuse + 10 clean + 10 heal + 7 refuse + 5 clean = 57 cases
print(f"Running {len(CASES)} test cases...\n")

client = app.test_client()
results = []
by_group = {"heal": [0, 0], "refuse": [0, 0], "clean": [0, 0]}

for name, source, expected in CASES:
    res = client.post(
        '/api/fix',
        data={'source': (io.BytesIO(source.encode()), name + '.cpp')},
        content_type='multipart/form-data'
    )
    data = res.get_json()
    verdict = data.get('verdict', 'unknown')
    changed = data.get('fixed_source') != data.get('original_source')
    actual = "clean" if verdict == "already_clean" else ("heal" if changed else "refuse")
    match = "PASS" if actual == expected else "FAIL"
    results.append((name, expected, actual, match))
    by_group[expected][1] += 1
    if actual == expected:
        by_group[expected][0] += 1
    print("[%s] %-30s expected=%-7s actual=%-7s verdict=%s" % (match, name, expected, actual, verdict))

print()
passed = sum(1 for _, _, _, m in results if m == "PASS")
print("OVERALL: %d/%d = %.1f%%" % (passed, len(results), 100.0 * passed / len(results)))
print()
for g, (p, t) in by_group.items():
    print("  %-7s: %d/%d = %.1f%%" % (g, p, t, 100.0 * p / t if t else 0))