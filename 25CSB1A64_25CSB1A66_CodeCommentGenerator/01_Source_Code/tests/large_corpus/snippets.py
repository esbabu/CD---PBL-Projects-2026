"""
Snippet library for the large test corpus
==========================================
For every rule SEC001-SEC050 there is one VULNERABLE snippet and one SAFE twin
(the fix the rule's remediation text recommends).

Ground truth is written by hand here: the line of each vulnerable snippet that
the rule must report ends with the marker ``#!``. The generator strips the
marker and records the line in ``manifest.json``. Safe twins carry no marker
and must produce no finding at all. ``__N__`` is replaced by a unique number so
that every snippet defines its own names.
"""

HEADER = '''"""
__TITLE__

Generated test case __CASE__ of the large-file corpus (tests/large_corpus). The code is
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
'''

VULN = {
    "SEC001": '''
@app.route("/calc__N__")
def calculate__N__():
    expression = request.args.get("expr", "")
    result = eval(expression)  #!
    return jsonify(result=result)
''',
    "SEC002": '''
@app.route("/ping__N__")
def ping_host__N__():
    host = request.args.get("host", "")
    os.system("ping -c 1 " + host)  #!
    return jsonify(status="sent")
''',
    "SEC003": '''
def billing_client__N__():
    api_key = "q9X2vLm4Rt8Zp1Kw__N__"  #!
    return {"service": "billing", "auth": api_key}
''',
    "SEC004": '''
def hash_password__N__(password):
    return hashlib.md5(password.encode()).hexdigest()  #!
''',
    "SEC005": '''
@app.route("/orders__N__")
def find_orders__N__():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = '" + customer + "'").fetchall()  #!
    return jsonify(rows=rows)
''',
    "SEC006": '''
def read_settings__N__(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except:  #!
        return {}
''',
    "SEC007": '''
def collect_tags__N__(item, tags=[]):  #!
    tags.append(item)
    return tags
''',
    "SEC008": '''
def withdraw__N__(balance, amount):
    assert amount <= balance, "insufficient funds"  #!
    return balance - amount
''',
    "SEC009": '''
@app.route("/restore__N__", methods=["POST"])
def restore_state__N__():
    state = pickle.loads(request.data)  #!
    return jsonify(keys=len(state))
''',
    "SEC010": '''
@app.route("/config__N__", methods=["POST"])
def upload_config__N__():
    config = yaml.load(request.data, Loader=yaml.Loader)  #!
    return jsonify(sections=len(config))
''',
    "SEC011": '''
def generate_reset_token__N__():
    return str(random.randint(100000, 999999))  #!
''',
    "SEC012": '''
def backup_target__N__():
    return {"host": "10.42.7.__M__", "port": 873}  #!
''',
    "SEC013": '''
@app.route("/download__N__")
def download__N__():
    name = request.args.get("file", "")
    with open(os.path.join(BASE_DIR, name), "rb") as fh:  #!
        return jsonify(size=len(fh.read()))
''',
    "SEC014": '''
@app.route("/hello__N__")
def hello__N__():
    name = request.args.get("name", "")
    return "<h1>Hello " + name + "</h1>"  #!
''',
    "SEC015": '''
@app.route("/preview__N__")
def preview__N__():
    template = request.args.get("tpl", "")
    return render_template_string(template)  #!
''',
    "SEC016": '''
@app.route("/fetch__N__")
def fetch_url__N__():
    target = request.args.get("url", "")
    resp = requests.get(target, timeout=5)  #!
    return jsonify(status=resp.status_code)
''',
    "SEC017": '''
@app.route("/continue__N__")
def continue_to__N__():
    target = request.args.get("next", "/")
    return redirect(target)  #!
''',
    "SEC018": '''
@app.route("/import__N__", methods=["POST"])
def import_xml__N__():
    parser = lxml.etree.XMLParser(resolve_entities=True)
    doc = lxml.etree.fromstring(request.data, parser)  #!
    return jsonify(tag=doc.tag)
''',
    "SEC019": '''
@app.route("/directory__N__")
def directory_lookup__N__():
    uid = request.args.get("uid", "")
    conn = ldap3.Connection("ldap://directory")
    conn.search("ou=people,dc=corp", "(uid=" + uid + ")")  #!
    return jsonify(found=len(conn.entries))
''',
    "SEC020": '''
@app.route("/staff__N__")
def staff_record__N__():
    eid = request.args.get("id", "")
    tree = lxml.etree.parse(os.path.join(BASE_DIR, "staff.xml"))
    nodes = tree.xpath("//employee[@id='" + eid + "']")  #!
    return jsonify(count=len(nodes))
''',
    "SEC021": '''
@app.route("/account__N__", methods=["POST"])
def account_lookup__N__():
    query = request.get_json()
    account = mongo.bank.accounts.find_one(query)  #!
    return jsonify(found=account is not None)
''',
    "SEC022": '''
@app.route("/track__N__")
def track_visit__N__():
    page = request.args.get("page", "")
    logger.info("visited " + page)  #!
    return jsonify(ok=True)
''',
    "SEC023": '''
@app.route("/lang__N__")
def content_language__N__():
    headers = Headers()
    headers.add_header("Content-Language", request.args.get("lang", "en"))  #!
    return jsonify(headers=str(headers))
''',
    "SEC024": '''
@app.route("/grep__N__")
def grep_notes__N__():
    pattern = request.args.get("q", "")
    matches = re.findall(pattern, "release notes for the current sprint")  #!
    return jsonify(matches=len(matches))
''',
    "SEC025": '''
@app.route("/plugin__N__")
def load_plugin__N__():
    module = importlib.import_module(request.args.get("name", "json"))  #!
    return jsonify(module=module.__name__)
''',
    "SEC026": '''
@app.route("/greet__N__")
def greet__N__():
    template = request.args.get("t", "")
    text = template.format(user=app)  #!
    return jsonify(length=len(text))
''',
    "SEC027": '''
class Profile__N__:
    name = ""

@app.route("/profile__N__", methods=["POST"])
def update_profile__N__():
    profile = Profile__N__()
    for key in request.form:
        setattr(profile, key, request.form[key])  #!
    return jsonify(ok=True)
''',
    "SEC028": '''
@app.route("/remember__N__")
def remember_user__N__():
    session["user"] = request.args.get("user", "")  #!
    return jsonify(ok=True)
''',
    "SEC029": '''
def run_dev_server__N__():
    app.run(debug=True)  #!
''',
    "SEC030": '''
def fetch_daily_report__N__():
    return requests.get("https://reports.acme-corp.com/daily", verify=False, timeout=10)  #!
''',
    "SEC031": '''
def legacy_tls_context__N__():
    return ssl._create_unverified_context()  #!
''',
    "SEC032": '''
def old_partner_context__N__():
    return ssl.SSLContext(ssl.PROTOCOL_TLSv1)  #!
''',
    "SEC033": '''
def encrypt_record__N__(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)  #!
''',
    "SEC034": '''
def encrypt_block__N__(key, data):
    return AES.new(key, AES.MODE_ECB).encrypt(data)  #!
''',
    "SEC035": '''
def make_signing_key__N__():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)  #!
''',
    "SEC036": '''
def make_cipher__N__(key):
    return Cipher(algorithms.AES(key), modes.CBC(b"0123456789abcdef"))  #!
''',
    "SEC037": '''
def scratch_export_path__N__():
    return tempfile.mktemp(suffix=".csv")  #!
''',
    "SEC038": '''
def publish_log__N__(path):
    os.chmod(path, 0o777)  #!
''',
    "SEC039": '''
def serve_public__N__():
    app.run(host="0.0.0.0", port=8080)  #!
''',
    "SEC040": '''
def upload_invoices__N__(host):
    return ftplib.FTP(host)  #!
''',
    "SEC041": '''
def pull_inventory__N__():
    return requests.get("http://inventory.acme-corp.com/api/items", timeout=5)  #!
''',
    "SEC042": '''
def unpack_bundle__N__(path, dest):
    with tarfile.open(path) as tar:
        tar.extractall(dest)  #!
''',
    "SEC043": '''
def report_environment__N__():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))  #!
''',
    "SEC044": '''
@app.route("/prefs__N__")
def save_prefs__N__():
    resp = make_response("saved")
    resp.set_cookie("theme", "dark", secure=False, httponly=True)  #!
    return resp
''',
    "SEC045": '''
def configure_forms__N__():
    app.config["WTF_CSRF_ENABLED"] = False  #!
''',
    "SEC046": '''
def enable_cross_origin__N__():
    CORS(app)  #!
''',
    "SEC047": '''
def read_claims__N__(token):
    return jwt.decode(token, options={"verify_signature": False})  #!
''',
    "SEC048": '''
def open_ssh__N__(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  #!
    client.connect(host)
    return client
''',
    "SEC049": '''
def remove_lock__N__(path):
    try:
        os.remove(path)
    except FileNotFoundError:  #!
        pass
''',
    "SEC050": '''
def audit_login__N__(username, password):
    logger.info("login attempt %s %s", username, password)  #!
''',
}

