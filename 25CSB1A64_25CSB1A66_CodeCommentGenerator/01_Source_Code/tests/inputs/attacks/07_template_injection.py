"""Attack 7 - Server-side template injection: ?name={{config.items()}} leaks the app config."""
from markupsafe import escape
from flask import Flask, render_template_string, request

app = Flask(__name__)


@app.route("/hello")
def vulnerable_hello():
    name = request.args.get("name", "guest")
    return render_template_string("<p>Hello " + name + "</p>")


@app.route("/hello_safe")
def safe_hello():
    name = request.args.get("name", "guest")
    return render_template_string("<p>Hello {{ name }}</p>", name=name)
