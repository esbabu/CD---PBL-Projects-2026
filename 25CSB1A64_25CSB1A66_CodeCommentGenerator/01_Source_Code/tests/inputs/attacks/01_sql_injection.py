"""Attack 1 - SQL injection: ?name=' OR '1'='1 dumps every user."""
import sqlite3
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


def lookup(conn, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return conn.execute(query).fetchall()


@app.route("/user")
def vulnerable_user():
    conn = sqlite3.connect("app.db")
    return escape(str(lookup(conn, request.args.get("name", ""))))


@app.route("/user_safe")
def safe_user():
    conn = sqlite3.connect("app.db")
    name = request.args.get("name", "")
    return escape(str(conn.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchall()))
