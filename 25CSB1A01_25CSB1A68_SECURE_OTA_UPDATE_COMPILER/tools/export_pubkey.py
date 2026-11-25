#!/usr/bin/env python3
from pathlib import Path
from cryptography.hazmat.primitives import serialization

key_path = Path("keys/test_key.pem")
if not key_path.exists():
    from cryptography.hazmat.primitives.asymmetric import ec
    key = ec.generate_private_key(ec.SECP256R1())
    key_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ))
else:
    key = serialization.load_pem_private_key(key_path.read_bytes(), None)

pn = key.public_key().public_numbers()
x = pn.x.to_bytes(32, "big")
y = pn.y.to_bytes(32, "big")

print(f"X_HEX: {x.hex()}")
print(f"Y_HEX: {y.hex()}")

# Also print as C array
def to_c_arr(b):
    return ", ".join(f"0x{byte:02x}" for byte in b)

print(f"static const uint8_t HARDCODED_PUB_X[32] = {{ {to_c_arr(x)} }};")
print(f"static const uint8_t HARDCODED_PUB_Y[32] = {{ {to_c_arr(y)} }};")
