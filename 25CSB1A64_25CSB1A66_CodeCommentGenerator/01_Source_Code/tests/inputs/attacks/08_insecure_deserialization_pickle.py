"""Attack 8 - Insecure deserialization: a crafted pickle in the cookie executes code on load."""
import base64
import json
import pickle
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


@app.route("/cart")
def vulnerable_cart():
    blob = base64.b64decode(request.cookies.get("cart", ""))
    return escape(str(pickle.loads(blob)))


@app.route("/cart_safe")
def safe_cart():
    blob = base64.b64decode(request.cookies.get("cart", ""))
    return escape(str(json.loads(blob)))
