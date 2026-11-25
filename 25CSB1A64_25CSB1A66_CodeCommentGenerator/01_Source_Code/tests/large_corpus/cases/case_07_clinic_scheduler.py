"""
Clinic Scheduler — Appointment service module.

Generated test case 07 of the large-file corpus (tests/large_corpus). The code is
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


@dataclass
class AppointmentRecord07080:
    """A appointment record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "AppointmentRecord07080":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return AppointmentRecord07080(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "AppointmentRecord07080":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


@app.route("/fetch07006")
def fetch_url07006():
    target = request.args.get("url", "")
    resp = requests.get(target, timeout=5)
    return jsonify(status=resp.status_code)


def configure_forms_safe07020():
    app.config["WTF_CSRF_ENABLED"] = True


def slugify_appointment07073(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies07073(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words07073(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def split_csv_line07046(line: str, delimiter: str = ",") -> List[str]:
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


def parse_appointment_rows07046(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line07046(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line07046(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


class AppointmentCache07027:
    """A small least-recently-used cache for appointment lookups."""

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


@app.route("/appointment/list07042")
def list_appointment07042():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"appointment {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_appointment07042(items, page, per_page) if "paginate_appointment07042" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


class AppointmentWorkflow07055:
    """Allowed status transitions for a appointment order."""

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


def summarize_appointment07039(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07039(values: List[float], fraction: float) -> float:
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


def recent_commits07053(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def paginate_appointment07045(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_appointment_by_field07045(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


@app.route("/download07003")
def download07003():
    name = request.args.get("file", "")
    with open(os.path.join(BASE_DIR, name), "rb") as fh:
        return jsonify(size=len(fh.read()))


class AppointmentWorkflow07036:
    """Allowed status transitions for a appointment order."""

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


def split_csv_line07068(line: str, delimiter: str = ",") -> List[str]:
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


def parse_appointment_rows07068(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line07068(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line07068(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def make_cipher_safe07011(key):
    return Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))


class AppointmentWorkflow07054:
    """Allowed status transitions for a appointment order."""

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


def summarize_appointment07049(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07049(values: List[float], fraction: float) -> float:
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


class AppointmentRateLimiter07044:
    """Token-bucket rate limiter for appointment requests (time passed in by the caller)."""

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


class AppointmentCache07043:
    """A small least-recently-used cache for appointment lookups."""

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


def load_appointment_settings07075(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


class AppointmentWorkflow07071:
    """Allowed status transitions for a appointment order."""

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


def pull_inventory_safe07016():
    return requests.get("https://inventory.acme-corp.com/api/items", timeout=5)


def validate_appointment_payload07085(payload: Dict[str, object]) -> List[str]:
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


def reorder_plan_appointment07066(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_appointment07066(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def reorder_plan_appointment07060(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_appointment07060(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@app.route("/staff07010")
def staff_record07010():
    eid = request.args.get("id", "")
    tree = lxml.etree.parse(os.path.join(BASE_DIR, "staff.xml"))
    nodes = tree.xpath("//employee[@id='" + eid + "']")
    return jsonify(count=len(nodes))


@app.route("/appointment/create07052", methods=["POST"])
def create_appointment07052():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@dataclass
class AppointmentRecord07058:
    """A appointment record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "AppointmentRecord07058":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return AppointmentRecord07058(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "AppointmentRecord07058":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


class AppointmentCache07063:
    """A small least-recently-used cache for appointment lookups."""

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


class AppointmentRateLimiter07025:
    """Token-bucket rate limiter for appointment requests (time passed in by the caller)."""

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


@app.route("/appointment/list07079")
def list_appointment07079():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"appointment {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_appointment07079(items, page, per_page) if "paginate_appointment07079" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def apply_discount07082(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill07082(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest07082(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


class AppointmentEvents07083:
    """Publish/subscribe dispatcher for appointment events."""

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


def scratch_export_file_safe07012():
    return tempfile.mkstemp(suffix=".csv")


def new_api_reference07084() -> str:
    return secrets.token_urlsafe(24)


def checksum_appointment07084(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_appointment07084(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_appointment07084(payload), expected)


class AppointmentEvents07069:
    """Publish/subscribe dispatcher for appointment events."""

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


def validate_appointment_payload07022(payload: Dict[str, object]) -> List[str]:
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


def unpack_bundle_safe07017(path, dest):
    with tarfile.open(path) as archive:
        archive.extractall(dest, filter="data")


def recent_commits07077(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def report_environment_safe07018():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                              autoescape=jinja2.select_autoescape())


@dataclass
class AppointmentRecord07064:
    """A appointment record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "AppointmentRecord07064":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return AppointmentRecord07064(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "AppointmentRecord07064":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def build_appointment_report07059(rows: List[Dict[str, object]], title: str) -> str:
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


def backup_target07002():
    return {"host": "10.42.7.52", "port": 873}


def load_appointment_settings07070(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


def summarize_appointment07074(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07074(values: List[float], fraction: float) -> float:
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


def summarize_appointment07065(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07065(values: List[float], fraction: float) -> float:
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


def slugify_appointment07076(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies07076(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words07076(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


@app.route("/preview07005")
def preview07005():
    template = request.args.get("tpl", "")
    return render_template_string(template)


def summarize_appointment07040(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07040(values: List[float], fraction: float) -> float:
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


def new_api_reference07038() -> str:
    return secrets.token_urlsafe(24)


def checksum_appointment07038(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_appointment07038(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_appointment07038(payload), expected)


def serve_local_safe07014():
    app.run(host="127.0.0.1", port=8080)


class AppointmentCache07056:
    """A small least-recently-used cache for appointment lookups."""

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


def new_api_reference07021() -> str:
    return secrets.token_urlsafe(24)


def checksum_appointment07021(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_appointment07021(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_appointment07021(payload), expected)


def apply_discount07086(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill07086(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest07086(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def build_appointment_report07061(rows: List[Dict[str, object]], title: str) -> str:
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


@app.route("/appointment/create07057", methods=["POST"])
def create_appointment07057():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@app.route("/appointment/create07030", methods=["POST"])
def create_appointment07030():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@app.route("/import07008", methods=["POST"])
def import_xml07008():
    parser = lxml.etree.XMLParser(resolve_entities=True)
    doc = lxml.etree.fromstring(request.data, parser)
    return jsonify(tag=doc.tag)


def reorder_plan_appointment07035(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_appointment07035(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@app.route("/hello07004")
def hello07004():
    name = request.args.get("name", "")
    return "<h1>Hello " + name + "</h1>"


class AppointmentRateLimiter07051:
    """Token-bucket rate limiter for appointment requests (time passed in by the caller)."""

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


def shortest_path07024(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


def paginate_appointment07062(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_appointment_by_field07062(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def transpose07032(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply07032(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose07032(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity07032(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


@app.route("/appointment/badge07081")
def badge_appointment07081():
    label = request.args.get("label", "appointment")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def validate_appointment_payload07078(payload: Dict[str, object]) -> List[str]:
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


def summarize_appointment07029(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07029(values: List[float], fraction: float) -> float:
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


@app.route("/continue07007")
def continue_to07007():
    target = request.args.get("next", "/")
    return redirect(target)


class AppointmentEvents07034:
    """Publish/subscribe dispatcher for appointment events."""

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


def publish_log_safe07013(path):
    os.chmod(path, 0o640)


def shortest_path07037(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


def recent_commits07072(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


@app.route("/appointment/badge07028")
def badge_appointment07028():
    label = request.args.get("label", "appointment")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def slugify_appointment07050(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies07050(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words07050(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def summarize_appointment07033(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_appointment07033(values: List[float], fraction: float) -> float:
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


@app.route("/prefs_safe07019")
def save_prefs_safe07019():
    resp = make_response("saved")
    resp.set_cookie("theme", "dark", secure=True, httponly=True, samesite="Lax")
    return resp


class AppointmentEvents07067:
    """Publish/subscribe dispatcher for appointment events."""

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


class AppointmentWorkflow07023:
    """Allowed status transitions for a appointment order."""

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


def generate_reset_token07001():
    return str(random.randint(100000, 999999))


@app.route("/appointment/create07048", methods=["POST"])
def create_appointment07048():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def recent_commits07041(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def is_leap_year07047(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month07047(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year07047(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months07047(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month07047(new_year, new_month))


@app.route("/directory07009")
def directory_lookup07009():
    uid = request.args.get("uid", "")
    conn = ldap3.Connection("ldap://directory")
    conn.search("ou=people,dc=corp", "(uid=" + uid + ")")
    return jsonify(found=len(conn.entries))


@app.route("/appointment/list07031")
def list_appointment07031():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"appointment {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_appointment07031(items, page, per_page) if "paginate_appointment07031" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def upload_invoices_safe07015(host):
    return ftplib.FTP_TLS(host)


def validate_appointment_payload07026(payload: Dict[str, object]) -> List[str]:
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
