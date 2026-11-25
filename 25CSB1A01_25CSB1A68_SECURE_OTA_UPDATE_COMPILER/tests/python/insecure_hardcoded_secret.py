#!/usr/bin/env python3
"""
insecure_hardcoded_secret.py - OTA Update With Hardcoded Vendor Private Key
VIOLATION: Embedded asymmetric private key in source code.
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

# VULNERABILITY: Hardcoded ECDSA private key literal
EMBEDDED_DEV_KEY = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEILeX8N8m0G0+d3W5S5nK0qV9x7yP6Z1m4J3l9k2q1r2toAoGCCqGSM49
AwEHoUQDQgAE9bC1g...
-----END EC PRIVATE KEY-----"""


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

    if pkg.version <= dev.current_version:
        return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED

    install(pkg, decrypted)
    return UpdateStatus.OTA_UPDATE_SUCCESS
