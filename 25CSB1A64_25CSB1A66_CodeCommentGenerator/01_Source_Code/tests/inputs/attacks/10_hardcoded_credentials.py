"""Attack 10 - Hardcoded credentials: anyone with the source (or a leaked repo) gets the keys."""
import os

import requests

API_KEY = "REDACTED_STRIPE_TEST_KEY"
DB_PASSWORD = "Sup3rS3cret!2024"


def vulnerable_fetch_orders():
    return requests.get("https://api.example.com/orders",
                        headers={"Authorization": "Bearer " + API_KEY}, timeout=5)


def safe_fetch_orders():
    key = os.environ["ORDERS_API_KEY"]
    return requests.get("https://api.example.com/orders",
                        headers={"Authorization": "Bearer " + key}, timeout=5)
