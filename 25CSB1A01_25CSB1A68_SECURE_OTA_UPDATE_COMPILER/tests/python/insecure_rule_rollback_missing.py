#!/usr/bin/env python3
"""
insecure_rule_rollback_missing.py - OTA Update Without Rollback Prevention
VIOLATION: install() reachable without monotonic version guard.
"""

from src_py.update_handler import (
    OtaPackage,
    DeviceState,
    UpdateStatus,
    verify_signature,
    source_trusted,
    verify_image_hash,
    decrypt_payload_aes_gcm,
    install,
)


def update_firmware(dev: DeviceState, pkg: OtaPackage) -> UpdateStatus:
    if not verify_signature(pkg, dev.public_key_pem):
        return UpdateStatus.ERR_SIGNATURE_INVALID

    if not source_trusted(pkg):
        return UpdateStatus.ERR_SOURCE_UNTRUSTED

    if not verify_image_hash(pkg):
        return UpdateStatus.ERR_IMAGE_HASH_INVALID

    decrypted = decrypt_payload_aes_gcm(pkg, dev.master_key)
    if decrypted is None:
        return UpdateStatus.ERR_DECRYPTION_FAILED

    # VULNERABILITY: Missing anti-rollback version check! Downgrade attack possible.

    install(pkg, decrypted)
    return UpdateStatus.OTA_UPDATE_SUCCESS
