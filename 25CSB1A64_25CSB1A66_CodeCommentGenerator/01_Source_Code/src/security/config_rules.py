"""
Configuration, crypto and transport rules (SEC029-SEC050)
==========================================================
AST pattern rules for insecure *settings* rather than insecure data flows:
debug mode, TLS verification, weak protocols and ciphers, key sizes, static
IVs, temporary files, file permissions, network binding, cleartext protocols,
archive extraction, template auto-escaping, cookie flags, CSRF, CORS, JWT
verification, SSH host keys, swallowed exceptions and secrets in logs.

Each check looks at one call, assignment, decorator or handler and reports the
line of that node. Names are resolved through the module's imports, so
``from requests import get`` and ``import requests as r`` are both understood.
"""
from __future__ import annotations

import ast
import re
from typing import Callable, Dict, List, Optional, Set

from ..ir.lowering import collect_module_imports

RawFinding = Dict[str, object]

_HTTP_CLIENTS = re.compile(r"^(requests|httpx|aiohttp|urllib3)(\.|$)")
_HTTP_VERBS = {"get", "post", "put", "patch", "delete", "head", "options", "request", "stream",
               "Client", "AsyncClient", "Session", "urlopen", "Request"}
# PROTOCOL_SSLv23 / SSLv23_METHOD are not listed: despite the name they negotiate the
# highest version both sides support.
_WEAK_TLS_ATTRS = {"PROTOCOL_SSLv2", "PROTOCOL_SSLv3", "PROTOCOL_TLSv1", "PROTOCOL_TLSv1_1",
                   "SSLv2_METHOD", "SSLv3_METHOD", "TLSv1_METHOD", "TLSv1_1_METHOD"}
_WEAK_TLS_VERSIONS = {"SSLv3", "TLSv1", "TLSv1_1"}
_WEAK_CIPHERS = {
    "Crypto.Cipher.DES.new": "DES", "Crypto.Cipher.DES3.new": "3DES",
    "Crypto.Cipher.ARC4.new": "RC4", "Crypto.Cipher.ARC2.new": "RC2",
    "Crypto.Cipher.Blowfish.new": "Blowfish", "Crypto.Cipher.XOR.new": "XOR",
    "Cryptodome.Cipher.DES.new": "DES", "Cryptodome.Cipher.DES3.new": "3DES",
    "Cryptodome.Cipher.ARC4.new": "RC4", "Cryptodome.Cipher.ARC2.new": "RC2",
    "Cryptodome.Cipher.Blowfish.new": "Blowfish",
}
_WEAK_CIPHER_ALGOS = {"TripleDES": "3DES", "ARC4": "RC4", "Blowfish": "Blowfish", "IDEA": "IDEA",
                      "CAST5": "CAST5", "SEED": "SEED"}
_IV_MODES = {"CBC", "CFB", "CFB8", "OFB", "CTR", "GCM", "XTS"}
_CLEARTEXT = {"ftplib.FTP": "FTP", "telnetlib.Telnet": "Telnet", "poplib.POP3": "POP3",
              "imaplib.IMAP4": "IMAP"}
_LOCAL_HOSTS = re.compile(r"^http://(localhost|127\.\d+\.\d+\.\d+|\[::1\]|0\.0\.0\.0)([:/]|$)|"
                          r"^http://[^/]*\.(local|localhost|test|example|invalid|internal)([:/]|$)|"
                          r"^http://(www\.)?example\.(com|org|net)([:/]|$)", re.I)
_LOG_METHODS = {"debug", "info", "warning", "warn", "error", "critical", "exception", "log"}
_LOG_RECEIVER = re.compile(r"(?i)(^|_)(log|logger|logging|_log)$")
_SENSITIVE = re.compile(r"(?i)(^|_)(pass(word|wd|phrase)?|pwd|secret|token|api_?key|apikey|"
                        r"access_?key|private_?key|credentials?|client_?secret|ssn|card_?number|"
                        r"cvv)(s)?($|_)")
