#!/usr/bin/env python3
"""
test_python_pipeline_e2e.py - End-to-End Automated Test Harness (Python Subsystem)

Validates the Hybrid Encrypt-Then-Sign OTA Firmware Pipeline for Python:
1. Python packaging tool (AES-256-GCM encryption + ECDSA P-256 signing)
2. Python runtime decryption & verification (src_py/update_handler.py)
3. AST CFG dominance & policy security compiler (secure-python)
4. Tampering & attack simulations:
   - Test 1: Valid upgrade (clean verification, decryption, and install)
   - Test 2: Tampered digital signature rejection
   - Test 3: Tampered ciphertext payload rejection (hash failure)
   - Test 4: Tampered AES-GCM tag rejection (AEAD auth failure)
   - Test 5: Monotonic rollback guard (downgrade v1.0.0 <= v1.1.0 blocked)
   - Test 6: Monotonic rollback guard (same-version replay v1.1.0 <= v1.1.0 blocked)
   - Test 7: Untrusted source URL rejection
   - Test 8: Wrong Master Key rejection
   - Test 9: secure-python compiler verification (secure passes, 7 attack samples blocked)
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PYTHON_EXE = PROJECT_ROOT / ".venv" / "bin" / "python3"
if not PYTHON_EXE.is_file():
    PYTHON_EXE = Path(sys.executable)

PACKAGER_SCRIPT = PROJECT_ROOT / "tools" / "package_firmware.py"
SECURE_PYTHON = PROJECT_ROOT / "secure-python"
DEFAULT_KEY = PROJECT_ROOT / "keys" / "private_key.pem"
DEFAULT_MASTER_KEY = PROJECT_ROOT / "keys" / "master_key.bin"

from src_py.update_handler import (
    DeviceState,
    OtaPackage,
    UpdateStatus,
    parse_semver,
    update_firmware,
)
from tools.package_firmware import (
    build_package,
    load_or_generate_ecdsa_key,
    load_or_generate_master_key,
)


def log(msg: str):
    print(f"[Python E2E Test] {msg}")


def test_1_valid_update():
    log("--- Running Test 1: Valid Firmware Update (v1.2.0 > v1.1.0) ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"AUTHENTIC_PYTHON_GATEWAY_FIRMWARE_PAYLOAD_V120"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=master_key,
        channel="stable",
        source_url="https://github.com/firmware/release.bin",
    )

    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None, "Failed to parse OTA package bytes"

    # Current installed version is v1.1.0 = (1 << 16) | (1 << 8) | 0 = 65792
    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(
        current_version=packed_cur,
        boot_slot=0,
        pending_slot=1,
        master_key=master_key,
    )

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.OTA_UPDATE_SUCCESS, f"Expected SUCCESS, got: {status}"
    assert dev.flashed_payload == payload, "Flashed payload does not match authentic payload"
    assert dev.current_version == pkg.version, "Device version not updated to 1.2.0"
    log("Test 1 PASSED: Valid update verified, cleanly decrypted, and flashed.")


def test_2_tampered_signature():
    log("--- Running Test 2: Tampered Digital Signature Rejection ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"PAYLOAD_SIGNATURE_TAMPER_TEST"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=master_key,
    )

    # Corrupt one byte in the 64-byte signature (located at offset 216 + 32 = 248)
    bundle_arr = bytearray(ota_bundle)
    bundle_arr[250] ^= 0xFF
    tampered_bundle = bytes(bundle_arr)

    pkg = OtaPackage.from_bytes(tampered_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_SIGNATURE_INVALID, f"Expected ERR_SIGNATURE_INVALID, got {status}"
    log("Test 2 PASSED: Tampered signature halted execution instantly.")


def test_3_tampered_ciphertext():
    log("--- Running Test 3: Tampered Ciphertext Payload (Hash Failure) ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"PAYLOAD_CIPHERTEXT_TAMPER_TEST"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=master_key,
    )

    # Corrupt byte in ciphertext payload (offset >= 328)
    bundle_arr = bytearray(ota_bundle)
    bundle_arr[330] ^= 0xAA
    tampered_bundle = bytes(bundle_arr)

    pkg = OtaPackage.from_bytes(tampered_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_IMAGE_HASH_INVALID, f"Expected ERR_IMAGE_HASH_INVALID, got {status}"
    log("Test 3 PASSED: Tampered ciphertext caught by image hash verification.")


def test_4_tampered_tag():
    log("--- Running Test 4: Tampered AES-GCM Tag (Decryption Authentication Failure) ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"PAYLOAD_TAG_TAMPER_TEST"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=master_key,
    )

    # Bypass hash check by adjusting tag and updating hash/sig, OR test decrypt_payload_aes_gcm directly
    from src_py.update_handler import decrypt_payload_aes_gcm
    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None

    # Corrupt tag
    pkg.tag = bytes(b ^ 0x01 for b in pkg.tag)
    dec = decrypt_payload_aes_gcm(pkg, master_key)
    assert dec is None, "Decryption succeeded with invalid AES-GCM tag!"
    log("Test 4 PASSED: Corrupted AES-GCM tag detected and decryption aborted cleanly.")


def test_5_downgrade_rollback():
    log("--- Running Test 5: Monotonic Rollback Guard (Downgrade v1.0.0 <= v1.1.0) ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"DOWNGRADE_ATTACK_PAYLOAD"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.0.0",  # Downgrade
        priv_key=priv_key,
        master_key=master_key,
    )

    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED, f"Expected ERR_VERSION_ROLLBACK_BLOCKED, got {status}"
    log("Test 5 PASSED: Downgrade attack blocked by monotonic version check.")


def test_6_same_version_replay():
    log("--- Running Test 6: Monotonic Rollback Guard (Equal Version Replay v1.1.0 <= v1.1.0) ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"SAME_VERSION_REPLAY_PAYLOAD"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.1.0",  # Replay identical version
        priv_key=priv_key,
        master_key=master_key,
    )

    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED, f"Expected ERR_VERSION_ROLLBACK_BLOCKED, got {status}"
    log("Test 6 PASSED: Same-version replay rejected by monotonic version check.")


def test_7_untrusted_source():
    log("--- Running Test 7: Untrusted Source URL Rejection ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)

    payload = b"EVIL_MIRROR_PAYLOAD"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=master_key,
        source_url="http://attacker-compromised-mirror.org/update.bin",
    )

    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_SOURCE_UNTRUSTED, f"Expected ERR_SOURCE_UNTRUSTED, got {status}"
    log("Test 7 PASSED: Untrusted source rejected before installation.")


def test_8_wrong_master_key():
    log("--- Running Test 8: Tampered / Wrong Master Key Rejection ---")
    priv_key = load_or_generate_ecdsa_key(DEFAULT_KEY)
    correct_master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY)
    wrong_master_key = os.urandom(32)

    payload = b"SECRET_FIRMWARE_CORE"
    ota_bundle, _ = build_package(
        firmware_bytes=payload,
        version_str="1.2.0",
        priv_key=priv_key,
        master_key=correct_master_key,
    )

    pkg = OtaPackage.from_bytes(ota_bundle)
    assert pkg is not None

    packed_cur, _, _, _ = parse_semver("1.1.0")
    dev = DeviceState(current_version=packed_cur, master_key=wrong_master_key)

    status = update_firmware(dev, pkg)
    assert status == UpdateStatus.ERR_DECRYPTION_FAILED, f"Expected ERR_DECRYPTION_FAILED, got {status}"
    log("Test 8 PASSED: Device with wrong Master Key failed GCM authentication & decryption.")


def test_9_compiler_verification():
    log("--- Running Test 9: secure-python AST CFG Compiler Verification ---")
    # 1. Compile secure.py
    secure_sample = PROJECT_ROOT / "tests" / "python" / "secure.py"
    res = subprocess.run([sys.executable, str(SECURE_PYTHON), str(secure_sample)], capture_output=True, text=True)
    assert res.returncode == 0, f"secure.py failed to compile:\n{res.stderr}"
    log("secure.py passed compilation cleanly.")

    # 2. Verify all insecure samples are blocked
    insecure_samples = [
        ("insecure_rule_signature_missing.py", "Signature Verification Dominance Violation"),
        ("insecure_rule_source_missing.py", "Trusted Source Dominance Violation"),
        ("insecure_rule_hash_missing.py", "Image Hash Dominance Violation"),
        ("insecure_rule_rollback_missing.py", "Monotonic Rollback Guard Violation"),
        ("insecure_rule_rollback_equal_allowed.py", "Monotonic Rollback Guard Violation"),
        ("insecure_banned_eval.py", "Banned Function Violation"),
        ("insecure_rule_weak_md5.py", "Weak Cryptography Violation"),
        ("insecure_hardcoded_secret.py", "Hardcoded Secret Violation"),
    ]

    for fname, expected_violation in insecure_samples:
        fpath = PROJECT_ROOT / "tests" / "python" / fname
        res = subprocess.run([sys.executable, str(SECURE_PYTHON), str(fpath)], capture_output=True, text=True)
        assert res.returncode != 0, f"{fname} unexpectedly passed compilation!"
        output = res.stderr + "\n" + res.stdout
        assert expected_violation in output, f"{fname} did not report '{expected_violation}'. Output was:\n{output}"
        log(f"{fname} blocked as expected: found '{expected_violation}'.")

    log("Test 9 PASSED: secure-python correctly accepted secure firmware and rejected all 8 attack variations.")


def main():
    log("=====================================================================")
    log(" STARTING END-TO-END PYTHON ENCRYPT-THEN-SIGN PIPELINE TEST SUITE")
    log("=====================================================================")
    test_1_valid_update()
    test_2_tampered_signature()
    test_3_tampered_ciphertext()
    test_4_tampered_tag()
    test_5_downgrade_rollback()
    test_6_same_version_replay()
    test_7_untrusted_source()
    test_8_wrong_master_key()
    test_9_compiler_verification()
    log("=====================================================================")
    log(" ALL 9 PYTHON PIPELINE E2E INTEGRATION TESTS PASSED SUCCESSFULLY!")
    log("=====================================================================")


if __name__ == "__main__":
    main()
