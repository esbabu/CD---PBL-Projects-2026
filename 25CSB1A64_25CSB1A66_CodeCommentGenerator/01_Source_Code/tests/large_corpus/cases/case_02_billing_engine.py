"""
Billing Engine — Invoice service module.

Generated test case 02 of the large-file corpus (tests/large_corpus). The code is
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


def summarize_invoice02087(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02087(values: List[float], fraction: float) -> float:
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


def apply_discount02104(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill02104(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest02104(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


class InvoiceRepository02024:
    """Stores invoice rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS invoice (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO invoice (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE invoice SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM invoice WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def paginate_invoice02062(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02062(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def apply_discount02076(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill02076(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest02076(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def build_invoice_report02070(rows: List[Dict[str, object]], title: str) -> str:
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


@app.route("/prefs_safe02019")
def save_prefs_safe02019():
    resp = make_response("saved")
    resp.set_cookie("theme", "dark", secure=True, httponly=True, samesite="Lax")
    return resp


def new_api_reference02059() -> str:
    return secrets.token_urlsafe(24)


def checksum_invoice02059(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_invoice02059(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_invoice02059(payload), expected)


class InvoiceRateLimiter02033:
    """Token-bucket rate limiter for invoice requests (time passed in by the caller)."""

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


def report_environment_safe02018():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                              autoescape=jinja2.select_autoescape())


@app.route("/download02003")
def download02003():
    name = request.args.get("file", "")
    with open(os.path.join(BASE_DIR, name), "rb") as fh:
        return jsonify(size=len(fh.read()))


def slugify_invoice02089(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies02089(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words02089(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def reorder_plan_invoice02046(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_invoice02046(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


class InvoiceRateLimiter02094:
    """Token-bucket rate limiter for invoice requests (time passed in by the caller)."""

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


def recent_commits02064(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


@app.route("/continue02007")
def continue_to02007():
    target = request.args.get("next", "/")
    return redirect(target)


@app.route("/staff02010")
def staff_record02010():
    eid = request.args.get("id", "")
    tree = lxml.etree.parse(os.path.join(BASE_DIR, "staff.xml"))
    nodes = tree.xpath("//employee[@id='" + eid + "']")
    return jsonify(count=len(nodes))


def apply_discount02027(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill02027(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest02027(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def serve_local_safe02014():
    app.run(host="127.0.0.1", port=8080)


def generate_reset_token02001():
    return str(random.randint(100000, 999999))


class InvoiceRepository02028:
    """Stores invoice rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS invoice (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO invoice (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE invoice SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM invoice WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


class InvoiceCache02023:
    """A small least-recently-used cache for invoice lookups."""

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


def paginate_invoice02053(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02053(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def new_api_reference02073() -> str:
    return secrets.token_urlsafe(24)


def checksum_invoice02073(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_invoice02073(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_invoice02073(payload), expected)


def recent_commits02084(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


class InvoiceCache02101:
    """A small least-recently-used cache for invoice lookups."""

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


def split_csv_line02095(line: str, delimiter: str = ",") -> List[str]:
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


def parse_invoice_rows02095(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line02095(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line02095(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def paginate_invoice02097(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02097(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def validate_invoice_payload02047(payload: Dict[str, object]) -> List[str]:
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


def paginate_invoice02032(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02032(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


@app.route("/import02008", methods=["POST"])
def import_xml02008():
    parser = lxml.etree.XMLParser(resolve_entities=True)
    doc = lxml.etree.fromstring(request.data, parser)
    return jsonify(tag=doc.tag)


class InvoiceRateLimiter02065:
    """Token-bucket rate limiter for invoice requests (time passed in by the caller)."""

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


class InvoiceCache02099:
    """A small least-recently-used cache for invoice lookups."""

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


class InvoiceWorkflow02060:
    """Allowed status transitions for a invoice order."""

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


def new_api_reference02031() -> str:
    return secrets.token_urlsafe(24)


def checksum_invoice02031(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_invoice02031(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_invoice02031(payload), expected)


class InvoiceRateLimiter02057:
    """Token-bucket rate limiter for invoice requests (time passed in by the caller)."""

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


@app.route("/invoice/create02050", methods=["POST"])
def create_invoice02050():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def recent_commits02022(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


@app.route("/invoice/create02067", methods=["POST"])
def create_invoice02067():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def recent_commits02040(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


@app.route("/invoice/create02029", methods=["POST"])
def create_invoice02029():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def reorder_plan_invoice02096(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_invoice02096(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@app.route("/invoice/list02092")
def list_invoice02092():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"invoice {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_invoice02092(items, page, per_page) if "paginate_invoice02092" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


@app.route("/invoice/badge02035")
def badge_invoice02035():
    label = request.args.get("label", "invoice")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@dataclass
class InvoiceRecord02100:
    """A invoice record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "InvoiceRecord02100":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return InvoiceRecord02100(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "InvoiceRecord02100":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def split_csv_line02063(line: str, delimiter: str = ",") -> List[str]:
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


def parse_invoice_rows02063(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line02063(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line02063(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


class InvoiceEvents02058:
    """Publish/subscribe dispatcher for invoice events."""

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


def paginate_invoice02085(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02085(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def paginate_invoice02075(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02075(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def transpose02079(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply02079(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose02079(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity02079(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def paginate_invoice02098(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02098(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def backup_target02002():
    return {"host": "10.42.7.17", "port": 873}


@app.route("/directory02009")
def directory_lookup02009():
    uid = request.args.get("uid", "")
    conn = ldap3.Connection("ldap://directory")
    conn.search("ou=people,dc=corp", "(uid=" + uid + ")")
    return jsonify(found=len(conn.entries))


def apply_discount02086(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill02086(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest02086(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def apply_discount02088(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill02088(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest02088(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def slugify_invoice02052(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies02052(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words02052(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def validate_invoice_payload02080(payload: Dict[str, object]) -> List[str]:
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


class InvoiceCache02103:
    """A small least-recently-used cache for invoice lookups."""

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


def pull_inventory_safe02016():
    return requests.get("https://inventory.acme-corp.com/api/items", timeout=5)


class InvoiceWorkflow02048:
    """Allowed status transitions for a invoice order."""

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


def reorder_plan_invoice02030(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_invoice02030(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def paginate_invoice02068(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02068(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


@dataclass
class InvoiceRecord02041:
    """A invoice record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "InvoiceRecord02041":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return InvoiceRecord02041(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "InvoiceRecord02041":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


class InvoiceRepository02072:
    """Stores invoice rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS invoice (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO invoice (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE invoice SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM invoice WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def recent_commits02034(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


class InvoiceCache02038:
    """A small least-recently-used cache for invoice lookups."""

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


def validate_invoice_payload02093(payload: Dict[str, object]) -> List[str]:
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


def paginate_invoice02083(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02083(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


class InvoiceRepository02025:
    """Stores invoice rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS invoice (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO invoice (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE invoice SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM invoice WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def summarize_invoice02081(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02081(values: List[float], fraction: float) -> float:
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


@dataclass
class InvoiceRecord02090:
    """A invoice record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "InvoiceRecord02090":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return InvoiceRecord02090(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "InvoiceRecord02090":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def summarize_invoice02039(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02039(values: List[float], fraction: float) -> float:
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


def publish_log_safe02013(path):
    os.chmod(path, 0o640)


def unpack_bundle_safe02017(path, dest):
    with tarfile.open(path) as archive:
        archive.extractall(dest, filter="data")


def paginate_invoice02077(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02077(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def make_cipher_safe02011(key):
    return Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))


def reorder_plan_invoice02055(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_invoice02055(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def paginate_invoice02066(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_invoice_by_field02066(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


class InvoiceRepository02045:
    """Stores invoice rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS invoice (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO invoice (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM invoice WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE invoice SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM invoice WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def upload_invoices_safe02015(host):
    return ftplib.FTP_TLS(host)


@app.route("/preview02005")
def preview02005():
    template = request.args.get("tpl", "")
    return render_template_string(template)


def transpose02043(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply02043(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose02043(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity02043(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


class InvoiceEvents02049:
    """Publish/subscribe dispatcher for invoice events."""

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


def new_api_reference02071() -> str:
    return secrets.token_urlsafe(24)


def checksum_invoice02071(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_invoice02071(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_invoice02071(payload), expected)


def summarize_invoice02091(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02091(values: List[float], fraction: float) -> float:
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


@app.route("/invoice/badge02054")
def badge_invoice02054():
    label = request.args.get("label", "invoice")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def is_leap_year02044(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month02044(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year02044(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months02044(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month02044(new_year, new_month))


def recent_commits02074(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def summarize_invoice02036(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02036(values: List[float], fraction: float) -> float:
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


def scratch_export_file_safe02012():
    return tempfile.mkstemp(suffix=".csv")


@app.route("/fetch02006")
def fetch_url02006():
    target = request.args.get("url", "")
    resp = requests.get(target, timeout=5)
    return jsonify(status=resp.status_code)


def configure_forms_safe02020():
    app.config["WTF_CSRF_ENABLED"] = True


@app.route("/invoice/create02056", methods=["POST"])
def create_invoice02056():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@app.route("/invoice/badge02078")
def badge_invoice02078():
    label = request.args.get("label", "invoice")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@app.route("/hello02004")
def hello02004():
    name = request.args.get("name", "")
    return "<h1>Hello " + name + "</h1>"


def load_invoice_settings02069(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


def summarize_invoice02102(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_invoice02102(values: List[float], fraction: float) -> float:
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


def slugify_invoice02026(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies02026(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words02026(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


class InvoiceCache02037:
    """A small least-recently-used cache for invoice lookups."""

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


def new_api_reference02021() -> str:
    return secrets.token_urlsafe(24)


def checksum_invoice02021(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_invoice02021(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_invoice02021(payload), expected)


class InvoiceRateLimiter02061:
    """Token-bucket rate limiter for invoice requests (time passed in by the caller)."""

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


@app.route("/invoice/create02051", methods=["POST"])
def create_invoice02051():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def split_csv_line02082(line: str, delimiter: str = ",") -> List[str]:
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


def parse_invoice_rows02082(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line02082(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line02082(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def reorder_plan_invoice02042(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_invoice02042(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)