_NOT_SENSITIVE = re.compile(r"(?i)_(len|length|count|id|name|type|field|label|hash|hashed|"
                            r"digest|masked|expiry|ttl|url|path|file)$|^(is|has|num|n)_")


def _const(node, *types):
    return isinstance(node, ast.Constant) and isinstance(node.value, types)


def _kw(call: ast.Call, name: str) -> Optional[ast.AST]:
    return next((k.value for k in call.keywords if k.arg == name), None)


class _ConfigRules(ast.NodeVisitor):
    def __init__(self, filepath: str, func_at: Callable[[int], str]):
        self.filepath = filepath
        self.func_at = func_at
        self.out: List[RawFinding] = []
        self.imports: Dict[str, str] = {}
        self.tar_names: Set[str] = set()       # names bound to a tarfile.open(...) result
        self.bytes_consts: Dict[str, int] = {}  # name -> line of a literal bytes assignment

    # ── helpers ─────────────────────────────────────────────────────────

    def canonical(self, node) -> Optional[str]:
        if isinstance(node, ast.Name):
            return self.imports.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base = self.canonical(node.value)
            return f"{base}.{node.attr}" if base else None
        return None

    def add(self, rule_id: str, node: ast.AST, message: str, confidence: str = "high",
            reasons: Optional[List[str]] = None) -> None:
        line = getattr(node, "lineno", 0)
        self.out.append({"rule_id": rule_id, "line": line, "col": getattr(node, "col_offset", 0),
                         "function": self.func_at(line), "message": message,
                         "confidence": confidence, "confidence_reasons": reasons or [],
                         "status": None, "suppression_reason": "", "code": ""})

    @staticmethod
    def _sensitive(name: Optional[str]) -> bool:
        return bool(name) and bool(_SENSITIVE.search(name)) and not _NOT_SENSITIVE.search(name)

    def _names_in(self, node) -> List[str]:
        """Names of the values an expression logs: the last part of an attribute chain, a
        string subscript key, a bare name. Arguments of len()/type()/bool() and of masking
        helpers are skipped (logging how many tokens exist does not log a token)."""
        out: List[str] = []

        def walk(n):
            if isinstance(n, ast.Constant):
                return
            if isinstance(n, ast.Name):
                out.append(n.id)
            elif isinstance(n, ast.Attribute):
                out.append(n.attr)
            elif isinstance(n, ast.Subscript):
                if _const(n.slice, str):
                    out.append(n.slice.value)
                else:
                    walk(n.value)
            elif isinstance(n, ast.Call):
                fname = self.canonical(n.func) or ""
                if fname in ("len", "bool", "type", "isinstance", "id", "hash") or \
                        re.search(r"(?i)mask|redact|hash|digest|fingerprint", fname):
                    return
                for a in list(n.args) + [k.value for k in n.keywords]:
                    walk(a)
            else:
                for c in ast.iter_child_nodes(n):
                    walk(c)
        walk(node)
        return out

    # ── traversal ───────────────────────────────────────────────────────

    def visit_Module(self, node: ast.Module):
        self.imports = collect_module_imports(node)
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) \
                    and (self.canonical(n.value.func) or "") in ("tarfile.open", "tarfile.TarFile"):
                self.tar_names.update(t.id for t in n.targets if isinstance(t, ast.Name))
            if isinstance(n, ast.withitem) and isinstance(n.context_expr, ast.Call) \
                    and (self.canonical(n.context_expr.func) or "") in ("tarfile.open", "tarfile.TarFile") \
                    and isinstance(n.optional_vars, ast.Name):
                self.tar_names.add(n.optional_vars.id)
            if isinstance(n, ast.Assign) and _const(n.value, bytes) and len(n.value.value) >= 8:
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.bytes_consts[t.id] = n.lineno
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for d in node.decorator_list:
            target = d.func if isinstance(d, ast.Call) else d
            name = self.canonical(target) or ""
            if name.endswith("csrf_exempt") or name.endswith("csrf.exempt"):
                self.add("SEC045", d, f"View '{node.name}' is exempt from CSRF protection.")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    # ── assignments: settings ──────────────────────────────────────────

    def _setting_name(self, t) -> Optional[str]:
        if isinstance(t, ast.Name):
            return t.id
        if isinstance(t, ast.Attribute):
            return t.attr
        if isinstance(t, ast.Subscript) and _const(t.slice, str):
            return t.slice.value
        return None

    def visit_Assign(self, node: ast.Assign):
        v = node.value
        for t in node.targets:
            name = self._setting_name(t) or ""
            if _const(v, bool):
                if v.value is True and name in ("debug", "DEBUG") and not isinstance(t, ast.Name):
                    self.add("SEC029", node, f"Debug mode switched on ({ast.unparse(t)} = True).")
                if v.value is False and name == "check_hostname":
                    self.add("SEC031", node, "Hostname checking disabled (check_hostname = False).")
                if v.value is False and name == "verify" and isinstance(t, ast.Attribute):
                    self.add("SEC030", node, f"TLS verification disabled ({ast.unparse(t)} = False).")
                if v.value is False and name in ("SESSION_COOKIE_SECURE", "SESSION_COOKIE_HTTPONLY",
                                                 "CSRF_COOKIE_SECURE", "REMEMBER_COOKIE_SECURE"):
                    self.add("SEC044", node, f"{name} is set to False.")
                if v.value is False and name in ("WTF_CSRF_ENABLED", "CSRF_ENABLED", "WTF_CSRF_CHECK_DEFAULT"):
                    self.add("SEC045", node, f"CSRF protection disabled ({name} = False).")
                if v.value is True and name in ("CORS_ORIGIN_ALLOW_ALL", "CORS_ALLOW_ALL_ORIGINS"):
                    self.add("SEC046", node, f"{name} = True accepts requests from any origin.")
            if name == "_create_default_https_context" and \
                    (self.canonical(v) or "").endswith("_create_unverified_context"):
                self.add("SEC031", node, "The default HTTPS context is replaced by an unverified one.")
            if name == "minimum_version" and isinstance(v, ast.Attribute) and v.attr in _WEAK_TLS_VERSIONS:
                self.add("SEC032", node, f"Minimum TLS version set to {v.attr}.")
            if name.lower() == "access-control-allow-origin" and _const(v, str) and v.value.strip() == "*":
                self.add("SEC046", node, "Access-Control-Allow-Origin is '*'.")
            if name in ("CORS_ORIGINS", "CORS_ALLOWED_ORIGINS") and _const(v, str) and v.value.strip() == "*":
                self.add("SEC046", node, f"{name} = '*' accepts requests from any origin.")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        for k, v in zip(node.keys, node.values):
            if _const(k, str) and k.value.lower() == "access-control-allow-origin" \
                    and _const(v, str) and v.value.strip() == "*":
                self.add("SEC046", v, "Access-Control-Allow-Origin header is '*'.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.ctx, ast.Load):
            name = self.canonical(node) or ""
            if node.attr in _WEAK_TLS_ATTRS and (name.startswith("ssl.") or name.startswith("OpenSSL.")):
                self.add("SEC032", node, f"Insecure protocol constant {node.attr}.")
            elif node.attr in _WEAK_TLS_VERSIONS and name.startswith("ssl.TLSVersion."):
                self.add("SEC032", node, f"Insecure TLS version ssl.TLSVersion.{node.attr}.")
            elif node.attr == "MODE_ECB":
                self.add("SEC034", node, f"ECB mode ({ast.unparse(node)}).")
            elif name == "ssl.CERT_NONE":
                self.add("SEC031", node, "ssl.CERT_NONE disables certificate verification.")
        self.generic_visit(node)

    # ── handlers ───────────────────────────────────────────────────────

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is not None and all(
                isinstance(s, (ast.Pass, ast.Continue)) or
                (isinstance(s, ast.Expr) and _const(s.value, type(Ellipsis))) for s in node.body):
            self.add("SEC049", node,
                     f"'except {ast.unparse(node.type)}' discards the exception without handling "
                     "or logging it.", "medium",
                     ["ignoring this exception may be intentional (an optional feature or "
                      "best-effort cleanup)"])
        self.generic_visit(node)

    # ── calls ──────────────────────────────────────────────────────────

    def visit_Call(self, node: ast.Call):
        name = self.canonical(node.func) or ""
        method = node.func.attr if isinstance(node.func, ast.Attribute) else ""
        self._debug(node, name, method)
        self._tls(node, name, method)
        self._crypto(node, name, method)
        self._files(node, name, method)
        self._network(node, name, method)
        self._web(node, name, method)
        self._logging(node, name, method)
        self.generic_visit(node)

    def _debug(self, node, name, method):
        debug = _kw(node, "debug")
        if method == "run" and _const(debug, bool) and debug.value is True:
            self.add("SEC029", node, f"{ast.unparse(node.func)}(debug=True) enables the interactive debugger.")
        if name.endswith("config.update") or method == "update" and \
                isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Attribute) \
                and node.func.value.attr == "config":
            for k in node.keywords:
                if k.arg == "DEBUG" and _const(k.value, bool) and k.value.value is True:
                    self.add("SEC029", node, "config.update(DEBUG=True) enables debug mode.")

    def _tls(self, node, name, method):
        verify = _kw(node, "verify")
        if _const(verify, bool) and verify.value is False and \
                (_HTTP_CLIENTS.match(name) or method in _HTTP_VERBS):
            self.add("SEC030", node, f"{ast.unparse(node.func)}(..., verify=False) skips certificate checks.")
        if name in ("ssl._create_unverified_context", "ssl._create_stdlib_context"):
            self.add("SEC031", node, f"{name}() creates a context that does not verify certificates.")
        if name == "ssl.wrap_socket":
            self.add("SEC032", node, "ssl.wrap_socket() is deprecated and does not check host names; "
                                     "use SSLContext.wrap_socket().")
        if name in ("ssl.SSLContext", "OpenSSL.SSL.Context") and node.args and \
                isinstance(node.args[0], ast.Attribute) and node.args[0].attr in _WEAK_TLS_ATTRS:
            pass  # reported once by visit_Attribute on the constant
        if method == "set_missing_host_key_policy" and node.args:
            pol = node.args[0]
            pol_name = self.canonical(pol.func if isinstance(pol, ast.Call) else pol) or ""
            if pol_name.endswith(("AutoAddPolicy", "WarningPolicy")):
                self.add("SEC048", node, f"SSH client accepts unknown host keys ({pol_name.rsplit('.', 1)[-1]}).")

    def _crypto(self, node, name, method):
        if name in _WEAK_CIPHERS:
            self.add("SEC033", node, f"{_WEAK_CIPHERS[name]} cipher ({name}).")
        tail = name.rsplit(".", 1)[-1]
        if ".ciphers.algorithms." in name and tail in _WEAK_CIPHER_ALGOS:
            self.add("SEC033", node, f"{_WEAK_CIPHER_ALGOS[tail]} cipher ({name}).")
        if ".ciphers.modes." in name and tail == "ECB":
            self.add("SEC034", node, "ECB mode (modes.ECB).")
        # key sizes
        size = None
        if name.endswith(("asymmetric.rsa.generate_private_key", "asymmetric.dsa.generate_private_key")):
            size = _kw(node, "key_size") or (node.args[1] if "rsa" in name and len(node.args) > 1 else
                                             node.args[0] if "dsa" in name and node.args else None)
        elif name in ("Crypto.PublicKey.RSA.generate", "Cryptodome.PublicKey.RSA.generate",
                      "Crypto.PublicKey.DSA.generate", "Cryptodome.PublicKey.DSA.generate"):
            size = _kw(node, "bits") or (node.args[0] if node.args else None)
        if _const(size, int) and size.value < 2048:
            self.add("SEC035", node, f"{size.value}-bit key generated by {name.rsplit('.', 2)[-2]}.")
        # static IV / nonce
        iv = None
        if ".ciphers.modes." in name and tail in _IV_MODES:
            iv = node.args[0] if node.args else (_kw(node, "initialization_vector") or _kw(node, "nonce"))
        elif name.endswith(".new") and name.startswith(("Crypto.Cipher.", "Cryptodome.Cipher.")):
            iv = _kw(node, "iv") or _kw(node, "nonce") or (node.args[2] if len(node.args) > 2 else None)
        if iv is not None:
            if _const(iv, bytes):
                self.add("SEC036", node, "IV/nonce is a constant byte string.")
            elif isinstance(iv, ast.Name) and iv.id in self.bytes_consts:
                self.add("SEC036", node, f"IV/nonce '{iv.id}' is the constant assigned on line "
                                         f"{self.bytes_consts[iv.id]}.", "medium",
                         ["the name may be reassigned on another path"])

    def _files(self, node, name, method):
        if name == "tempfile.mktemp":
            self.add("SEC037", node, "tempfile.mktemp() returns a name that another process can create first.")
        mode = None
        if name in ("os.chmod", "os.fchmod", "os.lchmod") and len(node.args) > 1:
            mode = node.args[1]
        elif method == "chmod" and not name.startswith("os.") and node.args:
            mode = node.args[0]
        elif name in ("os.open", "os.mkdir", "os.makedirs") and len(node.args) > (2 if name == "os.open" else 1):
            mode = node.args[2 if name == "os.open" else 1]
        if mode is None:
            mode = _kw(node, "mode") if name in ("os.chmod", "os.open", "os.mkdir", "os.makedirs") else None
        if mode is not None and self._world_writable(mode):
            self.add("SEC038", node, f"Mode {ast.unparse(mode)} makes the file world-writable.")
        if name == "os.umask" and node.args and _const(node.args[0], int) and node.args[0].value & 0o022 == 0:
            self.add("SEC038", node, f"os.umask({ast.unparse(node.args[0])}) creates world-writable files.")
        if method in ("extractall", "extract") and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name) and node.func.value.id in self.tar_names \
                and _kw(node, "filter") is None:
            self.add("SEC042", node, f"TarFile.{method}() without filter= can write outside the target "
                                     "directory (../ or absolute member names, links).")
        if name == "shutil.unpack_archive" and _kw(node, "filter") is None:
            self.add("SEC042", node, "shutil.unpack_archive() without filter= extracts tar members unchecked.",
                     "medium", ["the archive may be a zip file, whose member names Python sanitises"])

    def _world_writable(self, mode) -> bool:
        if _const(mode, int):
            return bool(mode.value & 0o002)
        names = [n.attr if isinstance(n, ast.Attribute) else n.id
                 for n in ast.walk(mode) if isinstance(n, (ast.Attribute, ast.Name))]
        return any(n in ("S_IWOTH", "S_IRWXO") for n in names)

    def _network(self, node, name, method):
        host = _kw(node, "host")
        if _const(host, str) and host.value in ("0.0.0.0", "::"):
            self.add("SEC039", node, f"{ast.unparse(node.func)}(host='{host.value}') listens on every interface.")
        if method == "bind" and node.args and isinstance(node.args[0], ast.Tuple) and node.args[0].elts \
                and _const(node.args[0].elts[0], str) and node.args[0].elts[0].value in ("0.0.0.0", "", "::"):
            self.add("SEC039", node, "Socket bound to all interfaces.")
        if name in _CLEARTEXT:
            self.add("SEC040", node, f"{_CLEARTEXT[name]} sends credentials and data in clear text ({name}).")
        url = node.args[0] if node.args else _kw(node, "url")
        if method == "request" and len(node.args) > 1:
            url = node.args[1]
        if _const(url, str) and url.value.lower().startswith("http://") \
                and not _LOCAL_HOSTS.match(url.value) and \
                (_HTTP_CLIENTS.match(name) or name.startswith("urllib.request.")) \
                and name.rsplit(".", 1)[-1] in _HTTP_VERBS:
            self.add("SEC041", node, f"Request to {url.value} over plain HTTP.")

    def _web(self, node, name, method):
        if name in ("jinja2.Environment", "jinja2.environment.Environment"):
            ae = _kw(node, "autoescape")
            if ae is None:
                self.add("SEC043", node, "jinja2.Environment() without autoescape= renders HTML unescaped.",
                         "medium", ["the environment may render non-HTML text such as e-mail or config"])
            elif _const(ae, bool) and ae.value is False:
                self.add("SEC043", node, "jinja2.Environment(autoescape=False).")
        if method == "set_cookie":
            secure, httponly = _kw(node, "secure"), _kw(node, "httponly")
            if _const(secure, bool) and secure.value is False:
                self.add("SEC044", node, "Cookie set with secure=False.")
            elif _const(httponly, bool) and httponly.value is False:
                self.add("SEC044", node, "Cookie set with httponly=False.")
            elif secure is None and not any(k.arg is None for k in node.keywords):
                self.add("SEC044", node, "Cookie set without secure=True.", "medium",
                         ["the application may set SESSION_COOKIE_SECURE or run behind HTTPS-only "
                          "middleware"])
        if name.endswith("CORS") and name.split(".")[0] in ("flask_cors", "CORS"):
            origins = _kw(node, "origins") or _kw(node, "resources")
            if origins is None:
                self.add("SEC046", node, "CORS(app) without origins= allows every origin.")
            elif _const(origins, str) and origins.value.strip() == "*":
                self.add("SEC046", node, "CORS origins='*'.")
        if method == "exempt" and "csrf" in ast.unparse(node.func.value).lower():
            self.add("SEC045", node, "View exempted from CSRF protection.")
        if name in ("jwt.decode", "jose.jwt.decode", "jwt.api_jwt.decode"):
            opts = _kw(node, "options")
            if isinstance(opts, ast.Dict):
                for k, v in zip(opts.keys, opts.values):
                    if _const(k, str) and k.value in ("verify_signature", "verify_exp") \
                            and _const(v, bool) and v.value is False:
                        self.add("SEC047", node, f"jwt.decode(..., options={{'{k.value}': False}}).")
            verify = _kw(node, "verify")
            if _const(verify, bool) and verify.value is False:
                self.add("SEC047", node, "jwt.decode(..., verify=False).")
            algs = _kw(node, "algorithms")
            if isinstance(algs, (ast.List, ast.Tuple)) and any(
                    _const(e, str) and e.value.lower() == "none" for e in algs.elts):
                self.add("SEC047", node, "jwt.decode accepts the 'none' algorithm.")

    def _logging(self, node, name, method):
        is_log = name.startswith("logging.") and name.rsplit(".", 1)[-1] in _LOG_METHODS
        if not is_log and method in _LOG_METHODS and isinstance(node.func, ast.Attribute):
            recv = node.func.value
            recv_name = recv.attr if isinstance(recv, ast.Attribute) else getattr(recv, "id", "")
            is_log = bool(_LOG_RECEIVER.search(recv_name or ""))
        if not is_log and name != "print":
            return
        for arg in list(node.args) + [k.value for k in node.keywords if k.arg not in ("exc_info", "extra")]:
            if _const(arg, str):
                continue
            hit = next((n for n in self._names_in(arg) if self._sensitive(n)), None)
            if hit:
                where = "print()" if name == "print" else "the log"
                self.add("SEC050", node, f"'{hit}' is written to {where}.",
                         "medium" if name == "print" else "high",
                         ["sensitivity inferred from the name"])
                break


def run_config_rules(tree: ast.Module, filepath: str, func_at: Callable[[int], str]) -> List[RawFinding]:
    v = _ConfigRules(filepath, func_at)
    v.visit(tree)
    seen, out = set(), []
    for f in v.out:                      # one report per rule and line
        key = (f["rule_id"], f["line"])
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out
