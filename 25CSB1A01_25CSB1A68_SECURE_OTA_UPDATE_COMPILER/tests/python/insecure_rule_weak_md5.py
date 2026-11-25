#!/usr/bin/env python3
"""
insecure_rule_weak_md5.py - OTA Update With Weak MD5 Cryptographic Hash
VIOLATION: MD5 is cryptographically broken and prohibited. Use SHA-256.
"""

import hashlib
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
    # VULNERABILITY: Use of weak hash function MD5
    legacy_md5 = hashlib.md5(pkg.ciphertext).hexdigest()

    if not verify_signature(pkg, dev.public_key_pem):
        return UpdateStatus.ERR_SIGNATURE_INVALID

    if not source_trusted(pkg):
        return UpdateStatus.ERR_SOURCE_UNTRUSTED

    if not verify_image_hash(pkg):
        return UpdateStatus.ERR_IMAGE_HASH_INVALID

    decrypted = decrypt_payload_aes_gcm(pkg, dev.master_key)
    if decrypted is None:
        return UpdateStatus.ERR_DECRYPTION_FAILED

    if pkg.version <= dev.current_version:
        return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED

    install(pkg, decrypted)
    return UpdateStatus.OTA_UPDATE_SUCCESS
