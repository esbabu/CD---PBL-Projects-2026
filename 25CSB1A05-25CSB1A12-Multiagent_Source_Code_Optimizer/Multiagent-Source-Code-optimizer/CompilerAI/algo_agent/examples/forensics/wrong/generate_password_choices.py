# Known-wrong rewrite: random.choices instead of sequential random.choice
import random

def generate_password():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    # Consumes RNG differently from 8 sequential random.choice calls
    return "".join(random.choices(chars, k=8))
