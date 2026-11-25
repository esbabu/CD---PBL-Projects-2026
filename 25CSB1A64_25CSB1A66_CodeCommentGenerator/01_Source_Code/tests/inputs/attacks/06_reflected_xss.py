"""Attack 6 - Reflected XSS: ?q=<script>steal(document.cookie)</script> runs in the victim's browser."""
from flask import Flask, make_response, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/search")
def vulnerable_search():
    q = request.args.get("q", "")
    return make_response("<h1>Results for " + q + "</h1>")


@app.route("/search_safe")
def safe_search():
    q = request.args.get("q", "")
    return make_response("<h1>Results for " + str(escape(q)) + "</h1>")
