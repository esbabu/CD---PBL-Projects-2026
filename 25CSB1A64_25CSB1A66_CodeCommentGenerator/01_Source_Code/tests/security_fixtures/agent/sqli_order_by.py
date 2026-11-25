"""SEC005 where the value is a column name: no placeholder can fix it -> manual fix."""
import sqlite3

from flask import request


def list_users():
    column = request.args["sort"]
    conn = sqlite3.connect("app.db")
    return conn.execute("SELECT * FROM users ORDER BY " + column).fetchall()
