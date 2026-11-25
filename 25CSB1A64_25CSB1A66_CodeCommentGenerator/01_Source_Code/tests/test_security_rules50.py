"""Rules SEC019-SEC050: each rule has a vulnerable snippet it must report and a safe
counterpart (the fix recommended in the rule's remediation text) it must not report.
Expected results come from the snippets as written here, not from analyzer output."""
import textwrap

import pytest

from src.security.analyzer import analyze_source
from src.security.rules import RULES

FLASK = "from flask import Flask, request, session, make_response\napp = Flask(__name__)\n"

CASES = {
    # ── taint rules ──────────────────────────────────────────────────────
    "SEC019": (FLASK + """
import ldap3
@app.route("/u")
def find_user():
    uid = request.args.get("uid")
    conn = ldap3.Connection("ldap://dir")
    conn.search("ou=people", f"(uid={uid})")
""", FLASK + """
import ldap3
from ldap3.utils.conv import escape_filter_chars
@app.route("/u")
def find_user():
    uid = escape_filter_chars(request.args.get("uid"))
    conn = ldap3.Connection("ldap://dir")
    conn.search("ou=people", f"(uid={uid})")
"""),
    "SEC020": (FLASK + """
import lxml.etree
@app.route("/e")
def employee():
    eid = request.args.get("id")
    tree = lxml.etree.parse("staff.xml")
    return str(tree.xpath(f"//employee[@id='{eid}']"))
""", FLASK + """
import lxml.etree
@app.route("/e")
def employee():
    eid = request.args.get("id")
    tree = lxml.etree.parse("staff.xml")
    return str(tree.xpath("//employee[@id=$eid]", eid=eid))
"""),
    "SEC021": (FLASK + """
from pymongo import MongoClient
db = MongoClient().shop
@app.route("/login", methods=["POST"])
def login():
    user = db.users.find_one({"name": request.json["name"], "pw": request.json["pw"]})
    return "ok" if user else "no"
""", FLASK + """
from pymongo import MongoClient
db = MongoClient().shop
@app.route("/login", methods=["POST"])
def login():
    name = int(request.json["id"])
    user = db.users.find_one({"uid": name})
    return "ok" if user else "no"
"""),
    "SEC022": (FLASK + """
import logging
@app.route("/l")
def track():
    page = request.args.get("page")
    logging.info("visited " + page)
    return "ok"
""", FLASK + """
import logging
@app.route("/l")
def track():
    page = request.args.get("page")
    if not page.isalnum():
        return "bad"
    logging.info("visited " + page)
    return "ok"
"""),
    "SEC023": (FLASK + """
from wsgiref.headers import Headers
@app.route("/h")
def lang():
    h = Headers()
    h.add_header("Content-Language", request.args.get("lang"))
    return str(h)
""", FLASK + """
from wsgiref.headers import Headers
import urllib.parse
@app.route("/h")
def lang():
    h = Headers()
    h.add_header("Content-Language", urllib.parse.quote(request.args.get("lang")))
    return str(h)
"""),
    "SEC024": (FLASK + """
import re
@app.route("/s")
def search():
    pattern = request.args.get("q")
    return str(re.findall(pattern, "some text"))
""", FLASK + """
import re
@app.route("/s")
def search():
    pattern = re.escape(request.args.get("q"))
    return str(re.findall(pattern, "some text"))
"""),
    "SEC025": (FLASK + """
import importlib
@app.route("/p")
def plugin():
    mod = importlib.import_module(request.args.get("name"))
    return mod.__name__
""", FLASK + """
import importlib
PLUGINS = {"csv": "csv", "json": "json"}
@app.route("/p")
def plugin():
    mod = importlib.import_module(PLUGINS.get("csv"))
    return mod.__name__
"""),
    "SEC026": (FLASK + """
@app.route("/g")
def greet():
    template = request.args.get("t")
    return template.format(user=app)
""", FLASK + """
@app.route("/g")
def greet():
    name = request.args.get("t")
    return "Hello {}".format(len(name))
"""),
    "SEC027": (FLASK + """
class Profile:
    pass
@app.route("/edit", methods=["POST"])
def edit():
    p = Profile()
    for key in request.form:
        setattr(p, key, request.form[key])
    return "ok"
""", FLASK + """
class Profile:
    pass
@app.route("/edit", methods=["POST"])
def edit():
    p = Profile()
    for key in ("name", "email"):
        setattr(p, key, request.form[key])
    return "ok"
"""),
    "SEC028": (FLASK + """
@app.route("/remember")
def remember():
    session["user"] = request.args.get("user")
    return "ok"
""", FLASK + """
@app.route("/remember")
def remember():
    session["visits"] = int(request.args.get("n"))
    return "ok"
"""),
    # ── AST rules ────────────────────────────────────────────────────────
    "SEC029": (FLASK + "app.run(debug=True)\n", FLASK + "import os\napp.run(debug=os.environ.get('DEBUG') == '1')\n"),
    "SEC030": ("import requests\nr = requests.get('https://api.service.io', verify=False)\n",
               "import requests\nr = requests.get('https://api.service.io', verify='/etc/ca.pem')\n"),
    "SEC031": ("import ssl\nctx = ssl._create_unverified_context()\n",
               "import ssl\nctx = ssl.create_default_context()\n"),
    "SEC032": ("import ssl\nctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)\n",
               "import ssl\nctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)\n"),
    "SEC033": ("from Crypto.Cipher import DES\ndef enc(k, d):\n    return DES.new(k, DES.MODE_CBC).encrypt(d)\n",
               "from Crypto.Cipher import AES\ndef enc(k, d):\n    return AES.new(k, AES.MODE_GCM).encrypt(d)\n"),
    "SEC034": ("from Crypto.Cipher import AES\ndef enc(k, d):\n    return AES.new(k, AES.MODE_ECB).encrypt(d)\n",
               "from Crypto.Cipher import AES\ndef enc(k, d):\n    return AES.new(k, AES.MODE_GCM).encrypt(d)\n"),
    "SEC035": ("from cryptography.hazmat.primitives.asymmetric import rsa\n"
               "key = rsa.generate_private_key(public_exponent=65537, key_size=1024)\n",
               "from cryptography.hazmat.primitives.asymmetric import rsa\n"
               "key = rsa.generate_private_key(public_exponent=65537, key_size=3072)\n"),
    "SEC036": ("from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\n"
               "def enc(key):\n    return Cipher(algorithms.AES(key), modes.CBC(b'0123456789abcdef'))\n",
               "import os\nfrom cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\n"
               "def enc(key):\n    return Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))\n"),
    "SEC037": ("import tempfile\npath = tempfile.mktemp()\n",
               "import tempfile\nfd, path = tempfile.mkstemp()\n"),
    "SEC038": ("import os\nos.chmod('/srv/app.log', 0o777)\n", "import os\nos.chmod('/srv/app.log', 0o640)\n"),
    "SEC039": (FLASK + "app.run(host='0.0.0.0')\n", FLASK + "app.run(host='127.0.0.1')\n"),
    "SEC040": ("import ftplib\nftp = ftplib.FTP('files.corp.io')\n",
               "import ftplib\nftp = ftplib.FTP_TLS('files.corp.io')\n"),
    "SEC041": ("import requests\nr = requests.get('http://api.service.io/data')\n",
               "import requests\nr = requests.get('https://api.service.io/data')\n"),
    "SEC042": ("import tarfile\ndef unpack(p):\n    with tarfile.open(p) as tar:\n        tar.extractall('out')\n",
               "import tarfile\ndef unpack(p):\n    with tarfile.open(p) as tar:\n        tar.extractall('out', filter='data')\n"),
    "SEC043": ("import jinja2\nenv = jinja2.Environment(loader=jinja2.FileSystemLoader('t'))\n",
               "import jinja2\nenv = jinja2.Environment(loader=jinja2.FileSystemLoader('t'), "
               "autoescape=jinja2.select_autoescape())\n"),
    "SEC044": (FLASK + "@app.route('/c')\ndef c():\n    r = make_response('x')\n"
               "    r.set_cookie('sid', 'v', secure=False, httponly=True)\n    return r\n",
               FLASK + "@app.route('/c')\ndef c():\n    r = make_response('x')\n"
               "    r.set_cookie('sid', 'v', secure=True, httponly=True, samesite='Lax')\n    return r\n"),
    "SEC045": (FLASK + "app.config['WTF_CSRF_ENABLED'] = False\n",
               FLASK + "app.config['WTF_CSRF_ENABLED'] = True\n"),
    "SEC046": (FLASK + "from flask_cors import CORS\nCORS(app)\n",
               FLASK + "from flask_cors import CORS\nCORS(app, origins=['https://shop.io'])\n"),
    "SEC047": ("import jwt\ndef claims(t):\n    return jwt.decode(t, options={'verify_signature': False})\n",
               "import jwt\ndef claims(t, key):\n    return jwt.decode(t, key, algorithms=['HS256'])\n"),
    "SEC048": ("import paramiko\nc = paramiko.SSHClient()\nc.set_missing_host_key_policy(paramiko.AutoAddPolicy())\n",
               "import paramiko\nc = paramiko.SSHClient()\nc.load_system_host_keys()\n"
               "c.set_missing_host_key_policy(paramiko.RejectPolicy())\n"),
    "SEC049": ("def load(p):\n    try:\n        return open(p).read()\n    except OSError:\n        pass\n",
               "import logging\ndef load(p):\n    try:\n        return open(p).read()\n    except OSError:\n"
               "        logging.warning('cannot read config')\n        return ''\n"),
    "SEC050": ("import logging\nlog = logging.getLogger(__name__)\ndef login(user, password):\n"
               "    log.info('login %s %s', user, password)\n",
               "import logging\nlog = logging.getLogger(__name__)\ndef login(user, password):\n"
               "    log.info('login %s (password length %d)', user, len(password))\n"),
}


def _rules(code: str):
    rep = analyze_source(textwrap.dedent(code), "case.py")
    assert rep.parse_error is None, rep.parse_error
    return {f.rule_id for f in rep.active()}


def test_catalogue_has_fifty_rules():
    assert len(RULES) >= 50
    assert set(CASES) == {f"SEC{n:03d}" for n in range(19, 51)}


@pytest.mark.parametrize("rule", sorted(CASES))
def test_vulnerable_snippet_is_reported(rule):
    assert rule in _rules(CASES[rule][0])


@pytest.mark.parametrize("rule", sorted(CASES))
def test_safe_snippet_is_not_reported(rule):
    assert rule not in _rules(CASES[rule][1])
