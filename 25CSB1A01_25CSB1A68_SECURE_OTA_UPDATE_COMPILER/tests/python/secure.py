#!/usr/bin/env python3
"""
secure.py - Canonical Secure OTA Update Routine (Python)
Complies with all 4 CFG dominance gates and zero banned APIs.
Uses uniform function names identical to C:
  updateFirmware, verifySignature, sourceTrusted, verifyImageHash, install
"""

from src_py.update_handler import (
    OtaPackage,
    DeviceState,
    UpdateStatus,
    verifySignature,
    sourceTrusted,
    verifyImageHash,
    decryptPayloadAesGcm,
    install,
    # Snake_case aliases also fully supported
    verify_signature,
    source_trusted,
    verify_image_hash,
    decrypt_payload_aes_gcm,
    update_firmware,
)


def updateFirmware(dev: DeviceState, pkg: OtaPackage) -> UpdateStatus:
    if not pkg:
        return UpdateStatus.ERR_INVALID_PACKAGE

    # 1. Asymmetric ECDSA P-256 signature check (dominates install)
    if not verifySignature(pkg, dev.public_key_pem):
        return UpdateStatus.ERR_SIGNATURE_INVALID

    # 2. Trusted source validation (dominates install)
    if not sourceTrusted(pkg):
        return UpdateStatus.ERR_SOURCE_UNTRUSTED

    # 3. Cryptographic image hash integrity check (dominates install)
    if not verifyImageHash(pkg):
        return UpdateStatus.ERR_IMAGE_HASH_INVALID

    # 4. Authenticated AES-256-GCM decryption
    decrypted = decryptPayloadAesGcm(pkg, dev.master_key)
    if decrypted is None:
        return UpdateStatus.ERR_DECRYPTION_FAILED

    # 5. Strict monotonic anti-rollback guard (strictly dominates install)
    if pkg.version <= dev.current_version:
        return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED

    # 6. Secure installation
    install(pkg, decrypted)

    # 7. Update device state
    dev.current_version = pkg.version
    dev.pending_slot = dev.boot_slot ^ 1
    return UpdateStatus.OTA_UPDATE_SUCCESS


# Snake_case alias for Python standard convention
update_firmware = updateFirmware