SAFE = {
    "SEC001": '''
@app.route("/calc_safe__N__")
def calculate_safe__N__():
    expression = request.args.get("expr", "0")
    return jsonify(result=ast.literal_eval(expression))
''',
    "SEC002": '''
@app.route("/ping_safe__N__")
def ping_host_safe__N__():
    host = request.args.get("host", "")
    subprocess.run(["ping", "-c", "1", host], check=False)
    return jsonify(status="sent")
''',
    "SEC003": '''
def billing_client_safe__N__():
    api_key = os.environ.get("BILLING_API_KEY", "")
    return {"service": "billing", "auth": api_key}
''',
    "SEC004": '''
def fingerprint__N__(data):
    return hashlib.sha256(data.encode()).hexdigest()
''',
    "SEC005": '''
@app.route("/orders_safe__N__")
def find_orders_safe__N__():
    customer = request.args.get("customer", "")
    conn = sqlite3.connect("shop.db")
    rows = conn.execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
    return jsonify(rows=rows)
''',
    "SEC006": '''
def read_settings_safe__N__(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}
''',
    "SEC007": '''
def collect_tags_safe__N__(item, tags=None):
    tags = list(tags or [])
    tags.append(item)
    return tags
''',
    "SEC008": '''
def withdraw_safe__N__(balance, amount):
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
''',
    "SEC009": '''
@app.route("/restore_safe__N__", methods=["POST"])
def restore_state_safe__N__():
    state = json.loads(request.data)
    return jsonify(keys=len(state))
''',
    "SEC010": '''
@app.route("/config_safe__N__", methods=["POST"])
def upload_config_safe__N__():
    config = yaml.safe_load(request.data)
    return jsonify(sections=len(config))
''',
    "SEC011": '''
def generate_reset_token_safe__N__():
    return str(secrets.randbelow(900000) + 100000)
''',
    "SEC012": '''
def backup_target_safe__N__():
    return {"host": os.environ.get("BACKUP_HOST", "localhost"), "port": 873}
''',
    "SEC013": '''
@app.route("/download_safe__N__")
def download_safe__N__():
    name = os.path.basename(request.args.get("file", ""))
    with open(os.path.join(BASE_DIR, name), "rb") as fh:
        return jsonify(size=len(fh.read()))
''',
    "SEC014": '''
@app.route("/hello_safe__N__")
def hello_safe__N__():
    name = request.args.get("name", "")
    return "<h1>Hello " + html.escape(name) + "</h1>"
''',
    "SEC015": '''
@app.route("/preview_safe__N__")
def preview_safe__N__():
    text = request.args.get("tpl", "")
    return render_template("preview.html", text=text)
''',
    "SEC016": '''
@app.route("/fetch_safe__N__")
def fetch_item_safe__N__():
    item = request.args.get("item", "")
    resp = requests.get("https://api.acme-corp.com/items/" + item, timeout=5)
    return jsonify(status=resp.status_code)
''',
    "SEC017": '''
@app.route("/continue_safe__N__")
def continue_safe__N__():
    return redirect(url_for("index"))
''',
    "SEC018": '''
@app.route("/import_safe__N__", methods=["POST"])
def import_xml_safe__N__():
    doc = lxml.etree.fromstring(request.data)
    return jsonify(tag=doc.tag)
''',
    "SEC019": '''
@app.route("/directory_safe__N__")
def directory_lookup_safe__N__():
    uid = escape_filter_chars(request.args.get("uid", ""))
    conn = ldap3.Connection("ldap://directory")
    conn.search("ou=people,dc=corp", "(uid=" + uid + ")")
    return jsonify(found=len(conn.entries))
''',
    "SEC020": '''
@app.route("/staff_safe__N__")
def staff_record_safe__N__():
    eid = request.args.get("id", "")
    tree = lxml.etree.parse(os.path.join(BASE_DIR, "staff.xml"))
    nodes = tree.xpath("//employee[@id=$eid]", eid=eid)
    return jsonify(count=len(nodes))
''',
    "SEC021": '''
@app.route("/account_safe__N__", methods=["POST"])
def account_lookup_safe__N__():
    number = int(request.get_json()["number"])
    account = mongo.bank.accounts.find_one({"number": number})
    return jsonify(found=account is not None)
''',
    "SEC022": '''
@app.route("/track_safe__N__")
def track_visit_safe__N__():
    page = request.args.get("page", "")
    if not page.isalnum():
        return jsonify(ok=False)
    logger.info("visited " + page)
    return jsonify(ok=True)
''',
    "SEC023": '''
@app.route("/lang_safe__N__")
def content_language_safe__N__():
    lang = request.args.get("lang", "en")
    headers = Headers()
    headers.add_header("Content-Language", lang if lang.isalpha() else "en")
    return jsonify(headers=str(headers))
''',
    "SEC024": '''
@app.route("/grep_safe__N__")
def grep_notes_safe__N__():
    pattern = re.escape(request.args.get("q", ""))
    matches = re.findall(pattern, "release notes for the current sprint")
    return jsonify(matches=len(matches))
''',
    "SEC025": '''
EXPORTERS__N__ = {"json": "json", "csv": "csv"}

@app.route("/plugin_safe__N__")
def load_plugin_safe__N__():
    module = importlib.import_module(EXPORTERS__N__["json"])
    return jsonify(module=module.__name__)
''',
    "SEC026": '''
@app.route("/greet_safe__N__")
def greet_safe__N__():
    name = request.args.get("t", "")
    text = "Hello {}".format(name)
    return jsonify(length=len(text))
''',
    "SEC027": '''
class ProfileSafe__N__:
    name = ""

@app.route("/profile_safe__N__", methods=["POST"])
def update_profile_safe__N__():
    profile = ProfileSafe__N__()
    for key in ("name", "email"):
        setattr(profile, key, request.form.get(key, ""))
    return jsonify(ok=True)
''',
    "SEC028": '''
@app.route("/remember_safe__N__")
def remember_user_safe__N__():
    session["visits"] = int(request.args.get("n", "0"))
    return jsonify(ok=True)
''',
    "SEC029": '''
def run_server_safe__N__():
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
''',
    "SEC030": '''
def fetch_daily_report_safe__N__():
    return requests.get("https://reports.acme-corp.com/daily", verify="/etc/ssl/corp-ca.pem", timeout=10)
''',
    "SEC031": '''
def tls_context_safe__N__():
    return ssl.create_default_context()
''',
    "SEC032": '''
def partner_context_safe__N__():
    return ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
''',
    "SEC033": '''
def encrypt_record_safe__N__(key, data):
    return AES.new(key, AES.MODE_GCM).encrypt(data)
''',
    "SEC034": '''
def encrypt_block_safe__N__(key, data):
    return AES.new(key, AES.MODE_GCM).encrypt(data)
''',
    "SEC035": '''
def make_signing_key_safe__N__():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)
''',
    "SEC036": '''
def make_cipher_safe__N__(key):
    return Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))
''',
    "SEC037": '''
def scratch_export_file_safe__N__():
    return tempfile.mkstemp(suffix=".csv")
''',
    "SEC038": '''
def publish_log_safe__N__(path):
    os.chmod(path, 0o640)
''',
    "SEC039": '''
def serve_local_safe__N__():
    app.run(host="127.0.0.1", port=8080)
''',
    "SEC040": '''
def upload_invoices_safe__N__(host):
    return ftplib.FTP_TLS(host)
''',
    "SEC041": '''
def pull_inventory_safe__N__():
    return requests.get("https://inventory.acme-corp.com/api/items", timeout=5)
''',
    "SEC042": '''
def unpack_bundle_safe__N__(path, dest):
    with tarfile.open(path) as archive:
        archive.extractall(dest, filter="data")
''',
    "SEC043": '''
def report_environment_safe__N__():
    return jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                              autoescape=jinja2.select_autoescape())
''',
    "SEC044": '''
@app.route("/prefs_safe__N__")
def save_prefs_safe__N__():
    resp = make_response("saved")
    resp.set_cookie("theme", "dark", secure=True, httponly=True, samesite="Lax")
    return resp
''',
    "SEC045": '''
def configure_forms_safe__N__():
    app.config["WTF_CSRF_ENABLED"] = True
''',
    "SEC046": '''
def enable_cross_origin_safe__N__():
    CORS(app, origins=["https://shop.acme-corp.com"])
''',
    "SEC047": '''
def read_claims_safe__N__(token, key):
    return jwt.decode(token, key, algorithms=["HS256"])
''',
    "SEC048": '''
def open_ssh_safe__N__(host):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host)
    return client
''',
    "SEC049": '''
def remove_lock_safe__N__(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug("lock file already removed")
''',
    "SEC050": '''
def audit_login_safe__N__(username, password):
    logger.info("login attempt %s (password length %d)", username, len(password))
''',
}
