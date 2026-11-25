"""Attack 13 - SSRF: ?url=http://169.254.169.254/latest/meta-data/ reads cloud credentials."""
from urllib.parse import urlparse

import requests
from markupsafe import escape
from flask import Flask, abort, request

app = Flask(__name__)
ALLOWED = {"images.example.com"}


@app.route("/preview")
def vulnerable_preview():
    url = request.args.get("url", "")
    return escape(requests.get(url, timeout=5).text)


@app.route("/preview_safe")
def safe_preview():
    url = request.args.get("url", "")
    if urlparse(url).hostname not in ALLOWED:
        abort(400)
    return escape(requests.get(url, timeout=5).text)
