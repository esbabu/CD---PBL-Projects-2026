#!/usr/bin/env python3
"""
package_firmware.py - Hybrid Encrypt-Then-Sign Firmware Packaging Tool

Combines symmetric encryption (AES-256-GCM) for confidentiality and
asymmetric cryptography (ECDSA P-256 / SHA-256) for authentication & integrity.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

OTA_MAGIC = 0x3141544F  # 'OTA1' in little-endian
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MASTER_KEY_PATH = PROJECT_ROOT / "keys" / "master_key.bin"


def parse_semver(version_str: str) -> tuple[int, int, int, int]:
    """Parse version string like '1.2.0' or 'v1.2.0' into (packed_u32, maj, min, pat)."""
    s = version_str.strip().lstrip("vV")
    parts = s.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid SemVer string '{version_str}', expected format X.Y.Z")
    maj, min_, pat = int(parts[0]), int(parts[1]), int(parts[2])
    packed = (maj << 16) | (min_ << 8) | pat
    return packed, maj, min_, pat


def load_or_generate_master_key(master_key_path: Path) -> bytes:
    """Load existing 32-byte Pre-Shared Master Key (PSK), or generate 32 random bytes."""
    if master_key_path.is_file():
        key = master_key_path.read_bytes()
        if len(key) != 32:
            raise ValueError(f"Master key file {master_key_path} must be exactly 32 bytes, got {len(key)}")
        return key

    master_key_path.parent.mkdir(parents=True, exist_ok=True)
    key = os.urandom(32)
    master_key_path.write_bytes(key)
    sys.stderr.write(f"[Packager] Generated new Pre-Shared Master Key at {master_key_path}\n")
    return key


def wrap_payload_key(master_key: bytes, iv: bytes, payload_key: bytes) -> bytes:
    """
    Wrap ephemeral 256-bit payload key with 256-bit PSK Master Key
    using AES-CTR keystream blocks with domain separation:
      Block 1: IV (12B) + b"WRA\x01"
      Block 2: IV (12B) + b"WRA\x02"
    """
    if len(master_key) != 32:
        raise ValueError(f"Master key must be exactly 32 bytes (256-bit), got {len(master_key)}")
    if len(iv) != 12:
        raise ValueError(f"IV must be exactly 12 bytes, got {len(iv)}")
    if len(payload_key) != 32:
        raise ValueError(f"Payload key must be exactly 32 bytes, got {len(payload_key)}")

    cipher = Cipher(algorithms.AES(master_key), modes.ECB())
    enc = cipher.encryptor()
    blk1 = enc.update(iv + b"WRA\x01")
    blk2 = enc.update(iv + b"WRA\x02")
    ks = blk1 + blk2
    return bytes(a ^ b for a, b in zip(payload_key, ks))


def unwrap_payload_key(master_key: bytes, iv: bytes, wrapped_key: bytes) -> bytes:
    """Unwrapping is symmetric (CTR XOR keystream)."""
    return wrap_payload_key(master_key, iv, wrapped_key)


def load_or_generate_ecdsa_key(key_path: Path) -> ec.EllipticCurvePrivateKey:
    """Load an existing ECDSA private key in PEM format, or generate one if missing."""
    if key_path.is_file():
        data = key_path.read_bytes()
        priv_key = serialization.load_pem_private_key(data, password=None)
        if not isinstance(priv_key, ec.EllipticCurvePrivateKey):
            raise TypeError(f"Key in {key_path} is not an Elliptic Curve private key")
        return priv_key

    # Generate a new NIST P-256 ECDSA key
    key_path.parent.mkdir(parents=True, exist_ok=True)
    priv_key = ec.generate_private_key(ec.SECP256R1())
    pem_bytes = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key_path.write_bytes(pem_bytes)
    sys.stderr.write(f"[Packager] Generated new ECDSA P-256 private key at {key_path}\n")
    return priv_key


def export_public_key_coordinates(priv_key: ec.EllipticCurvePrivateKey) -> tuple[bytes, bytes]:
    """Export public key X and Y affine coordinates (32 bytes each)."""
    pub_key = priv_key.public_key()
    pub_num = pub_key.public_numbers()
    x_bytes = pub_num.x.to_bytes(32, "big")
    y_bytes = pub_num.y.to_bytes(32, "big")
    return x_bytes, y_bytes


def build_package(
    firmware_bytes: bytes,
    version_str: str,
    priv_key: ec.EllipticCurvePrivateKey,
    master_key: bytes | None = None,
    channel: str = "stable",
    source_url: str = "https://github.com/firmware/release.bin",
    fixed_aes_key: bytes | None = None,
    fixed_iv: bytes | None = None,
) -> tuple[bytes, dict]:
    """
    Encrypt firmware with AES-256-GCM, wrap payload key with Master Key (PSK),
    compute SHA-256 hash over bundle, and sign with ECDSA P-256.
    """
    if master_key is None:
        master_key = load_or_generate_master_key(DEFAULT_MASTER_KEY_PATH)

    packed_ver, maj, min_, pat = parse_semver(version_str)

    # 1. Generate one-time symmetric key & IV
    aes_key = fixed_aes_key or os.urandom(32)  # 256-bit ephemeral AES key
    iv = fixed_iv or os.urandom(12)            # 96-bit standard GCM IV

    # 2. Symmetric Encryption: AES-256-GCM
    aesgcm = AESGCM(aes_key)
    ct_and_tag = aesgcm.encrypt(iv, firmware_bytes, associated_data=None)
    ciphertext = ct_and_tag[:-16]
    tag = ct_and_tag[-16:]
    payload_len = len(ciphertext)

    # 3. Key Wrapping: Encrypt ephemeral AES payload key with Master Key (PSK)
    wrapped_key = wrap_payload_key(master_key, iv, aes_key)

    # 4. Construct Metadata Block (216 bytes)
    # Magic (4B) + Version (4B) + Version_str (16B) + Channel (16B) + Source_url (128B) + IV (12B) + WrappedKey (32B) + Payload_len (4B)
    v_str_bytes = version_str.encode("utf-8")[:15].ljust(16, b"\x00")
    channel_bytes = channel.encode("utf-8")[:15].ljust(16, b"\x00")
    source_bytes = source_url.encode("utf-8")[:127].ljust(128, b"\x00")

    metadata = struct.pack(
        "<II16s16s128s12s32sI",
        OTA_MAGIC,
        packed_ver,
        v_str_bytes,
        channel_bytes,
        source_bytes,
        iv,
        wrapped_key,
        payload_len,
    )

    # 5. Compute Image Hash: SHA-256 of (Metadata + Ciphertext + Tag)
    hash_obj = hashlib.sha256()
    hash_obj.update(metadata)
    hash_obj.update(ciphertext)
    hash_obj.update(tag)
    image_hash = hash_obj.digest()

    # 6. Asymmetric Sign: ECDSA P-256 over SHA-256 digest
    sig_der = priv_key.sign(image_hash, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    r, s = utils.decode_dss_signature(sig_der)
    r_bytes = r.to_bytes(32, "big")
    s_bytes = s.to_bytes(32, "big")
    signature = r_bytes + s_bytes  # 64 bytes raw signature

    # 7. Assemble Final .ota Bundle
    # Header: metadata (216B) + image_hash (32B) + signature (64B) + tag (16B) = 328 bytes
    header = metadata + image_hash + signature + tag
    ota_bundle = header + ciphertext

    pub_x, pub_y = export_public_key_coordinates(priv_key)
    info = {
        "version_str": version_str,
        "packed_version": f"0x{packed_ver:08X}",
        "raw_payload_len": len(firmware_bytes),
        "ciphertext_len": payload_len,
        "bundle_size": len(ota_bundle),
        "master_key_hex": master_key.hex(),
        "aes_key_hex": aes_key.hex(),
        "wrapped_key_hex": wrapped_key.hex(),
        "iv_hex": iv.hex(),
        "tag_hex": tag.hex(),
        "image_hash_hex": image_hash.hex(),
        "sig_r_hex": r_bytes.hex(),
        "sig_s_hex": s_bytes.hex(),
        "pub_x_hex": pub_x.hex(),
        "pub_y_hex": pub_y.hex(),
    }
    return ota_bundle, info


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="package_firmware.py",
        description="Hybrid Encrypt-Then-Sign OTA Firmware Packaging Tool (AES-256-GCM + ECDSA P-256 + PSK Key Wrapping)",
    )
    parser.add_argument("-i", "--input", required=True, help="Path to raw compiled firmware binary")
    parser.add_argument("-v", "--version", required=True, help="Firmware version (e.g. 1.2.0)")
    parser.add_argument("-k", "--key", default="keys/private_key.pem", help="Path to ECDSA private key PEM")
    parser.add_argument(
        "-m",
        "--master-key",
        default="keys/master_key.bin",
        help="Path to Pre-Shared Master Key (PSK) binary file (default: keys/master_key.bin)",
    )
    parser.add_argument("-o", "--output", required=True, help="Path to output .ota package file")
    parser.add_argument("--channel", default="stable", help="Release channel name (default: stable)")
    parser.add_argument(
        "--source-url",
        default="https://github.com/firmware/release.bin",
        help="Trusted source URL",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        sys.stderr.write(f"Error: input firmware '{input_path}' not found.\n")
        return 1

    firmware_bytes = input_path.read_bytes()
    key_path = Path(args.key)
    priv_key = load_or_generate_ecdsa_key(key_path)

    master_key_path = Path(args.master_key)
    if not master_key_path.is_absolute():
        if not master_key_path.is_file() and (PROJECT_ROOT / master_key_path).is_file():
            master_key_path = PROJECT_ROOT / master_key_path
    master_key = load_or_generate_master_key(master_key_path)

    ota_bundle, info = build_package(
        firmware_bytes=firmware_bytes,
        version_str=args.version,
        priv_key=priv_key,
        master_key=master_key,
        channel=args.channel,
        source_url=args.source_url,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(ota_bundle)

    print("==========================================================")
    print(" FIRMWARE PACKAGING COMPLETED (ENCRYPT-THEN-SIGN + PSK)")
    print("==========================================================")
    print(f" Input Binary:     {input_path} ({info['raw_payload_len']} bytes)")
    print(f" Version:          {info['version_str']} (packed: {info['packed_version']})")
    print(f" Output Package:   {out_path} ({info['bundle_size']} bytes)")
    print(f" Master Key (PSK): {info['master_key_hex'][:16]}...{info['master_key_hex'][-16:]}")
    print(f" Ephemeral AES:    {info['aes_key_hex']}")
    print(f" Wrapped Key:      {info['wrapped_key_hex']}")
    print(f" AES-GCM IV:       {info['iv_hex']}")
    print(f" AES-GCM Tag:      {info['tag_hex']}")
    print(f" SHA-256 Hash:     {info['image_hash_hex']}")
    print(f" ECDSA Signature:  r={info['sig_r_hex'][:16]}... s={info['sig_s_hex'][:16]}...")
    print(f" Device PubKey X:  {info['pub_x_hex']}")
    print(f" Device PubKey Y:  {info['pub_y_hex']}")
    print("==========================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
