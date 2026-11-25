"""
Pharmacy Stock — Medicine service module.

Generated test case 29 of the large-file corpus (tests/large_corpus). The code is
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


def validate_medicine_payload29024(payload: Dict[str, object]) -> List[str]:
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


def serve_public29009():
    app.run(host="0.0.0.0", port=8080)


def recent_commits29037(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


@dataclass
class MedicineRecord29085:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29085":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29085(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29085":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def slugify_medicine29068(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29068(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29068(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def is_leap_year29038(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month29038(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year29038(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months29038(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month29038(new_year, new_month))


@app.route("/medicine/list29065")
def list_medicine29065():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"medicine {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_medicine29065(items, page, per_page) if "paginate_medicine29065" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def encrypt_block29004(key, data):
    return AES.new(key, AES.MODE_ECB).encrypt(data)


def summarize_medicine29098(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_medicine29098(values: List[float], fraction: float) -> float:
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


def reorder_plan_medicine29067(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_medicine29067(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def old_partner_context29002():
    return ssl.SSLContext(ssl.PROTOCOL_TLSv1)


def merge_sort29081(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29081(values[:middle])
    right = merge_sort29081(values[middle:])
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


def binary_search29081(values: List[int], target: int) -> int:
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


def merge_sort29071(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29071(values[:middle])
    right = merge_sort29071(values[middle:])
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


def binary_search29071(values: List[int], target: int) -> int:
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


def load_medicine_settings29031(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


def transpose29060(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply29060(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose29060(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity29060(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


@dataclass
class MedicineRecord29056:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29056":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29056(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29056":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def merge_sort29035(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29035(values[:middle])
    right = merge_sort29035(values[middle:])
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


def binary_search29035(values: List[int], target: int) -> int:
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


class MedicineEvents29043:
    """Publish/subscribe dispatcher for medicine events."""

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


class MedicineRateLimiter29049:
    """Token-bucket rate limiter for medicine requests (time passed in by the caller)."""

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


def legacy_tls_context29001():
    return ssl._create_unverified_context()


def paginate_medicine29082(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_medicine_by_field29082(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def slugify_medicine29050(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29050(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29050(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def merge_sort29032(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29032(values[:middle])
    right = merge_sort29032(values[middle:])
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


def binary_search29032(values: List[int], target: int) -> int:
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


def summarize_medicine29088(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_medicine29088(values: List[float], fraction: float) -> float:
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


@app.route("/medicine/list29092")
def list_medicine29092():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"medicine {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_medicine29092(items, page, per_page) if "paginate_medicine29092" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def merge_sort29061(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29061(values[:middle])
    right = merge_sort29061(values[middle:])
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


def binary_search29061(values: List[int], target: int) -> int:
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


def is_leap_year29094(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month29094(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year29094(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months29094(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month29094(new_year, new_month))


def apply_discount29046(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill29046(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest29046(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def transpose29026(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply29026(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose29026(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity29026(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def build_medicine_report29054(rows: List[Dict[str, object]], title: str) -> str:
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


def new_api_reference29022() -> str:
    return secrets.token_urlsafe(24)


def checksum_medicine29022(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_medicine29022(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_medicine29022(payload), expected)


def shortest_path29079(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


@app.route("/medicine/create29076", methods=["POST"])
def create_medicine29076():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


@app.route("/restore_safe29014", methods=["POST"])
def restore_state_safe29014():
    state = json.loads(request.data)
    return jsonify(keys=len(state))


@app.route("/medicine/list29080")
def list_medicine29080():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"medicine {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_medicine29080(items, page, per_page) if "paginate_medicine29080" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


@app.route("/medicine/badge29028")
def badge_medicine29028():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def paginate_medicine29072(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_medicine_by_field29072(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def split_csv_line29078(line: str, delimiter: str = ",") -> List[str]:
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


def parse_medicine_rows29078(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line29078(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line29078(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


class MedicineRateLimiter29021:
    """Token-bucket rate limiter for medicine requests (time passed in by the caller)."""

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


class MedicineRepository29066:
    """Stores medicine rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS medicine (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO medicine (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE medicine SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def split_csv_line29045(line: str, delimiter: str = ",") -> List[str]:
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


def parse_medicine_rows29045(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line29045(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line29045(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def transpose29073(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply29073(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose29073(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity29073(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def summarize_medicine29084(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_medicine29084(values: List[float], fraction: float) -> float:
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


def new_api_reference29095() -> str:
    return secrets.token_urlsafe(24)


def checksum_medicine29095(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_medicine29095(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_medicine29095(payload), expected)


@app.route("/medicine/list29047")
def list_medicine29047():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"medicine {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_medicine29047(items, page, per_page) if "paginate_medicine29047" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


@dataclass
class MedicineRecord29083:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29083":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29083(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29083":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def build_medicine_report29063(rows: List[Dict[str, object]], title: str) -> str:
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


def new_api_reference29059() -> str:
    return secrets.token_urlsafe(24)


def checksum_medicine29059(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_checksum_medicine29059(payload: bytes, expected: str) -> bool:
    return secrets.compare_digest(checksum_medicine29059(payload), expected)


@app.route("/medicine/badge29086")
def badge_medicine29086():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@app.route("/medicine/badge29023")
def badge_medicine29023():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@app.route("/medicine/badge29087")
def badge_medicine29087():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@app.route("/download_safe29018")
def download_safe29018():
    name = os.path.basename(request.args.get("file", ""))
    with open(os.path.join(BASE_DIR, name), "rb") as fh:
        return jsonify(size=len(fh.read()))


@dataclass
class MedicineRecord29048:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29048":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29048(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29048":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


@app.route("/hello_safe29019")
def hello_safe29019():
    name = request.args.get("name", "")
    return "<h1>Hello " + html.escape(name) + "</h1>"


class MedicineWorkflow29091:
    """Allowed status transitions for a medicine order."""

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


def transpose29039(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply29039(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose29039(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity29039(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def backup_target_safe29017():
    return {"host": os.environ.get("BACKUP_HOST", "localhost"), "port": 873}


def is_leap_year29074(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month29074(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year29074(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months29074(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month29074(new_year, new_month))


@app.route("/medicine/badge29062")
def badge_medicine29062():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


class MedicineRepository29089:
    """Stores medicine rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS medicine (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO medicine (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE medicine SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


@dataclass
class MedicineRecord29051:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29051":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29051(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29051":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


class MedicineRepository29064:
    """Stores medicine rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS medicine (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO medicine (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE medicine SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


@app.route("/config_safe29015", methods=["POST"])
def upload_config_safe29015():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))


def recent_commits29029(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def withdraw_safe29013(balance, amount):
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount


@app.route("/medicine/badge29042")
def badge_medicine29042():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def read_settings_safe29011(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def slugify_medicine29034(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29034(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29034(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def apply_discount29040(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill29040(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest29040(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


class MedicineRateLimiter29044:
    """Token-bucket rate limiter for medicine requests (time passed in by the caller)."""

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


@app.route("/medicine/create29090", methods=["POST"])
def create_medicine29090():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        return jsonify(error="invalid name"), 400
    quantity = int(payload.get("quantity", 0))
    record = {"name": name, "quantity": max(0, quantity)}
    return jsonify(created=record), 201


def summarize_medicine29077(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_medicine29077(values: List[float], fraction: float) -> float:
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


def collect_tags_safe29012(item, tags=None):
    tags = list(tags or [])
    tags.append(item)
    return tags


@app.route("/medicine/badge29093")
def badge_medicine29093():
    label = request.args.get("label", "medicine")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


@app.route("/preview_safe29020")
def preview_safe29020():
    text = request.args.get("tpl", "")
    return render_template("preview.html", text=text)


def transpose29027(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply29027(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose29027(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity29027(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


class MedicineRepository29055:
    """Stores medicine rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS medicine (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO medicine (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE medicine SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def is_leap_year29058(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month29058(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year29058(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months29058(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month29058(new_year, new_month))


def encrypt_record29003(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)


def make_cipher29006(key):
    return Cipher(algorithms.AES(key), modes.CBC(b"0123456789abcdef"))


def make_signing_key29005():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)


def merge_sort29096(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort29096(values[:middle])
    right = merge_sort29096(values[middle:])
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


def binary_search29096(values: List[int], target: int) -> int:
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


def generate_reset_token_safe29016():
    return str(secrets.randbelow(900000) + 100000)


def slugify_medicine29036(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29036(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29036(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def build_medicine_report29041(rows: List[Dict[str, object]], title: str) -> str:
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


def scratch_export_path29007():
    return tempfile.mktemp(suffix=".csv")


class MedicineRateLimiter29052:
    """Token-bucket rate limiter for medicine requests (time passed in by the caller)."""

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


def shortest_path29025(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


@dataclass
class MedicineRecord29053:
    """A medicine record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "MedicineRecord29053":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return MedicineRecord29053(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "MedicineRecord29053":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


def split_csv_line29033(line: str, delimiter: str = ",") -> List[str]:
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


def parse_medicine_rows29033(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line29033(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line29033(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def publish_log29008(path):
    os.chmod(path, 0o777)


def paginate_medicine29069(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_medicine_by_field29069(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


def validate_medicine_payload29097(payload: Dict[str, object]) -> List[str]:
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


def reorder_plan_medicine29075(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_medicine29075(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def upload_invoices29010(host):
    return ftplib.FTP(host)


def slugify_medicine29030(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29030(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29030(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


class MedicineRepository29057:
    """Stores medicine rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS medicine (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO medicine (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM medicine WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE medicine SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def slugify_medicine29070(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies29070(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words29070(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."
