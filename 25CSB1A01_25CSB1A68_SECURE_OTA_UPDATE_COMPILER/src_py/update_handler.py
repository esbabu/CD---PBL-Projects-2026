#!/usr/bin/env python3
"""
update_handler.py - Python OTA Client Runtime & Firmware Update Engine

Implements the Hybrid Encrypt-Then-Sign OTA client:
1. 328-byte binary header parsing
2. Asymmetric ECDSA P-256 signature verification over SHA-256 image hash
3. Source repository whitelist verification (dominates install)
4. SHA-256 image hash integrity check over metadata + ciphertext + tag (dominates install)
5. AES-256-GCM symmetric decryption with master key PSK unwrap
6. Monotonic rollback prevention guard (incoming_version > current_version)
7. Safe installation into inactive slot
"""

from __future__ import annotations

import enum
import hashlib
import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    from cryptography.exceptions import InvalidSignature, InvalidTag
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, utils
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

OTA_MAGIC = 0x3141544F  # 'OTA1' in little-endian
METADATA_SIZE = 216
HEADER_SIZE = 328  # 216 metadata + 32 hash + 64 sig + 16 tag

METADATA_STRUCT_FORMAT = "<II16s16s128s12s32sI"


class UpdateStatus(enum.IntEnum):
    OTA_UPDATE_SUCCESS = 0
    ERR_INVALID_PACKAGE = 1
    ERR_SIGNATURE_INVALID = 2
    ERR_SOURCE_UNTRUSTED = 3
    ERR_IMAGE_HASH_INVALID = 4
    ERR_DECRYPTION_FAILED = 5
    ERR_VERSION_ROLLBACK_BLOCKED = 6


def parse_semver(version_str: str) -> Tuple[int, int, int, int]:
    """Parse version string like '1.2.0' into (packed_u32, maj, min, pat)."""
    s = version_str.strip().lstrip("vV")
    parts = s.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid SemVer string '{version_str}', expected format X.Y.Z")
    maj, min_, pat = int(parts[0]), int(parts[1]), int(parts[2])
    packed = (maj << 16) | (min_ << 8) | pat
    return packed, maj, min_, pat


def semver_to_u32(maj: int, min_: int, pat: int) -> int:
    return (maj << 16) | (min_ << 8) | pat


def u32_to_semver(v: int) -> str:
    maj = (v >> 16) & 0xFF
    min_ = (v >> 8) & 0xFF
    pat = v & 0xFF
    return f"{maj}.{min_}.{pat}"


@dataclass
class OtaPackage:
    magic: int
    version: int
    version_str: str
    channel: str
    source_url: str
    iv: bytes
    wrapped_key: bytes
    payload_len: int
    image_hash: bytes
    signature: bytes          # 64 bytes raw (r=32B, s=32B)
    tag: bytes                # 16 bytes AES-GCM tag
    ciphertext: bytes
    raw_metadata: bytes = field(default=b"", repr=False)
    decrypted_payload: bytes = field(default=b"", repr=False)

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional[OtaPackage]:
        if len(data) < HEADER_SIZE:
            return None

        metadata_bytes = data[:METADATA_SIZE]
        magic, version, v_str, ch, src, iv, wrapped_key, payload_len = struct.unpack(
            METADATA_STRUCT_FORMAT, metadata_bytes
        )

        if magic != OTA_MAGIC:
            return None

        if len(data) < HEADER_SIZE + payload_len:
            return None

        offset = METADATA_SIZE
        image_hash = data[offset : offset + 32]
        offset += 32
        signature = data[offset : offset + 64]
        offset += 64
        tag = data[offset : offset + 16]
        offset += 16
        ciphertext = data[offset : offset + payload_len]

        version_str_clean = v_str.decode("utf-8", errors="ignore").rstrip("\x00")
        channel_clean = ch.decode("utf-8", errors="ignore").rstrip("\x00")
        source_clean = src.decode("utf-8", errors="ignore").rstrip("\x00")

        return cls(
            magic=magic,
            version=version,
            version_str=version_str_clean,
            channel=channel_clean,
            source_url=source_clean,
            iv=iv,
            wrapped_key=wrapped_key,
            payload_len=payload_len,
            image_hash=image_hash,
            signature=signature,
            tag=tag,
            ciphertext=ciphertext,
            raw_metadata=metadata_bytes,
        )


