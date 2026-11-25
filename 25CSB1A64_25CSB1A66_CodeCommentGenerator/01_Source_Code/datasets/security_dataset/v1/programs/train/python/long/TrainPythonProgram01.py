"""
TrainPythonProgram01 — dataset program.

Generated test case TrainPythonProgram01 of the large-file corpus (tests/large_corpus). The code is
synthetic application code; the vulnerabilities planted in it, and their safe twins, are
listed in tests/large_corpus/manifest.json. Do not deploy.
"""
import ast
import ftplib
import hashlib
import html
import importlib
import json
import logging
import os
import pickle
import random
import re
import secrets
import sqlite3
import ssl
import statistics
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from wsgiref.headers import Headers

import jinja2
import jwt
import ldap3
import lxml.etree
import paramiko
import requests
import yaml
from Crypto.Cipher import AES, DES
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import (Flask, jsonify, make_response, redirect, render_template,
                   render_template_string, request, session, url_for)
from flask_cors import CORS
from ldap3.utils.conv import escape_filter_chars
from pymongo import MongoClient

app = Flask(__name__)
logger = logging.getLogger(__name__)
BASE_DIR = "/srv/data"
mongo = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))


@app.route("/item/badge1")
def badge_item1():
    label = request.args.get("label", "item")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def is_leap_year2(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month2(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year2(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months2(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month2(new_year, new_month))

def audit_loginN3(username, password):
    logger.info("login attempt %s %s", username, password)


def new_api_reference4() -> str:
    return secrets.token_urlsafe(24)


def checksum_item4(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_item4(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_item4(payload), expected)


def recent_commits5(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]

def encrypt_record_safeN6(key, data):
    return AES.new(key, AES.MODE_GCM).encrypt(data)

def hash_passwordN7(password):
    return hashlib.md5(password.encode()).hexdigest()

def configure_formsN8():
    app.config["WTF_CSRF_ENABLED"] = False

@app.route("/greet_safeN9")
def greet_safeN9():
    name = request.args.get("t", "")
    text = "Hello {}".format(name)
    return jsonify(length=len(text))


def summarize_item10(values: Iterable[float]) -> Dict[str, float]:
    data = [float(v) for v in values]
    if not data:
        return {"count": 0, "mean": 0.0, "median": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    ordered = sorted(data)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        median = ordered[middle]
    else:
        median = (ordered[middle - 1] + ordered[middle]) / 2
    mean = sum(ordered) / len(ordered)
    variance = sum((x - mean) ** 2 for x in ordered) / len(ordered)
    return {
        "count": len(ordered),
        "mean": round(mean, 4),
        "median": median,
        "stdev": round(variance ** 0.5, 4),
        "min": ordered[0],
        "max": ordered[-1],
    }


def percentile_item10(values: List[float], fraction: float) -> float:
    if not values:
        raise ValueError("no values")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


@app.route("/item/create11", methods=["POST"])
def create_item11():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@app.route("/item/create12", methods=["POST"])
def create_item12():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201

def run_dev_serverN13():
    app.run(debug=True)

def make_signing_keyN14():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)


class ItemRepository15:
    """Stores item rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS item (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO item (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE item SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM item WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def validate_item_payload16(payload: Dict[str, object]) -> List[str]:
    problems = []
    name = str(payload.get("name", "")).strip()
    if not name:
        problems.append("name is required")
    elif len(name) > 120:
        problems.append("name is longer than 120 characters")
    code = str(payload.get("code", ""))
    if code and not re.fullmatch(r"[A-Z]{3}-[0-9]{4}", code):
        problems.append("code must look like ABC-1234")
    quantity = payload.get("quantity", 0)
    if not isinstance(quantity, int) or quantity < 0:
        problems.append("quantity must be a non-negative integer")
    email = str(payload.get("contact", ""))
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        problems.append("contact must be an e-mail address")
    return problems


def new_api_reference17() -> str:
    return secrets.token_urlsafe(24)


def checksum_item17(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_item17(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_item17(payload), expected)


class ItemWorkflow18:
    """Allowed status transitions for a item order."""

    TRANSITIONS = {
        "draft": {"submitted", "cancelled"},
        "submitted": {"approved", "rejected", "cancelled"},
        "approved": {"shipped", "cancelled"},
        "shipped": {"delivered", "returned"},
        "delivered": {"returned"},
        "rejected": set(),
        "cancelled": set(),
        "returned": set(),
    }

    def __init__(self):
        self.status = "draft"
        self.history: List[str] = ["draft"]

    def can_move_to(self, target: str) -> bool:
        return target in self.TRANSITIONS.get(self.status, set())

    def move_to(self, target: str) -> None:
        if not self.can_move_to(target):
            raise ValueError(f"cannot move from {self.status} to {target}")
        self.status = target
        self.history.append(target)

    def is_final(self) -> bool:
        return not self.TRANSITIONS.get(self.status)

    def undo(self) -> str:
        if len(self.history) < 2:
            raise ValueError("nothing to undo")
        self.history.pop()
        self.status = self.history[-1]
        return self.status

def read_settingsN19(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except:
        return {}


def validate_item_payload20(payload: Dict[str, object]) -> List[str]:
    problems = []
    name = str(payload.get("name", "")).strip()
    if not name:
        problems.append("name is required")
    elif len(name) > 120:
        problems.append("name is longer than 120 characters")
    code = str(payload.get("code", ""))
    if code and not re.fullmatch(r"[A-Z]{3}-[0-9]{4}", code):
        problems.append("code must look like ABC-1234")
    quantity = payload.get("quantity", 0)
    if not isinstance(quantity, int) or quantity < 0:
        problems.append("quantity must be a non-negative integer")
    email = str(payload.get("contact", ""))
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        problems.append("contact must be an e-mail address")
    return problems


def new_api_reference21() -> str:
    return secrets.token_urlsafe(24)


def checksum_item21(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_item21(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_item21(payload), expected)

def audit_loginN22(username, password):
    logger.info("login attempt %s %s", username, password)


def apply_discount23(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill23(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest23(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)

@app.route("/config_safe", methods=["POST"])
def upload_config_safeN24():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))


def recent_commits25(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def paginate_item26(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    total = len(items)
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(max(1, page), pages)
    start = (page - 1) * per_page
    return {
        "page": page,
        "pages": pages,
        "total": total,
        "items": items[start:start + per_page],
        "has_next": page < pages,
        "has_previous": page > 1,
    }


def group_item_by_field26(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))

def audit_login_safeN27(username, password):
    logger.info("login attempt %s (password length %d)", username, len(password))

def encrypt_record_safeN28(key, data):
    return AES.new(key, AES.MODE_GCM).encrypt(data)


class ItemEvents29:
    """Publish/subscribe dispatcher for item events."""

    def __init__(self):
        self.handlers: Dict[str, List[object]] = {}
        self.delivered = 0

    def subscribe(self, event: str, handler) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler) -> bool:
        handlers = self.handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event: str, payload: Dict[str, object]) -> int:
        count = 0
        for handler in list(self.handlers.get(event, [])):
            try:
                handler(payload)
                count += 1
            except ValueError as exc:
                logger.warning("handler for %s rejected the payload: %s", event, exc)
        self.delivered += count
        return count

@app.route("/plugin")
def load_pluginN30():
    module = importlib.import_module(request.args.get("name", "json"))
    return jsonify(module=module.__name__)

def open_ssh_safeN31(host):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host)
    return client

def remove_lockN32(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


@app.route("/item/badge33")
def badge_item33():
    label = request.args.get("label", "item")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def load_item_settings34(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    settings = dict(defaults or {})
    try:
        with open(path, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except FileNotFoundError:
        logger.info("no settings file at %s, using defaults", path)
        return settings
    except ValueError as exc:
        logger.warning("settings file %s is not valid JSON: %s", path, exc)
        return settings
    if not isinstance(loaded, dict):
        raise ValueError("settings must be a JSON object")
    settings.update(loaded)
    return settings


def slugify_item35(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies35(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words35(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."

@app.route("/config_safe", methods=["POST"])
def upload_config_safeN36():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))

def billing_client_safeN37():
    api_key = os.environ.get("BILLING_API_KEY", "")
    return {"service": "billing", "auth": api_key}


def split_csv_line38(line: str, delimiter: str = ",") -> List[str]:
    fields: List[str] = []
    current: List[str] = []
    in_quotes = False
    index = 0
    while index < len(line):
        char = line[index]
        if in_quotes:
            if char == '"' and index + 1 < len(line) and line[index + 1] == '"':
                current.append('"')
                index += 1
            elif char == '"':
                in_quotes = False
            else:
                current.append(char)
        elif char == '"':
            in_quotes = True
        elif char == delimiter:
            fields.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    fields.append("".join(current).strip())
    return fields


def parse_item_rows38(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line38(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line38(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows

def open_ssh_safeN39(host):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host)
    return client


def recent_commits40(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


class ItemCache41:
    """A small least-recently-used cache for item lookups."""

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.entries: Dict[str, object] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_name: str) -> Optional[object]:
        if cache_name in self.entries:
            value = self.entries.pop(cache_name)
            self.entries[cache_name] = value
            self.hits += 1
            return value
        self.misses += 1
        return None

    def put(self, cache_name: str, value: object) -> None:
        if cache_name in self.entries:
            self.entries.pop(cache_name)
        elif len(self.entries) >= self.capacity:
            oldest = next(iter(self.entries))
            self.entries.pop(oldest)
        self.entries[cache_name] = value

    def hit_ratio(self) -> float:
        lookups = self.hits + self.misses
        return self.hits / lookups if lookups else 0.0

    def clear(self) -> None:
        self.entries.clear()
        self.hits = 0
        self.misses = 0


def build_item_report42(rows: List[Dict[str, object]], title: str) -> str:
    lines = [title, "=" * len(title), ""]
    if not rows:
        lines.append("No data.")
        return "\n".join(lines)
    columns = list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    lines.append("  ".join(str(c).ljust(widths[c]) for c in columns))
    lines.append("  ".join("-" * widths[c] for c in columns))
    for row in rows:
        lines.append("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))
    lines.append("")
    lines.append(f"{len(rows)} rows")
    return "\n".join(lines)


class ItemCache43:
    """A small least-recently-used cache for item lookups."""

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.entries: Dict[str, object] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_name: str) -> Optional[object]:
        if cache_name in self.entries:
            value = self.entries.pop(cache_name)
            self.entries[cache_name] = value
            self.hits += 1
            return value
        self.misses += 1
        return None

    def put(self, cache_name: str, value: object) -> None:
        if cache_name in self.entries:
            self.entries.pop(cache_name)
        elif len(self.entries) >= self.capacity:
            oldest = next(iter(self.entries))
            self.entries.pop(oldest)
        self.entries[cache_name] = value

    def hit_ratio(self) -> float:
        lookups = self.hits + self.misses
        return self.hits / lookups if lookups else 0.0

    def clear(self) -> None:
        self.entries.clear()
        self.hits = 0
        self.misses = 0

def pull_inventoryN44():
    return requests.get("http://inventory.acme-corp.com/api/items", timeout=5)

def report_environmentN45():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

def backup_target_safeN46():
    return {"host": os.environ.get("BACKUP_HOST", "localhost"), "port": 873}


class ItemCache47:
    """A small least-recently-used cache for item lookups."""

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.entries: Dict[str, object] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_name: str) -> Optional[object]:
        if cache_name in self.entries:
            value = self.entries.pop(cache_name)
            self.entries[cache_name] = value
            self.hits += 1
            return value
        self.misses += 1
        return None

    def put(self, cache_name: str, value: object) -> None:
        if cache_name in self.entries:
            self.entries.pop(cache_name)
        elif len(self.entries) >= self.capacity:
            oldest = next(iter(self.entries))
            self.entries.pop(oldest)
        self.entries[cache_name] = value

    def hit_ratio(self) -> float:
        lookups = self.hits + self.misses
        return self.hits / lookups if lookups else 0.0

    def clear(self) -> None:
        self.entries.clear()
        self.hits = 0
        self.misses = 0


def validate_item_payload48(payload: Dict[str, object]) -> List[str]:
    problems = []
    name = str(payload.get("name", "")).strip()
    if not name:
        problems.append("name is required")
    elif len(name) > 120:
        problems.append("name is longer than 120 characters")
    code = str(payload.get("code", ""))
    if code and not re.fullmatch(r"[A-Z]{3}-[0-9]{4}", code):
        problems.append("code must look like ABC-1234")
    quantity = payload.get("quantity", 0)
    if not isinstance(quantity, int) or quantity < 0:
        problems.append("quantity must be a non-negative integer")
    email = str(payload.get("contact", ""))
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        problems.append("contact must be an e-mail address")
    return problems


class ItemCache49:
    """A small least-recently-used cache for item lookups."""

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.entries: Dict[str, object] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_name: str) -> Optional[object]:
        if cache_name in self.entries:
            value = self.entries.pop(cache_name)
            self.entries[cache_name] = value
            self.hits += 1
            return value
        self.misses += 1
        return None

    def put(self, cache_name: str, value: object) -> None:
        if cache_name in self.entries:
            self.entries.pop(cache_name)
        elif len(self.entries) >= self.capacity:
            oldest = next(iter(self.entries))
            self.entries.pop(oldest)
        self.entries[cache_name] = value

    def hit_ratio(self) -> float:
        lookups = self.hits + self.misses
        return self.hits / lookups if lookups else 0.0

    def clear(self) -> None:
        self.entries.clear()
        self.hits = 0
        self.misses = 0


def is_leap_year50(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month50(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year50(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months50(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month50(new_year, new_month))


class ItemRepository51:
    """Stores item rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS item (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO item (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE item SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM item WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()

def read_settings_safeN52(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}

def run_server_safeN53():
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

@app.route("/calc_safe")
def calculate_safeN54():
    expression = request.args.get("expr", "0")
    return jsonify(result=ast.literal_eval(expression))

@app.route("/account_safe", methods=["POST"])
def account_lookup_safeN55():
    number = int(request.get_json()["number"])
    account = mongo.bank.accounts.find_one({"number": number})
    return jsonify(found=account is not None)

def run_dev_serverN56():
    app.run(debug=True)

@app.route("/hello_safeN57")
def hello_safeN57():
    name = request.args.get("name", "")
    return "<h1>Hello " + html.escape(name) + "</h1>"

def make_signing_keyN58():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)


class ItemRateLimiter59:
    """Token-bucket rate limiter for item requests (time passed in by the caller)."""

    def __init__(self, rate_per_second: float, burst: int):
        if rate_per_second <= 0 or burst <= 0:
            raise ValueError("rate and burst must be positive")
        self.rate = rate_per_second
        self.burst = burst
        self.available = float(burst)
        self.updated = 0.0

    def allow(self, now: float, cost: float = 1.0) -> bool:
        elapsed = max(0.0, now - self.updated)
        self.available = min(self.burst, self.available + elapsed * self.rate)
        self.updated = now
        if self.available >= cost:
            self.available -= cost
            return True
        return False

    def wait_time(self, cost: float = 1.0) -> float:
        missing = cost - self.available
        return max(0.0, missing / self.rate)


class ItemEvents60:
    """Publish/subscribe dispatcher for item events."""

    def __init__(self):
        self.handlers: Dict[str, List[object]] = {}
        self.delivered = 0

    def subscribe(self, event: str, handler) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler) -> bool:
        handlers = self.handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event: str, payload: Dict[str, object]) -> int:
        count = 0
        for handler in list(self.handlers.get(event, [])):
            try:
                handler(payload)
                count += 1
            except ValueError as exc:
                logger.warning("handler for %s rejected the payload: %s", event, exc)
        self.delivered += count
        return count

def make_signing_keyN61():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)

def pull_inventory_safeN62():
    return requests.get("https://inventory.acme-corp.com/api/items", timeout=5)

@app.route("/grep")
def grep_notesN63():
    pattern = request.args.get("q", "")
    matches = re.findall(pattern, "release notes for the current sprint")
    return jsonify(matches=len(matches))

def encrypt_recordN64(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)


class ItemEvents65:
    """Publish/subscribe dispatcher for item events."""

    def __init__(self):
        self.handlers: Dict[str, List[object]] = {}
        self.delivered = 0

    def subscribe(self, event: str, handler) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler) -> bool:
        handlers = self.handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event: str, payload: Dict[str, object]) -> int:
        count = 0
        for handler in list(self.handlers.get(event, [])):
            try:
                handler(payload)
                count += 1
            except ValueError as exc:
                logger.warning("handler for %s rejected the payload: %s", event, exc)
        self.delivered += count
        return count


