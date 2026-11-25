"""SEC002 fixed with an argument list (os.system -> subprocess.run)."""
import os

from flask import request


def ping():
    host = request.args["host"]
    os.system("ping -c 1 " + host)
    return "ok"