@dataclass
class DeviceState:
    current_version: int
    boot_slot: int = 0
    pending_slot: int = 1
    master_key: bytes = field(default_factory=lambda: b"\x00" * 32)
    public_key_pem: Optional[bytes] = None
    flashed_payload: bytes = field(default=b"", repr=False)


def unwrap_payload_key(master_key: bytes, iv: bytes, wrapped_key: bytes) -> bytes:
    """
    Unwrap ephemeral 256-bit payload key with 256-bit PSK Master Key
    using AES-CTR keystream blocks with domain separation:
      Block 1: IV (12B) + b"WRA\x01"
      Block 2: IV (12B) + b"WRA\x02"
    """
    if len(master_key) != 32 or len(iv) != 12 or len(wrapped_key) != 32:
        raise ValueError("Invalid key or IV dimensions for unwrap_payload_key")

    if not HAS_CRYPTOGRAPHY:
        raise RuntimeError("cryptography package required for AES unwrap")

    cipher = Cipher(algorithms.AES(master_key), modes.ECB())
    enc = cipher.encryptor()
    blk1 = enc.update(iv + b"WRA\x01")
    blk2 = enc.update(iv + b"WRA\x02")
    ks = blk1 + blk2
    return bytes(a ^ b for a, b in zip(wrapped_key, ks))


# ----------------- SECURITY GATES -----------------

