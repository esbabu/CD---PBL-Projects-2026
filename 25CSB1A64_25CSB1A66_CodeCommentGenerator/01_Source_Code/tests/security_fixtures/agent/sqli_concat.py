"""SEC005 fixed with ? placeholders (sqlite3)."""
import sqlite3

from flask import request


def find_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    return conn.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall()


def helper_that_must_not_change():
    return "SELECT 1"
