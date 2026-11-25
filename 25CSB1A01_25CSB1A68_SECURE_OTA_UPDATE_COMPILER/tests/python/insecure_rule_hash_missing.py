#!/usr/bin/env python3
"""
insecure_rule_hash_missing.py - OTA Update Without Image Hash Integrity Check
VIOLATION: install() reachable without verify_image_hash() dominance check.
"""

from src_py.update_handler import (
    OtaPackage,
    DeviceState,
    UpdateStatus,
    verify_signature,
    source_trusted,
    decrypt_payload_aes_gcm,
    install,
)


def update_firmware(dev: DeviceState, pkg: OtaPackage) -> UpdateStatus:
    if not verify_signature(pkg, dev.public_key_pem):
        return UpdateStatus.ERR_SIGNATURE_INVALID

    if not source_trusted(pkg):
        return UpdateStatus.ERR_SOURCE_UNTRUSTED

    # VULNERABILITY: Missing verify_image_hash() check!

    decrypted = decrypt_payload_aes_gcm(pkg, dev.master_key)
    if decrypted is None:
        return UpdateStatus.ERR_DECRYPTION_FAILED

    if pkg.version <= dev.current_version:
        return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED

    install(pkg, decrypted)
    return UpdateStatus.OTA_UPDATE_SUCCESS
