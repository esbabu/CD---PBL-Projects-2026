"""Attack 14 - Open redirect: /login?next=https://evil.example sends users to a phishing site."""
from urllib.parse import urlparse

from markupsafe import escape
from flask import Flask, redirect, request

app = Flask(__name__)


@app.route("/login")
def vulnerable_login():
    return redirect(request.args.get("next", "/"))


@app.route("/login_safe")
def safe_login():
    target = request.args.get("next", "/")
    if urlparse(target).netloc:
        target = "/"
    return redirect(target)
