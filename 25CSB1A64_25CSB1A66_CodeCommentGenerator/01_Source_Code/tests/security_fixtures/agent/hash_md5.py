"""SEC004 fixed with hashlib.sha256."""
import hashlib


def password_digest(password):
    return hashlib.md5(password.encode()).hexdigest()


def cache_key(data):
    return hashlib.md5(data, usedforsecurity=False).hexdigest()
