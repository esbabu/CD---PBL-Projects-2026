"""Attack 12 - Predictable token: random is seeded from the clock, so reset tokens can be guessed."""
import random
import secrets
import string


def vulnerable_reset_token():
    token = "".join(random.choice(string.ascii_letters) for _ in range(32))
    return token


def safe_reset_token():
    token = secrets.token_urlsafe(32)
    return token
