"""Attack 9 - Unsafe YAML: an uploaded config with !!python/object/apply runs code."""
import yaml
from markupsafe import escape
from flask import Flask, request

app = Flask(__name__)


@app.route("/config", methods=["POST"])
def vulnerable_config():
    data = request.get_data()
    return escape(str(yaml.load(data, Loader=yaml.Loader)))


@app.route("/config_safe", methods=["POST"])
def safe_config():
    data = request.get_data()
    return escape(str(yaml.safe_load(data)))
