"""SEC016 (SSRF), SEC017 (open redirect) and SEC018 (XXE)."""
import os
import textwrap

import pytest

from src.agent import FIXED, fix_source
from src.security.analyzer import analyze_file, analyze_source

ATTACKS = os.path.join(os.path.dirname(__file__), "inputs", "attacks")

HEADER = """
import urllib.request
import xml.dom.minidom
import xml.sax
import xml.sax.handler
from urllib.parse import urlparse

import requests
from flask import Flask, abort, redirect, request, url_for
from lxml import etree

app = Flask(__name__)
ALLOWED = {"api.example.com"}
"""


def rules(body: str):
    src = HEADER + textwrap.dedent(body)
    return sorted((f.rule_id, f.function) for f in analyze_source(src, "t.py").active()
                  if f.rule_id in ("SEC016", "SEC017", "SEC018"))


# ── SSRF ──────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("call", [
    "requests.get(url)", "requests.post(url, data={})", "requests.request('GET', url)",
    "urllib.request.urlopen(url)",
])
def test_ssrf_user_controlled_url(call):
    assert rules(f"""
        @app.route("/f")
        def fetch():
            url = request.args.get("u")
            return {call}.read() if False else "ok"
        """) == [("SEC016", "fetch")]


@pytest.mark.parametrize("url", [
    'f"https://api.example.com/users/{uid}"',
    '"https://api.example.com/users/" + uid',
    '"https://api.example.com/q?id=%s" % uid',
    '"https://api.example.com/users/{}".format(uid)',
])
def test_ssrf_fixed_host_is_not_reported(url):
    assert rules(f"""
        @app.route("/f")
        def fetch():
            uid = request.args.get("id")
            requests.get({url})
            return "ok"
        """) == []


def test_ssrf_host_allowlist_check_clears_the_flow():
    assert rules("""
        @app.route("/f")
        def fetch():
            url = request.args.get("u")
            if urlparse(url).hostname not in ALLOWED:
                abort(400)
            requests.get(url)
            return "ok"
        """) == []


def test_ssrf_scheme_only_check_is_not_enough():
    assert rules("""
        @app.route("/f")
        def fetch():
            url = request.args.get("u")
            if urlparse(url).scheme != "https":
                abort(400)
            requests.get(url)
            return "ok"
        """) == [("SEC016", "fetch")]


# ── open redirect ─────────────────────────────────────────────────────────────

def test_redirect_to_request_value():
    assert rules("""
        @app.route("/login")
        def login():
            return redirect(request.args.get("next", "/"))
        """) == [("SEC017", "login")]


@pytest.mark.parametrize("target", ['"/profile/" + name', 'url_for("profile", name=name)'])
def test_redirect_to_local_path_is_not_reported(target):
    assert rules(f"""
        @app.route("/go")
        def go():
            name = request.args.get("n")
            return redirect({target})
        """) == []


def test_protocol_relative_prefix_is_still_reported():
    assert rules("""
        @app.route("/go")
        def go():
            host = request.args.get("h")
            return redirect("//" + host)
        """) == [("SEC017", "go")]


def test_redirect_after_netloc_check_on_parsed_url():
    assert rules("""
        @app.route("/go")
        def go():
            target = request.args.get("next")
            parts = urlparse(target)
            if parts.netloc not in ALLOWED or parts.scheme != "https":
                return "invalid"
            return redirect(target)
        """) == []


def test_redirect_relative_only_check():
    assert rules("""
        @app.route("/go")
        def go():
            target = request.args.get("next")
            if urlparse(target).netloc:
                target = "/"
            return redirect(target)
        """) == []


# ── XXE ───────────────────────────────────────────────────────────────────────

def test_xxe_minidom_with_external_entities_enabled():
    assert rules("""
        @app.route("/x", methods=["POST"])
        def parse():
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges, True)
            doc = xml.dom.minidom.parseString(request.get_data(), parser)
            return doc.documentElement.tagName
        """) == [("SEC018", "parse")]


@pytest.mark.parametrize("setup", [
    "parser = xml.sax.make_parser()",
    "parser = xml.sax.make_parser(); parser.setFeature(xml.sax.handler.feature_external_ges, False)",
])
def test_xxe_default_parser_is_not_reported(setup):
    assert rules(f"""
        @app.route("/x", methods=["POST"])
        def parse():
            {setup}
            doc = xml.dom.minidom.parseString(request.get_data(), parser)
            return doc.documentElement.tagName
        """) == []


def test_xxe_lxml_resolve_entities():
    vulnerable = rules("""
        @app.route("/x", methods=["POST"])
        def parse():
            return etree.fromstring(request.get_data(), etree.XMLParser(resolve_entities=True)).tag
        """)
    safe = rules("""
        @app.route("/x", methods=["POST"])
        def parse():
            return etree.fromstring(request.get_data(), etree.XMLParser(resolve_entities=False)).tag
        """)
    assert vulnerable == [("SEC018", "parse")] and safe == []


def test_xxe_untrusted_flow_required():
    assert rules("""
        def parse():
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges, True)
            return xml.dom.minidom.parseString("<a/>", parser)
        """) == []


# ── attack files and the agent ────────────────────────────────────────────────

@pytest.mark.parametrize("name, rule", [("13_ssrf.py", "SEC016"), ("14_open_redirect.py", "SEC017"),
                                        ("15_xxe.py", "SEC018")])
def test_attack_files_flag_only_the_vulnerable_function(name, rule):
    rep = analyze_file(os.path.join(ATTACKS, name))
    assert sorted({f.function for f in rep.active()}) == [f.function for f in rep.active() if f.rule_id == rule][:1]
    assert all(f.function.startswith("vulnerable") for f in rep.active())


def test_agent_disables_external_entities():
    src = open(os.path.join(ATTACKS, "15_xxe.py"), encoding="utf-8").read()
    res = fix_source(src, "15_xxe.py")
    (outcome,) = res.outcomes
    assert outcome.status == FIXED and outcome.strategy == "xxe-disable-entities"
    assert "resolve_entities=False" in res.patched and "resolve_entities=True" not in res.patched


def test_agent_leaves_ssrf_and_redirect_for_a_human():
    for name in ("13_ssrf.py", "14_open_redirect.py"):
        src = open(os.path.join(ATTACKS, name), encoding="utf-8").read()
        res = fix_source(src, name)
        assert not res.changed and all(o.status != FIXED for o in res.outcomes)
