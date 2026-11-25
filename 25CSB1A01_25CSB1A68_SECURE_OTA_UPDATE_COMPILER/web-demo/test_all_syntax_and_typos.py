import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from advisory_copilot import orchestrate_advisory_copilot, remediate_syntax_errors, remediate_python_syntax_errors
import ast

def run_tests():
    print("=" * 70)
    print("RUNNING COMPREHENSIVE SYNTAX & TYPO VERIFICATION SUITE (C & PYTHON)")
    print("=" * 70)

    # =========================================================================
    # PART 1: C SYNTAX ERRORS & TYPOS
    # =========================================================================
    print("\n--- PART 1: C SYNTAX DEFECTS & TYPOS ---")

    c_tests = [
        ("Missing opening bracket '['",
         "uint8_t image_hashHASH_LEN];",
         "uint8_t image_hash[HASH_LEN];"),

        ("Missing opening bracket with number",
         "char channel16];",
         "char channel[16];"),

        ("Missing closing bracket ']'",
         "memcpy(&ctx->buffer[buffer_index, data, space);",
         "memcpy(&ctx->buffer[buffer_index], data, space);"),

        ("Missing comma in enum",
         "typedef enum {\n    OTA_OK = 0,\n    OTA_ERR_ROLLBACK\n    OTA_ERR_IMAGE,\n} OtaStatus;",
         "OTA_ERR_ROLLBACK,\n    OTA_ERR_IMAGE,"),

        ("Missing bitwise XOR operator in slot toggle",
         "dev->pending_slot = dev->boot_slot 1;",
         "dev->pending_slot = dev->boot_slot ^ 1;"),

        ("Invalid assignment '=' to function call rvalue in return",
         "return strncmp(s, prefix, strlen(prefix)) = 0;",
         "return strncmp(s, prefix, strlen(prefix)) == 0;"),

        ("Invalid assignment '=' to function call in if condition",
         "if (verifySignature(pkg) = 1) {",
         "if (verifySignature(pkg) == 1) {"),

        ("Macro spelling typo [HSH_LEN]",
         "#define HASH_LEN 32\nuint8_t image_hash[HSH_LEN];",
         "uint8_t image_hash[HASH_LEN];"),

        ("Macro spelling typo [URL_MXA]",
         "#define URL_MAX 128\nchar source_url[URL_MXA];",
         "char source_url[URL_MAX];"),

        ("Keyword typo 'tic void'",
         "tic void sha256_update(void) {",
         "static void sha256_update(void) {"),

        ("Keyword typo 'voif'",
         "voif install(FirmwarePackage *pkg) {",
         "void install(FirmwarePackage *pkg) {"),

        ("Keyword typo 'strcut'",
         "typedef strcut { int version; } FirmwarePackage;",
         "typedef struct { int version; } FirmwarePackage;"),

        ("Keyword typo 'typdef'",
         "typdef struct { int version; } FirmwarePackage;",
         "typedef struct { int version; } FirmwarePackage;"),

        ("Keyword typo 'retun'",
         "retun 0;",
         "return 0;"),

        ("Type typo 'uin32_t'",
         "uin32_t image_size;",
         "uint32_t image_size;"),

        ("Type typo 'uin8_t'",
         "uin8_t master_key[32];",
         "uint8_t master_key[32];"),

        ("Member typo 'dev->boot_slt'",
         "dev->pending_slot = dev->boot_slt ^ 1;",
         "dev->pending_slot = dev->boot_slot ^ 1;"),

        ("Member typo 'dev->currnet_version'",
         "dev->currnet_version = pkg->version;",
         "dev->current_version = pkg->version;"),

        ("Member typo 'pkg->verison'",
         "if (pkg->verison <= dev->current_version)",
         "if (pkg->version <= dev->current_version)"),

        ("Missing closing parenthesis in conditional",
         "if (!verifySignature(pkg) {\n    return -1;\n}",
         "if (!verifySignature(pkg)) {\n    return -1;\n}"),

        ("Missing closing parenthesis in statement",
         "memcpy(dest, src, size;\nreturn 0;",
         "memcpy(dest, src, size);\nreturn 0;"),

        ("Missing closing parenthesis in cast '(voidpkg;'",
         "(voidpkg;\nreturn 1;",
         "(void)pkg;\nreturn 1;"),

        ("Missing closing parenthesis in cast with space '(void pkg;'",
         "(void pkg;\nreturn 1;",
         "(void)pkg;\nreturn 1;"),
    ]

    c_pass = 0
    for name, snippet, expected in c_tests:
        # Wrap in minimal context if needed
        wrapped = f"#include <stdint.h>\n#define HASH_LEN 32\n#define URL_MAX 128\n{snippet}\n"
        fixed = remediate_syntax_errors(wrapped)
        if expected in fixed:
            print(f"  [PASS] {name}")
            c_pass += 1
        else:
            print(f"  [FAIL] {name}\n     Expected: {expected}\n     Got:\n{fixed}")

    print(f"C Unit Tests Passed: {c_pass}/{len(c_tests)}")
    assert c_pass == len(c_tests), f"Some C unit tests failed ({c_pass}/{len(c_tests)})"

    # =========================================================================
    # PART 2: C ADVISORY COPILOT E2E PIPELINE (DIAGNOSIS + REMEDIATION)
    # =========================================================================
    print("\n--- PART 2: C E2E ADVISORY AUDIT ---")
    c_full_source = """#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define URL_MAX 128
#define HASH_LEN 32

typedef enum {
    OTA_OK = 0,
    OTA_ERR_SIGNATURE,
    OTA_ERR_ROLLBACK
    OTA_ERR_IMAGE,
} OtaStatus;

typedef struct {
    int version;
    char source_url[URL_MAX];
    uint8_t image_hash[HSH_LEN];
} FirmwarePackage;

typedef struct {
    int current_version;
    int boot_slot;
    int pending_slot;
} DeviceState;

static int startsWith(const char *s, const char *prefix) {
    return strncmp(s, prefix, strlen(prefix)) = 0;
}

tic void dummy(void) {
    dev->pending_slot = dev->boot_slot 1;
}

void install(FirmwarePackage *pkg) { (void)pkg; }
int sourceTrusted(FirmwarePackage *pkg) { (void)pkg; return 1; }
int verifyImageHash(FirmwarePackage *pkg) { (void)pkg; return 1; }
int verifySignature(FirmwarePackage *pkg) { (void)pkg; return 1; }

int updateFirmware(DeviceState *dev, FirmwarePackage *pkg) {
    if (!dev || !pkg) return -1;
    if (!sourceTrusted(pkg)) return -1;
    if (pkg->version <= dev->current_version) return -1;
    if (!verifyImageHash(pkg)) return -1;
    if (!verifySignature(pkg)) return -1;
    install(pkg);
    return 0;
}
"""
    raw_clang = "secure.c:30:47: error: expression is not assignable"
    res_c = orchestrate_advisory_copilot(c_full_source, violations=[], hints=[], policy="original_protocol.json", filename="secure.c", raw_output=raw_clang)
    print(f"C E2E Verdict: {res_c['verdict']} | Status: {res_c['status']}")
    print(f"Diagnostic Breakdown count: {len(res_c['diagnostic_breakdown'])}")
    for d in res_c['diagnostic_breakdown']:
        print(f"   • [{d['location']}] ({d['category']}): {d['issue']} -> {d['correction']}")

    assert "return strncmp(s, prefix, strlen(prefix)) == 0;" in res_c["full_code"], "strncmp not fixed!"
    assert "uint8_t image_hash[HASH_LEN];" in res_c["full_code"], "HSH_LEN not fixed!"
    assert "OTA_ERR_ROLLBACK," in res_c["full_code"], "OTA_ERR_ROLLBACK, not fixed!"
    assert "static void dummy" in res_c["full_code"], "static void not fixed!"
    assert "dev->boot_slot ^ 1;" in res_c["full_code"], "boot_slot ^ 1 not fixed!"
    print("PASS: C E2E Pipeline successfully diagnosed and resolved all defects!")

    # =========================================================================
    # PART 3: PYTHON SYNTAX DEFECTS & TYPOS
    # =========================================================================
    print("\n--- PART 3: PYTHON SYNTAX DEFECTS & TYPOS ---")

    py_tests = [
        ("Keyword typo 'dfe' -> 'def'",
         "dfe updateFirmware(dev, pkg):\n    return 0",
         "def updateFirmware(dev, pkg):\n    return 0"),

        ("Missing colon ':' on def",
         "def updateFirmware(dev, pkg)\n    return 0",
         "def updateFirmware(dev, pkg):\n    return 0"),

        ("Missing colon ':' on if",
         "    if not pkg\n        return 0",
         "    if not pkg:\n        return 0"),

        ("Accidental assignment '=' in if condition",
         "    if pkg.version = dev.current_version:\n        return 0",
         "    if pkg.version == dev.current_version:\n        return 0"),

        ("Keyword typo 'retun'",
         "    retun UpdateStatus.OTA_UPDATE_SUCCESS",
         "    return UpdateStatus.OTA_UPDATE_SUCCESS"),

        ("Attribute typo 'dev.currnet_version'",
         "    dev.currnet_version = pkg.version",
         "    dev.current_version = pkg.version"),

        ("Attribute typo 'pkg.verison'",
         "    if pkg.verison <= dev.current_version:",
         "    if pkg.version <= dev.current_version:"),

        ("Attribute typo 'dev.boot_slt'",
         "    dev.pending_slot = dev.boot_slt ^ 1",
         "    dev.pending_slot = dev.boot_slot ^ 1"),

        ("Symbol typo 'ERR_INVALID_PACKGE'",
         "    return UpdateStatus.ERR_INVALID_PACKGE",
         "    return UpdateStatus.ERR_INVALID_PACKAGE"),

        ("Unclosed parenthesis in condition",
         "    if not verifySignature(pkg, dev.public_key_pem:\n        return 0",
         "    if not verifySignature(pkg, dev.public_key_pem):\n        return 0"),

        ("Keyword typo 'calss'",
         "calss DeviceConfig:\n    pass",
         "class DeviceConfig:\n    pass"),

        ("Keyword typo 'improt'",
         "improt hashlib\nreturn 0",
         "import hashlib\nreturn 0"),

        ("Missing colon on while loop",
         "    while len >= 64\n        len -= 64",
         "    while len >= 64:\n        len -= 64"),

        ("Missing colon on for loop",
         "    for chunk in chunks\n        process(chunk)",
         "    for chunk in chunks:\n        process(chunk)"),

        ("Keyword typo 'whlie'",
         "    whlie True:\n        break",
         "    while True:\n        break"),

        ("Unclosed bracket in statement",
         "    items = [1, 2\n    return items",
         "    items = [1, 2]\n    return items"),
    ]

    py_pass = 0
    for name, snippet, expected in py_tests:
        fixed = remediate_python_syntax_errors(snippet)
        if expected in fixed:
            print(f"  [PASS] {name}")
            py_pass += 1
        else:
            print(f"  [FAIL] {name}\n     Expected: {expected}\n     Got:\n{fixed}")

    print(f"Python Unit Tests Passed: {py_pass}/{len(py_tests)}")
    assert py_pass == len(py_tests), f"Some Python unit tests failed ({py_pass}/{len(py_tests)})"

    # =========================================================================
    # PART 4: PYTHON ADVISORY COPILOT E2E PIPELINE
    # =========================================================================
    print("\n--- PART 4: PYTHON E2E ADVISORY AUDIT ---")
    py_full_source = """from src_py.update_handler import (
    OtaPackage, DeviceState, UpdateStatus,
    verifySignature, sourceTrusted, verifyImageHash, decryptPayloadAesGcm, install
)

dfe updateFirmware(dev: DeviceState, pkg: OtaPackage) -> UpdateStatus
    if not pkg
        retun UpdateStatus.ERR_INVALID_PACKGE

    if not verifySignature(pkg, dev.public_key_pem
        retun UpdateStatus.ERR_SIGNATURE_INVALID

    if not sourceTrusted(pkg
        retun UpdateStatus.ERR_SOURCE_UNTRUSTED

    if not verifyImageHash(pkg
        retun UpdateStatus.ERR_IMAGE_HASH_INVALID

    decrypted = decryptPayloadAesGcm(pkg, dev.master_key)

    if pkg.verison <= dev.currnet_version
        retun UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKD

    install(pkg, decrypted)
    dev.current_version = pkg.version
    dev.pending_slot = dev.boot_slt ^ 1
    retun UpdateStatus.OTA_UPDATE_SUCCESS
"""
    res_py = orchestrate_advisory_copilot(py_full_source, violations=[], hints=[], policy="original_protocol.json", filename="secure.py", raw_output="SyntaxError: invalid syntax")
    print(f"Python E2E Verdict: {res_py['verdict']} | Status: {res_py['status']}")
    print(f"Diagnostic Breakdown count: {len(res_py['diagnostic_breakdown'])}")
    for d in res_py['diagnostic_breakdown']:
        print(f"   • [{d['location']}] ({d['category']}): {d['issue']} -> {d['correction']}")

    fixed_py = res_py["full_code"]
    # Verify AST can parse it
    try:
        ast.parse(fixed_py)
        print("PASS: Remediated Python code successfully parsed by python ast.parse()!")
    except SyntaxError as e:
        print(f"FAIL: ast.parse failed on line {e.lineno}: {e.msg}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("ALL SYNTAX DEFECT & TYPO TESTS FOR BOTH C AND PYTHON PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