@app.route("/item/create66", methods=["POST"])
def create_item66():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201

def fetch_daily_reportN67():
    return requests.get("https://reports.acme-corp.com/daily", verify=False, timeout=10)


@app.route("/item/create68", methods=["POST"])
def create_item68():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201

def upload_invoices_safeN69(host):
    return ftplib.FTP_TLS(host)

def pull_inventoryN70():
    return requests.get("http://inventory.acme-corp.com/api/items", timeout=5)

def report_environmentN71():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

EXPORTERS = {"json": "json", "csv": "csv"}

@app.route("/plugin_safe")
def load_plugin_safeN72():
    module = importlib.import_module(EXPORTERS["json"])
    return jsonify(module=module.__name__)

def upload_invoicesN73(host):
    return ftplib.FTP(host)

def remove_lockN74(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

class ProfileSafe:
    name = ""

@app.route("/profile_safe", methods=["POST"])
def update_profile_safeN75():
    profile = ProfileSafe()
    for key in ("name", "email"):
        setattr(profile, key, request.form.get(key, ""))
    return jsonify(ok=True)

def billing_client_safeN76():
    api_key = os.environ.get("BILLING_API_KEY", "")
    return {"service": "billing", "auth": api_key}

def backup_targetN77():
    return {"host": "10.42.7.186", "port": 873}


class ItemCache78:
    """A small least-recently-used cache for item lookups."""

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.entries: Dict[str, object] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_name: str) -> Optional[object]:
        if cache_name in self.entries:
            value = self.entries.pop(cache_name)
            self.entries[cache_name] = value
            self.hits += 1
            return value
        self.misses += 1
        return None

    def put(self, cache_name: str, value: object) -> None:
        if cache_name in self.entries:
            self.entries.pop(cache_name)
        elif len(self.entries) >= self.capacity:
            oldest = next(iter(self.entries))
            self.entries.pop(oldest)
        self.entries[cache_name] = value

    def hit_ratio(self) -> float:
        lookups = self.hits + self.misses
        return self.hits / lookups if lookups else 0.0

    def clear(self) -> None:
        self.entries.clear()
        self.hits = 0
        self.misses = 0


