#!/usr/bin/env python3
"""
insecure_rule_rollback_equal_allowed.py - OTA Update With Rollback Replay Flaw
VIOLATION: Rollback check uses '>=' which permits equal version replay attack. Strict '>' required.
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

    # VULNERABILITY: '>=' allows same-version replay attack!
    if pkg.version >= dev.current_version:
        install(pkg, decrypted)
        return UpdateStatus.OTA_UPDATE_SUCCESS

    return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED
