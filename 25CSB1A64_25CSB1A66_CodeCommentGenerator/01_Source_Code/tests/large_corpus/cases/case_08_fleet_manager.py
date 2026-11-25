"""
Fleet Manager — Vehicle service module.

Generated test case 08 of the large-file corpus (tests/large_corpus). The code is
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


class VehicleRepository08065:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


class VehicleRepository08046:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def shortest_path08061(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


def billing_client_safe08018():
    api_key = os.environ.get("BILLING_API_KEY", "")
    return {"service": "billing", "auth": api_key}


def merge_sort08076(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08076(values[:middle])
    right = merge_sort08076(values[middle:])
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


def binary_search08076(values: List[int], target: int) -> int:
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


def is_leap_year08030(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08030(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08030(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08030(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08030(new_year, new_month))


@app.route("/plugin08005")
def load_plugin08005():
    module = importlib.import_module(request.args.get("name", "json"))
    return jsonify(module=module.__name__)


def is_leap_year08027(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08027(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08027(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08027(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08027(new_year, new_month))


@app.route("/lang08003")
def content_language08003():
    headers = Headers()
    headers.add_header("Content-Language", request.args.get("lang", "en"))
    return jsonify(headers=str(headers))


def build_vehicle_report08070(rows: List[Dict[str, object]], title: str) -> str:
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


def split_csv_line08059(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08059(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08059(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08059(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def transpose08080(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply08080(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose08080(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity08080(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def recent_commits08077(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def summarize_vehicle08044(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_vehicle08044(values: List[float], fraction: float) -> float:
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


class VehicleEvents08091:
    """Publish/subscribe dispatcher for vehicle events."""

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


def read_claims_safe08012(token, key):
    return jwt.decode(token, key, algorithms=["HS256"])


def apply_discount08093(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill08093(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest08093(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


class VehicleRateLimiter08024:
    """Token-bucket rate limiter for vehicle requests (time passed in by the caller)."""

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


def split_csv_line08048(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08048(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08048(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08048(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def transpose08037(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply08037(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose08037(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity08037(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def slugify_vehicle08089(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies08089(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words08089(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


@app.route("/remember08008")
def remember_user08008():
    session["user"] = request.args.get("user", "")
    return jsonify(ok=True)


def run_dev_server08009():
    app.run(debug=True)


def summarize_vehicle08079(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_vehicle08079(values: List[float], fraction: float) -> float:
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


class VehicleRepository08042:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def merge_sort08051(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08051(values[:middle])
    right = merge_sort08051(values[middle:])
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


def binary_search08051(values: List[int], target: int) -> int:
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


class VehicleCache08040:
    """A small least-recently-used cache for vehicle lookups."""

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


class VehicleCache08082:
    """A small least-recently-used cache for vehicle lookups."""

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


def reorder_plan_vehicle08031(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_vehicle08031(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@app.route("/orders_safe08020")
def find_orders_safe08020():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
    return jsonify(rows=rows)


class VehicleCache08087:
    """A small least-recently-used cache for vehicle lookups."""

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


class VehicleRepository08054:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def apply_discount08083(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill08083(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest08083(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def summarize_vehicle08026(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_vehicle08026(values: List[float], fraction: float) -> float:
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


def load_vehicle_settings08050(path: str, defaults: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


def reorder_plan_vehicle08033(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_vehicle08033(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


def slugify_vehicle08039(text: str, max_length: int = 60) -> str:
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:max_length].rstrip("-") or "item"


def word_frequencies08039(text: str, top: int = 10) -> List[tuple]:
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-zA-Z']+", text.lower()):
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:top]


def truncate_words08039(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + " ..."


def is_leap_year08073(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08073(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08073(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08073(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08073(new_year, new_month))


@app.route("/calc_safe08016")
def calculate_safe08016():
    expression = request.args.get("expr", "0")
    return jsonify(result=ast.literal_eval(expression))


def is_leap_year08092(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08092(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08092(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08092(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08092(new_year, new_month))


class VehicleCache08049:
    """A small least-recently-used cache for vehicle lookups."""

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


@app.route("/grep08004")
def grep_notes08004():
    pattern = request.args.get("q", "")
    matches = re.findall(pattern, "release notes for the current sprint")
    return jsonify(matches=len(matches))


@app.route("/ping_safe08017")
def ping_host_safe08017():
    host = request.args.get("host", "")
    subprocess.run(["ping", "-c", "1", host], check=False)
    return jsonify(status="sent")


class VehicleWorkflow08085:
    """Allowed status transitions for a vehicle order."""

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


class VehicleCache08057:
    """A small least-recently-used cache for vehicle lookups."""

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


def is_leap_year08035(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08035(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08035(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08035(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08035(new_year, new_month))


def split_csv_line08052(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08052(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08052(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08052(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


def merge_sort08078(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08078(values[:middle])
    right = merge_sort08078(values[middle:])
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


def binary_search08078(values: List[int], target: int) -> int:
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


class VehicleEvents08068:
    """Publish/subscribe dispatcher for vehicle events."""

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


class VehicleCache08058:
    """A small least-recently-used cache for vehicle lookups."""

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


def summarize_vehicle08086(values: Iterable[float]) -> Dict[str, float]:
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


def percentile_vehicle08086(values: List[float], fraction: float) -> float:
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


def shortest_path08047(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
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


def split_csv_line08025(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08025(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08025(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08025(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


@app.route("/account08001", methods=["POST"])
def account_lookup08001():
    query = request.get_json()
    account = mongo.bank.accounts.find_one(query)
    return jsonify(found=account is not None)


def fetch_daily_report08010():
    return requests.get("https://reports.acme-corp.com/daily", verify=False, timeout=10)


def reorder_plan_vehicle08075(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_vehicle08075(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


@dataclass
class VehicleRecord08036:
    """A vehicle record as stored by the service."""
    identifier: int
    name: str
    quantity: int = 0
    unit_price: float = 0.0
    labels: Optional[List[str]] = None

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def is_available(self) -> bool:
        return self.quantity > 0

    def with_quantity(self, quantity: int) -> "VehicleRecord08036":
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        return VehicleRecord08036(self.identifier, self.name, quantity, self.unit_price,
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
    def from_dict(cls, data: Dict[str, object]) -> "VehicleRecord08036":
        return cls(
            identifier=int(data["id"]),
            name=str(data["name"]).strip(),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0.0)),
            labels=[str(x) for x in data.get("labels") or []],
        )


class VehicleCache08055:
    """A small least-recently-used cache for vehicle lookups."""

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


def merge_sort08074(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08074(values[:middle])
    right = merge_sort08074(values[middle:])
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


def binary_search08074(values: List[int], target: int) -> int:
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


def transpose08043(matrix: List[List[float]]) -> List[List[float]]:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def multiply08043(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shapes do not match")
    columns = transpose08043(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity08043(size: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def recent_commits08072(repository: str, limit: int = 10) -> List[str]:
    count = max(1, min(int(limit), 100))
    completed = subprocess.run(
        ["git", "-C", repository, "log", "--oneline", "-n", str(count)],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        logger.warning("git log failed with exit code %d", completed.returncode)
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def paginate_vehicle08023(items: List[Dict[str, object]], page: int, per_page: int) -> Dict[str, object]:
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


def group_vehicle_by_field08023(items: Iterable[Dict[str, object]], field_name: str) -> Dict[str, List[Dict[str, object]]]:
    groups: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        groups.setdefault(key, []).append(item)
    return dict(sorted(groups.items()))


@app.route("/track08002")
def track_visit08002():
    page = request.args.get("page", "")
    logger.info("visited " + page)
    return jsonify(ok=True)


@app.route("/vehicle/badge08081")
def badge_vehicle08081():
    label = request.args.get("label", "vehicle")
    count = int(request.args.get("count", "0"))
    safe_label = html.escape(label)
    return f"<span class='badge'>{safe_label}: {count}</span>"


def split_csv_line08053(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08053(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08053(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08053(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


class VehicleRateLimiter08028:
    """Token-bucket rate limiter for vehicle requests (time passed in by the caller)."""

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


def apply_discount08041(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill08041(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest08041(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def build_vehicle_report08090(rows: List[Dict[str, object]], title: str) -> str:
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


def build_vehicle_report08022(rows: List[Dict[str, object]], title: str) -> str:
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


def open_ssh_safe08013(host):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host)
    return client


def build_vehicle_report08038(rows: List[Dict[str, object]], title: str) -> str:
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


def merge_sort08067(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08067(values[:middle])
    right = merge_sort08067(values[middle:])
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


def binary_search08067(values: List[int], target: int) -> int:
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


def split_csv_line08032(line: str, delimiter: str = ",") -> List[str]:
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


def parse_vehicle_rows08032(text: str) -> List[Dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = split_csv_line08032(lines[0])
    rows = []
    for line in lines[1:]:
        values = split_csv_line08032(line)
        rows.append({name: values[i] if i < len(values) else "" for i, name in enumerate(header)})
    return rows


@app.route("/vehicle/list08045")
def list_vehicle08045():
    page = int(request.args.get("page", "1"))
    per_page = min(int(request.args.get("per_page", "25")), 100)
    sort = request.args.get("sort", "name")
    if sort not in ("name", "quantity", "updated"):
        sort = "name"
    items = [{"id": i, "name": f"vehicle {i}", "quantity": i * 3} for i in range(1, 60)]
    items.sort(key=lambda item: item.get(sort, 0) if sort != "name" else str(item["name"]))
    return jsonify(paginate_vehicle08045(items, page, per_page) if "paginate_vehicle08045" in globals()
                   else {"items": items[(page - 1) * per_page:page * per_page]})


def merge_sort08056(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08056(values[:middle])
    right = merge_sort08056(values[middle:])
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


def binary_search08056(values: List[int], target: int) -> int:
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


def build_vehicle_report08064(rows: List[Dict[str, object]], title: str) -> str:
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


class VehicleEvents08021:
    """Publish/subscribe dispatcher for vehicle events."""

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


class VehicleEvents08066:
    """Publish/subscribe dispatcher for vehicle events."""

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


class Profile08007:
    name = ""

@app.route("/profile08007", methods=["POST"])
def update_profile08007():
    profile = Profile08007()
    for key in request.form:
        setattr(profile, key, request.form[key])
    return jsonify(ok=True)


def fingerprint08019(data):
    return hashlib.sha256(data.encode()).hexdigest()


def enable_cross_origin_safe08011():
    CORS(app, origins=["https://shop.acme-corp.com"])


def apply_discount08088(amount_cents: int, percent: float) -> int:
    if amount_cents < 0:
        raise ValueError("amount cannot be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(round(amount_cents * (100 - percent) / 100))


def split_bill08088(total_cents: int, people: int) -> List[int]:
    if people <= 0:
        raise ValueError("people must be positive")
    share, remainder = divmod(total_cents, people)
    return [share + (1 if i < remainder else 0) for i in range(people)]


def compound_interest08088(principal: float, rate: float, years: int, periods: int = 12) -> float:
    if periods <= 0:
        raise ValueError("periods must be positive")
    return round(principal * (1 + rate / periods) ** (periods * years), 2)


def merge_sort08034(values: List[int]) -> List[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort08034(values[:middle])
    right = merge_sort08034(values[middle:])
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


def binary_search08034(values: List[int], target: int) -> int:
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


class VehicleEvents08062:
    """Publish/subscribe dispatcher for vehicle events."""

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


def is_leap_year08071(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month08071(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")
    if month == 2:
        return 29 if is_leap_year08071(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def add_months08071(year: int, month: int, day: int, months: int) -> tuple:
    total = year * 12 + (month - 1) + months
    new_year, new_month = divmod(total, 12)
    new_month += 1
    return new_year, new_month, min(day, days_in_month08071(new_year, new_month))


def remove_lock_safe08014(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug("lock file already removed")


def audit_login_safe08015(username, password):
    logger.info("login attempt %s (password length %d)", username, len(password))


@app.route("/greet08006")
def greet08006():
    template = request.args.get("t", "")
    text = template.format(user=app)
    return jsonify(length=len(text))


class VehicleRepository08084:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


def reorder_plan_vehicle08069(stock: Dict[str, int], daily_use: Dict[str, float],
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


def days_of_cover_vehicle08069(on_hand: int, daily_use: float) -> float:
    if daily_use <= 0:
        return float("inf")
    return round(on_hand / daily_use, 1)


class VehicleRepository08029:
    """Stores vehicle rows in SQLite with parameterised statements only."""

    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS vehicle (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)"
        )

    def add(self, name: str, quantity: int) -> int:
        cursor = self.connection.execute(
            "INSERT INTO vehicle (name, quantity) VALUES (?, ?)", (name, quantity)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, row_id: int) -> Optional[Dict[str, object]]:
        row = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "quantity": row[2]}

    def search(self, prefix: str, limit: int = 20) -> List[Dict[str, object]]:
        rows = self.connection.execute(
            "SELECT id, name, quantity FROM vehicle WHERE name LIKE ? ORDER BY name LIMIT ?",
            (prefix + "%", limit),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]

    def adjust(self, row_id: int, delta: int) -> None:
        self.connection.execute(
            "UPDATE vehicle SET quantity = quantity + ? WHERE id = ?", (delta, row_id)
        )
        self.connection.commit()

    def delete(self, row_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM vehicle WHERE id = ?", (row_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()


class VehicleEvents08060:
    """Publish/subscribe dispatcher for vehicle events."""

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


class VehicleWorkflow08063:
    """Allowed status transitions for a vehicle order."""

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
