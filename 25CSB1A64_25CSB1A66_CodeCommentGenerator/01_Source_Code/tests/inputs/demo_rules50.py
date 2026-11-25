"""Demo of rules from the 50-rule extension (SEC019-SEC050): one example per line marked
'# SECxxx'. Used for screenshots and the RAG 'explain' demo. Do not deploy."""
import logging
import re
import tarfile

import jwt
import ldap3
import lxml.etree
import requests
from Crypto.Cipher import DES
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, jsonify, make_response, request, session

app = Flask(__name__)
log = logging.getLogger(__name__)


@app.route("/user")
def find_user():
    uid = request.args.get("uid", "")
    conn = ldap3.Connection("ldap://directory")
    conn.search("ou=people,dc=corp", "(uid=" + uid + ")")                       # SEC019
    return jsonify(found=len(conn.entries))


@app.route("/staff")
def staff():
    tree = lxml.etree.parse("staff.xml")
    nodes = tree.xpath("//employee[@id='" + request.args.get("id", "") + "']")   # SEC020
    return jsonify(count=len(nodes))


@app.route("/grep")
def grep():
    pattern = request.args.get("q", "")
    return jsonify(hits=len(re.findall(pattern, "release notes")))              # SEC024


@app.route("/remember")
def remember():
    session["user"] = request.args.get("user", "")                              # SEC028
    resp = make_response("ok")
    resp.set_cookie("theme", "dark", secure=False)                              # SEC044
    return resp


def fetch_report():
    return requests.get("https://reports.acme-corp.com/daily", verify=False)    # SEC030


def encrypt(key, data):
    return DES.new(key, DES.MODE_CBC).encrypt(data)                             # SEC033


def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=1024)       # SEC035


def unpack(path):
    with tarfile.open(path) as tar:
        tar.extractall("out")                                                   # SEC042


def claims(token):
    return jwt.decode(token, options={"verify_signature": False})               # SEC047


def audit_login(user, password):
    log.info("login %s %s", user, password)                                     # SEC050


if __name__ == "__main__":
    app.run(debug=True)                                                          # SEC029
