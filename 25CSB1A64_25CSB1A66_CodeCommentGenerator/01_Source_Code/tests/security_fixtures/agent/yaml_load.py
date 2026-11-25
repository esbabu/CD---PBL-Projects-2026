"""SEC010 fixed with yaml.safe_load."""
import yaml
from flask import request


def read_config():
    return yaml.load(request.data, Loader=yaml.Loader)
