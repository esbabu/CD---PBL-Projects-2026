#!/usr/bin/env python3
"""
test_pipeline_e2e.py - End-to-End Automated Test Harness

Validates the Hybrid Encrypt-Then-Sign OTA Firmware Pipeline:
1. Python packaging tool (AES-256-GCM encryption + ECDSA P-256 signing)
2. C runtime decryption & verification (update_handler.c + crypto.c)
3. LLVM pass compiler dominance and security checks via secure-clang
4. Tampering & attack simulations:
   - Valid upgrade (clean verification, decryption, and simulated flash)
   - Tampered ECDSA digital signature rejection
   - Tampered ciphertext payload rejection (hash verification failure)
   - Tampered AES-GCM tag rejection (AEAD decryption authentication failure)
   - Downgrade rollback attack prevention (v1.0.0 <= v1.1.0 blocked)
   - Same-version replay prevention (v1.1.0 <= v1.1.0 blocked)
   - Untrusted source URL rejection
"""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = PROJECT_ROOT / ".venv" / "bin" / "python3"
if not PYTHON_EXE.is_file():
    PYTHON_EXE = Path(sys.executable)

PACKAGER_SCRIPT = PROJECT_ROOT / "tools" / "package_firmware.py"
SECURE_CLANG = PROJECT_ROOT / "secure-clang"
RUNNER_SRC = PROJECT_ROOT / "tests" / "e2e_runner.c"
RUNNER_BIN = PROJECT_ROOT / "tests" / "e2e_runner"
DEFAULT_KEY = PROJECT_ROOT / "keys" / "private_key.pem"
DEFAULT_MASTER_KEY = PROJECT_ROOT / "keys" / "master_key.bin"


def log(msg: str):
    print(f"[E2E Test] {msg}")


