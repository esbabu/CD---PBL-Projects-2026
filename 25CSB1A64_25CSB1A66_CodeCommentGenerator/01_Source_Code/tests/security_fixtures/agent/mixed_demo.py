"""Demo for the Auto-fix agent: five fixable findings and one that needs a human."""
import hashlib
import os
import sqlite3

import requests
import yaml
from flask import Flask, jsonify, request
from lxml import etree

app = Flask(__name__)


@app.route("/user")
def find_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    return jsonify(conn.execute("SELECT id FROM users WHERE name = '" + name + "'").fetchall())


@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    os.system("ping -c 1 " + host)
    return "sent"


@app.route("/config", methods=["POST"])
def load_config():
    return jsonify(yaml.load(request.get_data()))


def password_digest(password):
    return hashlib.md5(password.encode()).hexdigest()


@app.route("/import", methods=["POST"])
def import_xml():
    parser = etree.XMLParser(resolve_entities=True)
    return jsonify(etree.fromstring(request.get_data(), parser).tag)


@app.route("/preview")
def preview():
    return jsonify(requests.get(request.args.get("url", ""), timeout=5).status_code)
