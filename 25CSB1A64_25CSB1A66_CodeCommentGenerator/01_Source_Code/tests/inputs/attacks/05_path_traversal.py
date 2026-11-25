"""Attack 5 - Path traversal: ?name=../../secrets.env reads files outside the upload folder."""
import os
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)
BASE = "/srv/uploads"


@app.route("/download")
def vulnerable_download():
    name = request.args.get("name", "")
    with open(os.path.join(BASE, name)) as fh:
        return escape(fh.read())


@app.route("/download_safe")
def safe_download():
    name = os.path.basename(request.args.get("name", ""))
    with open(os.path.join(BASE, name)) as fh:
        return escape(fh.read())
