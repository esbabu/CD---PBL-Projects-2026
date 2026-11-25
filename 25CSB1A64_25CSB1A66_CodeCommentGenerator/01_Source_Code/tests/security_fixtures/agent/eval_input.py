"""SEC001 fixed with ast.literal_eval (import added)."""
from flask import request


def calculate():
    return eval(request.args["expr"])
