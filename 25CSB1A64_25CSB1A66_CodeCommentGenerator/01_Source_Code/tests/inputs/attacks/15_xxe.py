"""Attack 15 - XXE: an uploaded XML with <!ENTITY x SYSTEM "file:///etc/passwd"> leaks local files."""
import defusedxml.ElementTree as SafeET
from markupsafe import escape
from flask import Flask, request
from lxml import etree

app = Flask(__name__)


@app.route("/import", methods=["POST"])
def vulnerable_import():
    parser = etree.XMLParser(resolve_entities=True)
    root = etree.fromstring(request.get_data(), parser)
    return escape(root.findtext("name"))


@app.route("/import_safe", methods=["POST"])
def safe_import():
    root = SafeET.fromstring(request.get_data())
    return escape(root.findtext("name"))
