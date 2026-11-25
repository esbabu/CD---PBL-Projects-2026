"""Attack 3 - Command injection through subprocess with shell=True: ?file=a.txt && whoami."""
import subprocess
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


@app.route("/count")
def vulnerable_count():
    name = request.form["file"]
    out = subprocess.check_output(f"find /c /v \"\" {name}", shell=True)
    return escape(out.decode())


@app.route("/count_safe")
def safe_count():
    name = request.form["file"]
    out = subprocess.check_output(["find", "/c", "/v", "", name])
    return escape(out.decode())
