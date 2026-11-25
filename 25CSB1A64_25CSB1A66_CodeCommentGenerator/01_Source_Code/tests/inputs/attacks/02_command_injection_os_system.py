"""Attack 2 - OS command injection: ?host=8.8.8.8;del /q *.* runs a second command."""
import os
import subprocess
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


@app.route("/ping")
def vulnerable_ping():
    host = request.args.get("host", "")
    os.system("ping -n 1 " + host)
    return "done"


@app.route("/ping_safe")
def safe_ping():
    host = request.args.get("host", "")
    subprocess.run(["ping", "-n", "1", host], check=False)
    return "done"