def new_api_reference79() -> str:
    return secrets.token_urlsafe(24)


def checksum_item79(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_item79(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_item79(payload), expected)


def build_item_report80(rows: List[Dict[str, object]], title: str) -> str:
    lines = [title, "=" * len(title), ""]
    if not rows:
        lines.append("No data.")
        return "\n".join(lines)
    columns = list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    lines.append("  ".join(str(c).ljust(widths[c]) for c in columns))
    lines.append("  ".join("-" * widths[c] for c in columns))
    for row in rows:
        lines.append("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))
    lines.append("")
    lines.append(f"{len(rows)} rows")
    return "\n".join(lines)

def scratch_export_file_safeN81():
    return tempfile.mkstemp(suffix=".csv")


def summarize_item82(values: Iterable[float]) -> Dict[str, float]:
    data = [float(v) for v in values]
    if not data:
        return {"count": 0, "mean": 0.0, "median": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    ordered = sorted(data)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        median = ordered[middle]
    else:
        median = (ordered[middle - 1] + ordered[middle]) / 2
    mean = sum(ordered) / len(ordered)
    variance = sum((x - mean) ** 2 for x in ordered) / len(ordered)
    return {
        "count": len(ordered),
        "mean": round(mean, 4),
        "median": median,
        "stdev": round(variance ** 0.5, 4),
        "min": ordered[0],
        "max": ordered[-1],
    }


def percentile_item82(values: List[float], fraction: float) -> float:
    if not values:
        raise ValueError("no values")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight

def encrypt_recordN83(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)

@app.route("/account_safe", methods=["POST"])
def account_lookup_safeN84():
    number = int(request.get_json()["number"])
    account = mongo.bank.accounts.find_one({"number": number})
    return jsonify(found=account is not None)


def merge_sort85(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort85(values[:middle])
    right = merge_sort85(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search85(values: List[int], target: int) -> int:
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1

@app.route("/orders_safe")
def find_orders_safeN86():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
    return jsonify(rows=rows)

@app.route("/greetN87")
def greetN87():
    template = request.args.get("t", "")
    text = template.format(user=app)
    return jsonify(length=len(text))

@app.route("/config_safe", methods=["POST"])
def upload_config_safeN88():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))

@app.route("/config", methods=["POST"])
def upload_configN89():
    config = yaml.load(request.data, Loader=yaml.Loader)
    return jsonify(sections=len(config))

def remove_lock_safeN90(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug("lock file already removed")


def reorder_plan_item91(stock: Dict[str, int], daily_use: Dict[str, float],
                           lead_days: int = 7, safety_days: int = 3) -> Dict[str, int]:
    plan = {}
    for item, on_hand in sorted(stock.items()):
        usage = daily_use.get(item, 0.0)
        if usage <= 0:
            continue
        needed = int(usage * (lead_days + safety_days) + 0.999)
        if on_hand < needed:
            plan[item] = needed - on_hand
    return plan


def days_of_cover_item91(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@dataclass
class ItemRecord92:
    """A item record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "ItemRecord92":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return ItemRecord92(self.identifier, self.name, quantity, self.unit_price,
                                list(self.labels or []))

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.identifier,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "labels": list(self.labels or []),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ItemRecord92":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )

def billing_client_safeN93():
    api_key = os.environ.get("BILLING_API_KEY", "")
    return {"service": "billing", "auth": api_key}


class ItemRepository94:
    """Stores item rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS item (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO item (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM item WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE item SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM item WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()

def read_settingsN95(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except:
        return {}

@app.route("/orders_safe")
def find_orders_safeN96():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
    return jsonify(rows=rows)

@app.route("/config_safe", methods=["POST"])
def upload_config_safeN97():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))


@app.route("/item/list98")
def list_item98():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"item {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_item98(items, page, per_page) if "paginate_item98" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})

def pull_inventory_safeN99():
    return requests.get("https://inventory.acme-corp.com/api/items", timeout=5)

def publish_logN100(path):
    os.chmod(path, 0o777)

def remove_lock_safeN101(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug("lock file already removed")


@app.route("/item/list102")
def list_item102():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"item {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_item102(items, page, per_page) if "paginate_item102" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})

@app.route("/plugin")
def load_pluginN103():
    module = importlib.import_module(request.args.get("name", "json"))
    return jsonify(module=module.__name__)

@app.route("/orders_safe")
def find_orders_safeN104():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
    return jsonify(rows=rows)

@app.route("/restore", methods=["POST"])
def restore_stateN105():
    state = pickle.loads(request.data)
    return jsonify(keys=len(state))

def configure_formsN106():
    app.config["WTF_CSRF_ENABLED"] = False


class ItemWorkflow107:
    """Allowed status transitions for a item order."""

    TRANSITIONS = {
        "draft": {"submitted", "cancelled"},
        "submitted": {"approved", "rejected", "cancelled"},
        "approved": {"shipped", "cancelled"},
        "shipped": {"delivered", "returned"},
        "delivered": {"returned"},
        "rejected": set(),
        "cancelled": set(),
        "returned": set(),
    }

    def __init__(self):
        self.status = "draft"
        self.history: List[str] = ["draft"]

    def can_move_to(self, target: str) -> bool:
        return target in self.TRANSITIONS.get(self.status, set())

    def move_to(self, target: str) -> None:
        if not self.can_move_to(target):
            raise ValueError(f"cannot move from {self.status} to {target}")
        self.status = target
        self.history.append(target)

    def is_final(self) -> bool:
        return not self.TRANSITIONS.get(self.status)

    def undo(self) -> str:
        if len(self.history) < 2:
            raise ValueError("nothing to undo")
        self.history.pop()
        self.status = self.history[-1]
        return self.status

@app.route("/prefs")
def save_prefsN108():
    resp = make_response("saved")
    resp.set_cookie("theme", "dark", secure=False, httponly=True)
    return resp


@app.route("/item/list109")
def list_item109():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"item {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_item109(items, page, per_page) if "paginate_item109" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def build_item_report110(rows: List[Dict[str, object]], title: str) -> str:
    lines = [title, "=" * len(title), ""]
    if not rows:
        lines.append("No data.")
        return "\n".join(lines)
    columns = list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    lines.append("  ".join(str(c).ljust(widths[c]) for c in columns))
    lines.append("  ".join("-" * widths[c] for c in columns))
    for row in rows:
        lines.append("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))
    lines.append("")
    lines.append(f"{len(rows)} rows")
    return "\n".join(lines)


def new_api_reference111() -> str:
    return secrets.token_urlsafe(24)


def checksum_item111(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_item111(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_item111(payload), expected)


class ItemEvents112:
    """Publish/subscribe dispatcher for item events."""

    def __init__(self):
        self.handlers: Dict[str, List[object]] = {}
        self.delivered = 0

    def subscribe(self, event: str, handler) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler) -> bool:
        handlers = self.handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event: str, payload: Dict[str, object]) -> int:
        count = 0
        for handler in list(self.handlers.get(event, [])):
            try:
                handler(payload)
                count += 1
            except ValueError as exc:
                logger.warning("handler for %s rejected the payload: %s", event, exc)
        self.delivered += count
        return count


def is_leap_year113(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month113(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year113(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months113(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month113(new_year, new_month))


def split_csv_line114(line: str, delimiter: str = ",") -> List[str]:
    fields: List[str] = []
    current: List[str] = []
    in_quotes = False
    index = 0
    while index < len(line):
        char = line[index]
        if in_quotes:
            if char == '"' and index + 1 < len(line) and line[index + 1] == '"':
                current.append('"')
                index += 1
            elif char == '"':
                in_quotes = False
            else:
                current.append(char)
        elif char == '"':
            in_quotes = True
        elif char == delimiter:
            fields.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    fields.append("".join(current).strip())
    return fields


def parse_item_rows114(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line114(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line114(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows

def enable_cross_origin_safeN115():
    CORS(app, origins=["https://shop.acme-corp.com"])


@app.route("/item/create116", methods=["POST"])
def create_item116():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201

@app.route("/downloadN117")
def downloadN117():
    name = request.args.get("file", "")
    with open(os.path.join(BASE_DIR, name), "rb") as fh:
        return jsonify(size=len(fh.read()))


def is_leap_year118(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month118(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year118(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months118(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month118(new_year, new_month))

def make_signing_keyN119():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)


def transpose120(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply120(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose120(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity120(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


class ItemRateLimiter121:
    """Token-bucket rate limiter for item requests (time passed in by the caller)."""

    def __init__(self, rate_per_second: float, burst: int):
        if rate_per_second <= 0 or burst <= 0:
            raise ValueError("rate and burst must be positive")
        self.rate = rate_per_second
        self.burst = burst
        self.available = float(burst)
        self.updated = 0.0

    def allow(self, now: float, cost: float = 1.0) -> bool:
        elapsed = max(0.0, now - self.updated)
        self.available = min(self.burst, self.available + elapsed * self.rate)
        self.updated = now
        if self.available >= cost:
            self.available -= cost
            return True
        return False

    def wait_time(self, cost: float = 1.0) -> float:
        missing = cost - self.available
        return max(0.0, missing / self.rate)


def validate_item_payload122(payload: Dict[str, object]) -> List[str]:
    problems = []
    name = str(payload.get("name", "")).strip()
    if not name:
        problems.append("name is required")
    elif len(name) > 120:
        problems.append("name is longer than 120 characters")
    code = str(payload.get("code", ""))
    if code and not re.fullmatch(r"[A-Z]{3}-[0-9]{4}", code):
        problems.append("code must look like ABC-1234")
    quantity = payload.get("quantity", 0)
    if not isinstance(quantity, int) or quantity < 0:
        problems.append("quantity must be a non-negative integer")
    email = str(payload.get("contact", ""))
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        problems.append("contact must be an e-mail address")
    return problems


@dataclass
class ItemRecord123:
    """A item record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "ItemRecord123":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return ItemRecord123(self.identifier, self.name, quantity, self.unit_price,
                                list(self.labels or []))

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.identifier,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "labels": list(self.labels or []),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ItemRecord123":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )

def read_claims_safeN124(token, key):
    return jwt.decode(token, key, algorithms=["HS256"])

def configure_forms_safeN125():
    app.config["WTF_CSRF_ENABLED"] = True

def upload_invoices_safeN126(host):
    return ftplib.FTP_TLS(host)


def recent_commits127(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]

def upload_invoicesN128(host):
    return ftplib.FTP(host)

def remove_lock_safeN129(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug("lock file already removed")


@app.route("/item/create130", methods=["POST"])
def create_item130():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def build_item_report131(rows: List[Dict[str, object]], title: str) -> str:
    lines = [title, "=" * len(title), ""]
    if not rows:
        lines.append("No data.")
        return "\n".join(lines)
    columns = list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    lines.append("  ".join(str(c).ljust(widths[c]) for c in columns))
    lines.append("  ".join("-" * widths[c] for c in columns))
    for row in rows:
        lines.append("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))
    lines.append("")
    lines.append(f"{len(rows)} rows")
    return "\n".join(lines)


def shortest_path132(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
    if start == goal:
        return [start]
    previous: Dict[str, str] = {}
    frontier = [start]
    seen = {start}
    while frontier:
        next_frontier = []
        for node in frontier:
            for neighbour in graph.get(node, []):
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                previous[neighbour] = node
                if neighbour == goal:
                    path = [goal]
                    while path[-1] != start:
                        path.append(previous[path[-1]])
                    return list(reversed(path))
                next_frontier.append(neighbour)
        frontier = next_frontier
    return []

def encrypt_recordN133(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)


def paginate_item134(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    total = len(items)
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(max(1, page), pages)
    start = (page - 1) * per_page
    return {
        "page": page,
        "pages": pages,
        "total": total,
        "items": items[start:start + per_page],
        "has_next": page < pages,
        "has_previous": page > 1,
    }


def group_item_by_field134(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def merge_sort135(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort135(values[:middle])
    right = merge_sort135(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search135(values: List[int], target: int) -> int:
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1

@app.route("/account_safe", methods=["POST"])
def account_lookup_safeN136():
    number = int(request.get_json()["number"])
    account = mongo.bank.accounts.find_one({"number": number})
    return jsonify(found=account is not None)

def upload_invoices_safeN137(host):
    return ftplib.FTP_TLS(host)

def fingerprintN138(data):
    return hashlib.sha256(data.encode()).hexdigest()

