"""Attack 4 - Code injection: ?expr=__import__('os').system('calc') runs arbitrary Python."""
import ast
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


@app.route("/calc")
def vulnerable_calc():
    expr = request.args.get("expr", "0")
    return escape(str(eval(expr)))


@app.route("/calc_safe")
def safe_calc():
    expr = request.args.get("expr", "0")
    return escape(str(ast.literal_eval(expr)))
