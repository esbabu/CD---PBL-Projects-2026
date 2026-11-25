"""Attack 11 - Weak password hashing: MD5 hashes from a leaked table crack in seconds."""
import hashlib
import os


def vulnerable_hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def safe_hash_password(password):
    salt = os.urandom(16)
    return salt + hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