def run_cmd(cmd: list[str], cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def compile_runner():
    log("Compiling C runtime test runner using secure-clang...")
    cmd = [
        str(SECURE_CLANG),
        "--",
        "-Iinclude",
        "-Isrc",
        str(RUNNER_SRC),
        "src/update_handler.c",
        "src/crypto.c",
        "src/version.c",
        "-o",
        str(RUNNER_BIN),
    ]
    res = run_cmd(cmd)
    if res.returncode != 0:
        print("secure-clang compilation failed!")
        print("STDOUT:\n", res.stdout)
        print("STDERR:\n", res.stderr)
        sys.exit(1)
    log("C runtime test runner compiled successfully with secure-clang.")


def test_valid_firmware_update(work_dir: Path):
    log("--- Running Test 1: Valid Firmware Update (v1.2.0 > v1.1.0) ---")
    raw_payload = b"SECURE_GATEWAY_FIRMWARE_CORE_IMAGE_V1.2.0_AUTHENTIC"
    fw_bin = work_dir / "firmware_v120.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "firmware_v120.ota"
    pack_res = run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.2.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])
    assert pack_res.returncode == 0, f"Packager failed:\n{pack_res.stderr}"
    assert ota_pkg.is_file(), "OTA package not generated"

    # Installed version is v1.1.0 = (1 << 16) | (1 << 8) | 0 = 0x00010100 (65792)
    current_ver_hex = "0x00010100"
    runner_res = run_cmd([str(RUNNER_BIN), str(ota_pkg), current_ver_hex])

    assert runner_res.returncode == 0, (
        f"Expected runner to succeed (returncode 0), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "SUCCESS: Firmware update applied successfully!" in runner_res.stdout
    assert raw_payload.decode("utf-8") in runner_res.stdout, "Decrypted payload does not match original"
    log("Test 1 PASSED: Valid update verified, cleanly decrypted, and flashed.")


def test_tampered_signature(work_dir: Path):
    log("--- Running Test 2: Tampered Digital Signature Rejection ---")
    raw_payload = b"SECURE_PAYLOAD_TAMPER_SIGNATURE_TEST"
    fw_bin = work_dir / "fw_sig.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_sig.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.3.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])

    data = bytearray(ota_pkg.read_bytes())
    # Header layout:
    # metadata: 0..215
    # image_hash: 216..247
    # signature: 248..311 (64 bytes)
    # Corrupt signature by zeroing it out
    data[248:312] = b"\x00" * 64

    tampered_ota = work_dir / "tampered_sig.ota"
    tampered_ota.write_bytes(data)

    runner_res = run_cmd([str(RUNNER_BIN), str(tampered_ota)])
    assert runner_res.returncode == 10, (
        f"Expected returncode 10 (ERR_SIGNATURE_INVALID), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_SIGNATURE_INVALID" in runner_res.stderr
    log("Test 2 PASSED: Tampered signature halted execution instantly.")


def test_tampered_ciphertext_payload(work_dir: Path):
    log("--- Running Test 3: Tampered Ciphertext Payload (Hash Failure) ---")
    raw_payload = b"SECURE_PAYLOAD_TAMPER_CIPHERTEXT_TEST"
    fw_bin = work_dir / "fw_ct.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_ct.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.3.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])

    data = bytearray(ota_pkg.read_bytes())
    # Ciphertext starts at byte 328
    data[330] ^= 0x5A  # Corrupt 1 byte in ciphertext

    tampered_ota = work_dir / "tampered_ct.ota"
    tampered_ota.write_bytes(data)

    runner_res = run_cmd([str(RUNNER_BIN), str(tampered_ota)])
    assert runner_res.returncode == 12, (
        f"Expected returncode 12 (ERR_IMAGE_HASH_INVALID), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_IMAGE_HASH_INVALID" in runner_res.stderr
    log("Test 3 PASSED: Tampered ciphertext caught by image hash verification.")


def test_tampered_tag_decryption(work_dir: Path):
    log("--- Running Test 4: Tampered AES-GCM Tag (Decryption Authentication Failure) ---")
    raw_payload = b"SECURE_PAYLOAD_TAMPER_AES_TAG_TEST"
    fw_bin = work_dir / "fw_tag.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_tag.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.3.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])

    data = bytearray(ota_pkg.read_bytes())
    # Tag is at offset 312..327 (16 bytes)
    # Corrupt the tag byte
    data[315] ^= 0xA5

    # Recompute image_hash so step 3 (hash verify) passes, testing step 4 (AES-GCM tag verification)
    metadata = bytes(data[:216])
    tag = bytes(data[312:328])
    ciphertext = bytes(data[328:])
    h = hashlib.sha256()
    h.update(metadata)
    h.update(ciphertext)
    h.update(tag)
    new_hash = h.digest()
    data[216:248] = new_hash

    tampered_ota = work_dir / "tampered_tag.ota"
    tampered_ota.write_bytes(data)

    runner_res = run_cmd([str(RUNNER_BIN), str(tampered_ota)])
    assert runner_res.returncode == 14, (
        f"Expected returncode 14 (ERR_DECRYPTION_FAILED), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_DECRYPTION_FAILED" in runner_res.stderr
    log("Test 4 PASSED: Corrupted AES-GCM tag detected and decryption aborted cleanly.")


def test_version_rollback_downgrade(work_dir: Path):
    log("--- Running Test 5: Monotonic Rollback Guard (Downgrade v1.0.0 <= v1.1.0) ---")
    raw_payload = b"OLDER_FIRMWARE_PAYLOAD_V1.0.0"
    fw_bin = work_dir / "fw_v100.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_v100.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.0.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])

    # Installed version is v1.1.0 = 0x00010100
    current_ver_hex = "0x00010100"
    runner_res = run_cmd([str(RUNNER_BIN), str(ota_pkg), current_ver_hex])

    assert runner_res.returncode == 13, (
        f"Expected returncode 13 (ERR_VERSION_ROLLBACK_BLOCKED), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_VERSION_ROLLBACK_BLOCKED" in runner_res.stderr
    log("Test 5 PASSED: Downgrade attack blocked by monotonic version check.")


def test_version_rollback_equal(work_dir: Path):
    log("--- Running Test 6: Monotonic Rollback Guard (Equal Version Replay v1.1.0 <= v1.1.0) ---")
    raw_payload = b"SAME_FIRMWARE_PAYLOAD_V1.1.0"
    fw_bin = work_dir / "fw_v110.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_v110.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.1.0",
        "-k", str(DEFAULT_KEY),
        "-o", str(ota_pkg),
    ])

    # Installed version is v1.1.0 = 0x00010100
    current_ver_hex = "0x00010100"
    runner_res = run_cmd([str(RUNNER_BIN), str(ota_pkg), current_ver_hex])

    assert runner_res.returncode == 13, (
        f"Expected returncode 13 (ERR_VERSION_ROLLBACK_BLOCKED), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_VERSION_ROLLBACK_BLOCKED" in runner_res.stderr
    log("Test 6 PASSED: Same-version replay rejected by monotonic version check.")


def test_untrusted_source(work_dir: Path):
    log("--- Running Test 7: Untrusted Source URL Rejection ---")
    raw_payload = b"PAYLOAD_FROM_UNTRUSTED_HOST"
    fw_bin = work_dir / "fw_untrusted.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_untrusted.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.4.0",
        "-k", str(DEFAULT_KEY),
        "--source-url", "https://untrusted-host.example.com/fw.bin",
        "-o", str(ota_pkg),
    ])

    runner_res = run_cmd([str(RUNNER_BIN), str(ota_pkg)])
    assert runner_res.returncode == 11, (
        f"Expected returncode 11 (ERR_SOURCE_UNTRUSTED), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_SOURCE_UNTRUSTED" in runner_res.stderr
    log("Test 7 PASSED: Untrusted source rejected before installation.")


def test_tampered_master_key(work_dir: Path):
    log("--- Running Test 8: Tampered / Wrong Master Key Rejection ---")
    raw_payload = b"SECURE_PAYLOAD_TAMPERED_MASTER_KEY_TEST"
    fw_bin = work_dir / "fw_mk.bin"
    fw_bin.write_bytes(raw_payload)

    ota_pkg = work_dir / "fw_mk.ota"
    run_cmd([
        str(PYTHON_EXE),
        str(PACKAGER_SCRIPT),
        "-i", str(fw_bin),
        "-v", "1.3.0",
        "-k", str(DEFAULT_KEY),
        "-m", str(DEFAULT_MASTER_KEY),
        "-o", str(ota_pkg),
    ])

    # Corrupt master key (e.g. wrong key on an unauthorized device or altered eFuse)
    corrupt_master_key_hex = "00" * 32
    current_ver_hex = "0x00010100"
    runner_res = run_cmd([str(RUNNER_BIN), str(ota_pkg), current_ver_hex, corrupt_master_key_hex])
    assert runner_res.returncode == 14, (
        f"Expected returncode 14 (ERR_DECRYPTION_FAILED), got {runner_res.returncode}.\n"
        f"Stdout: {runner_res.stdout}\nStderr: {runner_res.stderr}"
    )
    assert "ERR_DECRYPTION_FAILED" in runner_res.stderr
    log("Test 8 PASSED: Device with wrong Master Key failed GCM authentication & decryption.")


def main() -> int:
    log("=====================================================================")
    log(" STARTING END-TO-END HYBRID ENCRYPT-THEN-SIGN PIPELINE TEST SUITE")
    log("=====================================================================")

    compile_runner()

    work_dir = Path(tempfile.mkdtemp(prefix="ota_e2e_"))
    try:
        test_valid_firmware_update(work_dir)
        test_tampered_signature(work_dir)
        test_tampered_ciphertext_payload(work_dir)
        test_tampered_tag_decryption(work_dir)
        test_version_rollback_downgrade(work_dir)
        test_version_rollback_equal(work_dir)
        test_untrusted_source(work_dir)
        test_tampered_master_key(work_dir)

        log("=====================================================================")
        log(" ALL 8 PIPELINE E2E INTEGRATION TESTS PASSED SUCCESSFULLY!")
        log("=====================================================================")
        return 0
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
