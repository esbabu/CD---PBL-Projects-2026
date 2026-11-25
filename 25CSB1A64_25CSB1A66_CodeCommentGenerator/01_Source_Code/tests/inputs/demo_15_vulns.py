"""Demo web service with 15 different kinds of security vulnerability (one per function).

Every function is deliberately vulnerable. Do not run this code.
"""
import hashlib
import os
import pickle
import random
import sqlite3
import xml.dom.minidom
import xml.sax
import xml.sax.handler

import requests
import yaml
from flask import Flask, jsonify, make_response, redirect, render_template_string, request

app = Flask(__name__)

# 1. Hard-coded secret (CWE-798)
STRIPE_API_KEY = "REDACTED_STRIPE_TEST_KEY"


# 2. Code injection (CWE-95)
@app.route("/calc")
def calculator():
    expression = request.args.get("expr", "1+1")
    return jsonify(result=eval(expression))


# 3. OS command injection (CWE-78)
@app.route("/ping")
def ping_host():
    host = request.args.get("host", "localhost")
    os.system("ping -c 1 " + host)
    return jsonify(status="sent")


# 4. Weak password hash (CWE-328)
def store_password(username, password):
    digest = hashlib.md5(password.encode()).hexdigest()
    return {"user": username, "password_hash": digest}


# 5. SQL injection (CWE-89)
@app.route("/user")
def find_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    rows = conn.execute("SELECT id, email FROM users WHERE name = '" + name + "'").fetchall()
    return jsonify(rows)


# 6. Bare except hides every error, including KeyboardInterrupt (CWE-396)
def read_config(path):
    try:
        with open(path) as fh:
            return fh.read()
    except:
        return ""


# 7. Insecure deserialization (CWE-502)
@app.route("/session", methods=["POST"])
def load_session():
    session = pickle.loads(request.get_data())
    return jsonify(user=session.get("user"))


# 8. Unsafe YAML load (CWE-502)
@app.route("/import-settings", methods=["POST"])
def import_settings():
    settings = yaml.load(request.get_data())
    return jsonify(settings)


# 9. Predictable password-reset token (CWE-338)
def generate_reset_token():
    token = "".join(random.choice("abcdef0123456789") for _ in range(32))
    return token


# 10. Path traversal (CWE-22)
@app.route("/download")
def download_report():
    filename = request.args.get("file", "report.txt")
    with open(os.path.join("/srv/reports", filename)) as fh:
        return jsonify(content=fh.read())


# 11. Reflected cross-site scripting (CWE-79)
@app.route("/greet")
def greet():
    name = request.args.get("name", "guest")
    return make_response("<h1>Hello " + name + "</h1>")


# 12. Server-side template injection (CWE-1336)
@app.route("/preview")
def preview_template():
    template = request.args.get("tpl", "Hello")
    return render_template_string(template)


# 13. Server-side request forgery (CWE-918)
@app.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    return jsonify(status=requests.get(url, timeout=5).status_code)


# 14. Open redirect (CWE-601)
@app.route("/login")
def login_redirect():
    return redirect(request.args.get("next", "/"))


# 15. XML external entity processing (CWE-611)
@app.route("/upload-xml", methods=["POST"])
def upload_xml():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_external_ges, True)
    doc = xml.dom.minidom.parseString(request.get_data(), parser)
    return jsonify(root=doc.documentElement.tagName)