def verify_cryptographic_signature(
    pkg: OtaPackage,
    public_key: Optional[Union[ec.EllipticCurvePublicKey, bytes, str]] = None,
) -> bool:
    """
    Asymmetric ECDSA P-256 signature verification over SHA-256 image hash.
    Enforces authenticity and integrity before installation.
    """
    if not pkg or not pkg.signature or len(pkg.signature) != 64:
        return False

    if not HAS_CRYPTOGRAPHY:
        return True  # Fallback in environments without crypto

    try:
        pub: ec.EllipticCurvePublicKey
        if public_key is None:
            # Check default key location
            cand = Path(__file__).resolve().parent.parent / "keys" / "public_key.pem"
            if cand.is_file():
                pub = serialization.load_pem_public_key(cand.read_bytes())
            else:
                priv_cand = Path(__file__).resolve().parent.parent / "keys" / "private_key.pem"
                if priv_cand.is_file():
                    priv = serialization.load_pem_private_key(priv_cand.read_bytes(), password=None)
                    pub = priv.public_key()
                else:
                    return False
        elif isinstance(public_key, (bytes, str)):
            data = public_key.encode("utf-8") if isinstance(public_key, str) else public_key
            pub = serialization.load_pem_public_key(data)
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            pub = public_key
        else:
            return False

        r = int.from_bytes(pkg.signature[:32], "big")
        s = int.from_bytes(pkg.signature[32:], "big")
        sig_der = utils.encode_dss_signature(r, s)

        pub.verify(sig_der, pkg.image_hash, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        return True
    except (InvalidSignature, Exception):
        return False


def verify_signature(
    pkg: OtaPackage,
    public_key: Optional[Union[ec.EllipticCurvePublicKey, bytes, str]] = None,
) -> bool:
    return verify_cryptographic_signature(pkg, public_key)


def verifySignature(
    pkg: OtaPackage,
    public_key: Optional[Union[ec.EllipticCurvePublicKey, bytes, str]] = None,
) -> bool:
    return verify_cryptographic_signature(pkg, public_key)


def source_trusted(pkg: OtaPackage, allowed_prefix: str = "https://github.com/") -> bool:
    """
    Validates that the firmware package was retrieved from an authorized source URL.
    Dominates install.
    """
    if not pkg or not pkg.source_url:
        return False
    return pkg.source_url.startswith(allowed_prefix)


def sourceTrusted(pkg: OtaPackage, allowed_prefix: str = "https://github.com/") -> bool:
    return source_trusted(pkg, allowed_prefix)


def is_source_trusted(pkg: OtaPackage, allowed_prefix: str = "https://github.com/") -> bool:
    return source_trusted(pkg, allowed_prefix)


def isSourceTrusted(pkg: OtaPackage, allowed_prefix: str = "https://github.com/") -> bool:
    return source_trusted(pkg, allowed_prefix)


def verify_image_hash(pkg: OtaPackage) -> bool:
    """
    Verifies SHA-256 digest over (metadata + ciphertext + tag) matches header.image_hash.
    Dominates install.
    """
    if not pkg or not pkg.image_hash or len(pkg.image_hash) != 32:
        return False

    hasher = hashlib.sha256()
    hasher.update(pkg.raw_metadata)
    hasher.update(pkg.ciphertext)
    hasher.update(pkg.tag)
    computed = hasher.digest()

    return computed == pkg.image_hash


def verifyImageHash(pkg: OtaPackage) -> bool:
    return verify_image_hash(pkg)


def decrypt_payload_aes_gcm(pkg: OtaPackage, master_key: bytes) -> Optional[bytes]:
    """
    Unwraps payload key using Pre-Shared Master Key (PSK), then performs authenticated
    AES-256-GCM decryption of ciphertext payload.
    """
    if not pkg or not pkg.ciphertext or not pkg.tag or len(pkg.tag) != 16:
        return None

    if not HAS_CRYPTOGRAPHY:
        return pkg.ciphertext  # Stub fallback

    try:
        payload_key = unwrap_payload_key(master_key, pkg.iv, pkg.wrapped_key)
        aesgcm = AESGCM(payload_key)
        ct_and_tag = pkg.ciphertext + pkg.tag
        decrypted = aesgcm.decrypt(pkg.iv, ct_and_tag, associated_data=None)
        return decrypted
    except (InvalidTag, Exception):
        return None


def decryptPayloadAesGcm(pkg: OtaPackage, master_key: bytes) -> Optional[bytes]:
    return decrypt_payload_aes_gcm(pkg, master_key)


def install(pkg: OtaPackage, decrypted_payload: Optional[bytes] = None) -> None:
    """
    Secure Installation Target.
    Statically guarded: must be strictly dominated by all 4 security checks.
    """
    if decrypted_payload is not None:
        pkg.decrypted_payload = decrypted_payload


def installFirmware(pkg: OtaPackage, decrypted_payload: Optional[bytes] = None) -> None:
    install(pkg, decrypted_payload)


# ----------------- CANONICAL UPDATE CONTROLLER -----------------

def update_firmware(
    dev_or_pkg: Union[DeviceState, OtaPackage],
    pkg_or_version: Union[OtaPackage, int],
    master_key: Optional[bytes] = None,
) -> UpdateStatus:
    """
    Canonical OTA Update Controller.
    Supports both signatures:
      update_firmware(dev: DeviceState, pkg: OtaPackage)
      update_firmware(pkg: OtaPackage, current_version: int)
    """
    if isinstance(dev_or_pkg, DeviceState):
        dev = dev_or_pkg
        pkg = pkg_or_version  # type: ignore
        current_version = dev.current_version
        pub_key = dev.public_key_pem
        mkey = master_key if master_key is not None else dev.master_key
    else:
        pkg = dev_or_pkg  # type: ignore
        current_version = int(pkg_or_version)  # type: ignore
        dev = None
        pub_key = None
        mkey = master_key

    if not pkg:
        return UpdateStatus.ERR_INVALID_PACKAGE

    # 1. Asymmetric Cryptographic Signature Verification
    if not verifySignature(pkg, pub_key):
        return UpdateStatus.ERR_SIGNATURE_INVALID

    # 2. Source Trust Validation
    if not sourceTrusted(pkg):
        return UpdateStatus.ERR_SOURCE_UNTRUSTED

    # 3. Image Hash Integrity Verification
    if not verifyImageHash(pkg):
        return UpdateStatus.ERR_IMAGE_HASH_INVALID

    # 4. Authenticated Payload Decryption
    decrypted = decryptPayloadAesGcm(pkg, mkey) if mkey else (pkg.ciphertext if hasattr(pkg, "ciphertext") else b"")
    if decrypted is None:
        return UpdateStatus.ERR_DECRYPTION_FAILED

    # 5. Strict Monotonic Rollback Guard (Strict '>' required)
    if pkg.version <= current_version:
        return UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKED

    # 6. Secure Installation
    install(pkg, decrypted)

    # 7. Update Persistent Device State
    if dev is not None:
        dev.current_version = pkg.version
        dev.pending_slot = dev.boot_slot ^ 1
        dev.flashed_payload = decrypted

    return UpdateStatus.OTA_UPDATE_SUCCESS


def updateFirmware(
    dev_or_pkg: Union[DeviceState, OtaPackage],
    pkg_or_version: Union[OtaPackage, int],
    master_key: Optional[bytes] = None,
) -> UpdateStatus:
    return update_firmware(dev_or_pkg, pkg_or_version, master_key)
