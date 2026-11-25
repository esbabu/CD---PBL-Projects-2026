"""
Syntax-level security rules for Java, C, C++, C# and Rust
==========================================================
Rules that are properties of the code itself rather than of a data flow. They
read the lowered calls (callee, literal arguments) and, where the syntax tree is
needed, the tree-sitter nodes.

  SEC003 hard-coded credentials        SEC004 weak hash            SEC011 weak randomness
  SEC009 dangerous deserializer use    SEC018 XXE parser config    SEC026 non-literal format string
  SEC029 debug / developer page        SEC030-032 TLS checks off   SEC033-036 weak crypto
  SEC037 insecure temp file            SEC044 cookie flags         SEC045 CSRF disabled
  SEC046 CORS any origin               SEC047 JWT not verified     SEC049 swallowed exception
  SEC050 secret in a log               SEC051 gets()               SEC052 unbounded copy / %s
  SEC059 TOCTOU race                   SEC060 unsafe memory op     SEC061 missing authorization
  SEC063 shared mutable state
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..ir.ir_nodes import IROpcode
from ..security.ast_rules import _KNOWN_FORMATS, _NOT_SECRET_SUFFIX, _PLACEHOLDER, _SECRET_NAME, _mask
from .lower import FunctionInfo, LoweredModule, fld, named, text

Raw = Dict[str, object]
_SEC_CTX = re.compile(r"(?i)(token|passw|secret|nonce|salt|otp|session|csrf|auth|reset|api_?key|apikey|private|"
                      r"signature|credential|key$|^key|iv$)")
_SENSITIVE = re.compile(r"(?i)(^|_|[a-z])(pass(word|wd|phrase)?|pwd|secret|token|api_?key|apikey|credential|"
                        r"private_?key|ssn|card_?number|cvv)(s)?($|_|[A-Z])")
_NOT_SENSITIVE = re.compile(r"(?i)(len|length|count|id|name|type|field|label|hash|hashed|digest|masked|url|path|"
                            r"file|expiry|ttl|policy|header)$")


class _Ctx:
    def __init__(self, mod: LoweredModule):
        self.mod, self.lang = mod, mod.language
        self.src = mod.source.encode("utf-8")
        self.lines = mod.source.splitlines()
        self.out: List[Raw] = []
        self.seen = set()

    def add(self, rule: str, line: int, col: int, fn: str, msg: str, confidence: str = "high",
            reasons: Optional[List[str]] = None, analysis: str = "ast-pattern") -> None:
        key = (rule, line)
        if key in self.seen:
            return
        self.seen.add(key)
        self.out.append({"rule_id": rule, "line": line, "col": col, "function": fn, "message": msg,
                         "confidence": confidence, "confidence_reasons": reasons or [], "analysis": analysis})

    def code(self, line: int) -> str:
        return self.lines[line - 1].strip() if 0 < line <= len(self.lines) else ""


def _calls(info: FunctionInfo):
    for ins in info.fn.all_instructions():
        if ins.op == IROpcode.CALL and ins.call is not None:
            yield ins


def _names(ins) -> str:
    return f"{ins.call.callee} {ins.meta.get('chain', '')}"


def _has(ins, *suffixes) -> bool:
    names = (ins.call.callee, ins.meta.get("chain", ""))
    return any(n == s or n.endswith("." + s) or n.replace("std.", "") == s for n in names for s in suffixes)


def _lit(ins, k: int = 0) -> Optional[str]:
    return ins.call.const_kwargs.get(f"#{k}")


def _int(v: Optional[str]) -> Optional[int]:
    try:
        return int(str(v).rstrip("uUlL").replace("_", ""), 0) if v is not None else None
    except ValueError:
        return None


def _secret_name(name: str) -> bool:
    return bool(_SECRET_NAME.search(name)) and not _NOT_SECRET_SUFFIX.search(name)


def _secret_value(v: str) -> bool:
    v = (v or "").strip()
    if len(v) < 4 or _PLACEHOLDER.match(v) or len(set(v)) <= 2 or re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", v):
        return False
    return not (" " in v and len(v.split()) > 3)


# ---------------------------------------------------------------------------
# per-function checks over lowered calls
# ---------------------------------------------------------------------------

def _crypto_and_misc(cx: _Ctx, info: FunctionInfo) -> None:
    q, lang = info.fn.qualname, cx.lang
    for ins in _calls(info):
        c, L, col = ins.call, ins.lineno, ins.col
        if lang in ("c", "cpp") and c.callee.startswith("std.") and not c.method:
            c = _StdView(c)
        a0 = (_lit(ins, 0) or "")
        A0 = a0.upper().replace("_", "-")
        # ── weak hash ───────────────────────────────────────────────────
        if (_has(ins, "MessageDigest.getInstance", "DigestUtils.getInstance") and A0 in ("MD5", "MD2", "MD4", "SHA1", "SHA-1", "SHA")) \
                or _has(ins, "MD5.Create", "SHA1.Create", "new MD5CryptoServiceProvider", "new SHA1Managed",
                        "new SHA1CryptoServiceProvider", "MD5", "SHA1", "MD5_Init", "SHA1_Init", "EVP_md5", "EVP_sha1",
                        "md5.compute", "Md5.new", "Sha1.new", "md5.Md5.new", "sha1.Sha1.new", "DigestUtils.md5Hex",
                        "DigestUtils.sha1Hex", "DigestUtils.md5", "HashAlgorithm.Create#md5") \
                or (_has(ins, "HashAlgorithm.Create") and A0 in ("MD5", "SHA1")):
            if not (lang in ("c", "cpp") and c.callee in ("MD5", "SHA1") and not c.args):
                cx.add("SEC004", L, col, q, f"Weak hash algorithm ({c.raw_callee}{'(' + a0 + ')' if a0 else ''}).",
                       "medium", ["whether the digest protects security-relevant data is not determined"])
        # ── weak cipher / ECB / key size / static IV ────────────────────
        if _has(ins, "Cipher.getInstance"):
            if re.match(r"(?i)(DES|DESede|TripleDES|RC2|RC4|ARCFOUR|Blowfish)\b", a0):
                cx.add("SEC033", L, col, q, f"Weak cipher Cipher.getInstance(\"{a0}\").")
            if re.search(r"(?i)/ECB/", a0) or re.fullmatch(r"(?i)(AES|DES|DESede|Blowfish)", a0):
                cx.add("SEC034", L, col, q, f"ECB mode: Cipher.getInstance(\"{a0}\")"
                       + (" defaults to ECB." if "/" not in a0 else "."))
        if _has(ins, "DES.Create", "TripleDES.Create", "RC2.Create", "new DESCryptoServiceProvider",
                "new TripleDESCryptoServiceProvider", "new RC2CryptoServiceProvider", "EVP_des_ecb", "EVP_des_cbc",
                "EVP_des_ede3_cbc", "EVP_rc4", "EVP_bf_cbc", "EVP_rc2_cbc", "DES_ecb_encrypt", "DES_set_key",
                "Des.new", "TdesEde3.new", "Rc4.new", "des.Des.new", "Blowfish.new"):
            cx.add("SEC033", L, col, q, f"Weak cipher ({c.raw_callee}).")
        if _has(ins, "EVP_aes_128_ecb", "EVP_aes_192_ecb", "EVP_aes_256_ecb", "AES_ecb_encrypt", "Ecb.new"):
            cx.add("SEC034", L, col, q, f"ECB mode ({c.raw_callee}).")
        if _has(ins, "KeyPairGenerator.initialize", "*initialize") and c.method == "initialize":
            n = _int(_lit(ins, 0))
            if n is not None and n < 2048 and "keypair" in (ins.meta.get("rtype", "") + ins.meta.get("receiver_name", "")).lower() or \
                    (n is not None and n < 2048 and _has(ins, "KeyPairGenerator.initialize")):
                cx.add("SEC035", L, col, q, f"{n}-bit key pair.")
        if _has(ins, "new RSACryptoServiceProvider", "RSA.Create", "new DSACryptoServiceProvider", "RSA_generate_key",
                "EVP_PKEY_CTX_set_rsa_keygen_bits", "RsaPrivateKey.new", "RSA_generate_key_ex"):
            k = 1 if _has(ins, "EVP_PKEY_CTX_set_rsa_keygen_bits", "RsaPrivateKey.new") else 0
            n = _int(_lit(ins, k)) or _int(_lit(ins, 0))
            if n is not None and 0 < n < 2048:
                cx.add("SEC035", L, col, q, f"{n}-bit RSA/DSA key.")
        if _has(ins, "new IvParameterSpec", "new GCMParameterSpec") and c.args:
            k = 1 if "GCM" in c.callee else 0
            d = _def(info, c.args[k] if k < len(c.args) else None)
            if d is not None and (d.op == IROpcode.ASSIGN and "const" in d.meta or
                                  d.op == IROpcode.CALL and d.call and d.call.method == "getBytes" and
                                  _def(info, d.call.receiver) is not None and
                                  "const" in _def(info, d.call.receiver).meta):
                cx.add("SEC036", L, col, q, "Static initialisation vector (a constant byte string).", "medium",
                       ["the constant may be reassigned on another path"])
        # ── weak randomness in a security context ───────────────────────
        if _has(ins, "new Random", "Math.random", "rand", "random", "srand", "drand48", "lrand48") and \
                not _has(ins, "new SecureRandom"):
            if lang in ("c", "cpp") and c.callee not in ("rand", "random", "drand48", "lrand48"):
                continue
            ctx = _security_context(info, ins)
            if ctx:
                cx.add("SEC011", L, col, q, f"{c.raw_callee}() is predictable but used for {ctx}.", "medium",
                       [f"security use inferred from the name {ctx!r}"])
        # ── TLS ─────────────────────────────────────────────────────────
        if _has(ins, "SSLContext.getInstance") and a0 in ("SSL", "SSLv2", "SSLv3", "TLSv1", "TLSv1.1"):
            cx.add("SEC032", L, col, q, f"Insecure protocol SSLContext.getInstance(\"{a0}\").")
        if _has(ins, "SSLv3_method", "SSLv23_method", "TLSv1_method", "TLSv1_1_method", "SSLv2_method"):
            if not c.callee.endswith("SSLv23_method"):
                cx.add("SEC032", L, col, q, f"Insecure protocol ({c.raw_callee}).")
        if _has(ins, "SSL_CTX_set_verify", "SSL_set_verify") and len(c.args) >= 2 and \
                (_lit(ins, 1) in ("SSL_VERIFY_NONE", "0") or _const_name(info, c.args[1]) == "SSL_VERIFY_NONE"):
            cx.add("SEC031", L, col, q, "Certificate verification disabled (SSL_VERIFY_NONE).")
        if _has(ins, "curl_easy_setopt") and len(c.args) >= 3 and \
                _const_name(info, c.args[1]) in ("CURLOPT_SSL_VERIFYPEER", "CURLOPT_SSL_VERIFYHOST") and \
                (_lit(ins, 2) or "").rstrip("Ll") in ("0", "FALSE"):
            cx.add("SEC030", L, col, q, f"TLS verification disabled ({_const_name(info, c.args[1])} = 0).")
        if c.method in ("danger_accept_invalid_certs", "danger_accept_invalid_hostnames") and _lit(ins, 0) == "true":
            cx.add("SEC030", L, col, q, f"{c.method}(true) disables certificate checks.")
        # ── deserialization APIs that are dangerous on any input ────────
        if _has(ins, "new BinaryFormatter", "new SoapFormatter", "new NetDataContractSerializer", "new LosFormatter",
                "new ObjectStateFormatter"):
            cx.add("SEC009", L, col, q, f"{c.callee[4:]} deserializes arbitrary types; Microsoft marks it unsafe "
                                         "for any untrusted data.", "medium",
                   ["no untrusted source traced to Deserialize(); the API itself is unsafe"], "api-use")
        if _has(ins, "XMLDecoder.readObject", "new XMLDecoder", "XStream.fromXML") or \
                (c.method == "readObject" and "objectinputstream" in
                 (ins.meta.get("rtype", "") + ins.meta.get("chain", "")).lower()):
            cx.add("SEC009", L, col, q, f"Java deserialization of a stream ({c.raw_callee}()).", "low",
                   ["no untrusted source traced to the stream; review where it comes from"], "api-use")
        if _has(ins, "enableDefaultTyping", "activateDefaultTyping"):
            cx.add("SEC009", L, col, q, "Jackson default typing lets the input choose the class to create.")
        # ── temp files, dangerous functions ─────────────────────────────
        if lang in ("c", "cpp") and c.callee in ("mktemp", "tmpnam", "tempnam", "_mktemp", "tmpnam_r"):
            cx.add("SEC037", L, col, q, f"{c.callee}() returns a name another process can create first.")
        if lang in ("c", "cpp") and c.callee in ("gets", "_getws", "getwd"):
            cx.add("SEC051", L, col, q, f"{c.callee}() cannot limit how much it writes; any input longer than "
                                         "the buffer overflows it.")
        if lang in ("c", "cpp") and c.callee in ("scanf", "fscanf", "sscanf", "wscanf"):
            k = 0 if c.callee in ("scanf", "wscanf") else 1
            fmt = _lit(ins, k)
            if fmt is not None and re.search(r"%(?!\d)(\[[^\]]*\]|s)", fmt):
                cx.add("SEC052", L, col, q, f"{c.callee}(\"{fmt}\") reads a string with no field width.")
        if lang in ("c", "cpp") and c.callee in ("strcpy", "strcat", "wcscpy", "wcscat", "sprintf", "vsprintf") \
                and len(c.args) >= 2:
            src_k = 1 if c.callee not in ("sprintf", "vsprintf") else None
            if src_k is not None and _lit(ins, src_k) is None and _is_fixed_array(info, c.args[0]):
                cx.add("SEC052", L, col, q, f"{c.callee}() into the fixed-size buffer '{c.args[0]}' does not check "
                                             "the source length.", "medium",
                       ["the source length is not known statically"])
            if src_k is None and "%s" in (_lit(ins, 1) or "") and _is_fixed_array(info, c.args[0]):
                cx.add("SEC052", L, col, q, f"{c.callee}() writes a %s string into the fixed-size buffer "
                                             f"'{c.args[0]}' without a length limit.", "medium",
                       ["the formatted length is not known statically"])
        # ── format string not a literal ─────────────────────────────────
        if lang in ("c", "cpp"):
            fmt_pos = {"printf": 0, "vprintf": 0, "wprintf": 0, "fprintf": 1, "vfprintf": 1, "sprintf": 1,
                       "vsprintf": 1, "snprintf": 2, "vsnprintf": 2, "syslog": 1, "dprintf": 1}.get(c.callee)
            if fmt_pos is not None and fmt_pos < len(c.args) and _lit(ins, fmt_pos) is None and \
                    not _is_literal_var(info, c.args[fmt_pos]):
                cx.add("SEC026", L, col, q, f"The format string of {c.callee}() is not a literal.", "medium",
                       ["no untrusted source traced to the format argument"])
        # ── secrets written to logs / output ────────────────────────────
        is_log = (c.method or "").lower() in ("info", "warn", "warning", "error", "debug", "trace", "fatal",
                                              "loginformation", "logwarning", "logerror", "logdebug", "logcritical") \
            and re.search(r"(?i)log", ins.meta.get("receiver_name", "") + ins.meta.get("chain", "")) \
            or c.callee in ("println!", "eprintln!", "info!", "warn!", "error!", "debug!", "log.info!",
                            "printf", "fprintf", "System.out.println", "Console.WriteLine")
        if is_log:
            for a in c.args:
                nm = _origin_name(info, a)
                if nm and _SENSITIVE.search(nm) and not _NOT_SENSITIVE.search(nm):
                    cx.add("SEC050", L, col, q, f"'{nm}' is written to {'the log' if 'print' not in c.callee else 'output'}.",
                           "medium", ["sensitivity inferred from the name"])
                    break
        # ── hard-coded credentials passed as arguments ──────────────────
        cred_pos = {"DriverManager.getConnection": 2, "mysql_real_connect": 3, "PQsetdbLogin": 6,
                    "new NetworkCredential": 1, "new PasswordAuthentication": 1}
        for name, k in cred_pos.items():
            if _has(ins, name) and k < len(c.args) and _lit(ins, k) and _secret_value(_lit(ins, k)):
                cx.add("SEC003", L, col, q, f"Hard-coded password passed to {name} ({_mask(_lit(ins, k))}).")
        for k in range(len(c.args)):
            v = _lit(ins, k) or ""
            if re.search(r"(?i)(password|pwd)\s*=\s*[^;'\"\s{]{3,}", v):
                cx.add("SEC003", L, col, q, "Connection string with an embedded password.")
                break
        # ── JWT, CORS, CSRF ─────────────────────────────────────────────
        if c.method == "parse" and re.search(r"Jwts\.parser|parserBuilder|JwtParser", ins.meta.get("chain", "")) \
                or _has(ins, "JWT.decode", "dangerous_insecure_decode", "insecure_decode",
                        "insecure_disable_signature_validation"):
            cx.add("SEC047", L, col, q, f"JWT decoded without verifying its signature ({c.raw_callee}()).")
        if c.method in ("AllowAnyOrigin",) or _has(ins, "Cors.permissive", "Cors.allow_any_origin") or \
                (c.method in ("allowedOrigins", "allowedOriginPatterns", "addAllowedOrigin", "WithOrigins")
                 and _lit(ins, 0) == "*"):
            cx.add("SEC046", L, col, q, f"CORS allows any origin ({c.raw_callee}).")
        if c.method == "disable" and re.search(r"csrf", ins.meta.get("chain", ""), re.I):
            cx.add("SEC045", L, col, q, "CSRF protection disabled (csrf().disable()).")
        if c.method == "csrf" and any("disable" in (cx.code(L)) for _ in [0]):
            cx.add("SEC045", L, col, q, "CSRF protection disabled.")
        if c.method == "permitAll" and re.search(r"anyRequest", ins.meta.get("chain", "")):
            cx.add("SEC061", L, col, q, "Every request is permitted without authentication (anyRequest().permitAll()).")
        if c.method == "UseDeveloperExceptionPage" and not any("IsDevelopment" in g for g in ins.guards):
            cx.add("SEC029", L, col, q, "Developer exception page enabled outside an IsDevelopment() check.",
                   "medium", ["the environment may be configured elsewhere"])
        # ── C# / Rust settings as named arguments or assignments ────────
        for kname, kop in c.keywords.items():
            val = _const_value(info, kop)
            if kname in ("Secure", "HttpOnly") and val == "false":
                cx.add("SEC044", L, col, q, f"Cookie created with {kname} = false.")
            if kname in ("ValidateIssuerSigningKey", "RequireSignedTokens", "RequireSignature") and val == "false":
                cx.add("SEC047", L, col, q, f"JWT validation with {kname} = false.")
            if kname == "DtdProcessing" and "Parse" in (_attr_chain(info, kop) or ""):
                cx.add("SEC018", L, col, q, "XML reader with DtdProcessing.Parse resolves external entities.")
            if kname == "XmlResolver" and "XmlUrlResolver" in (_callee_of(info, kop) or ""):
                cx.add("SEC018", L, col, q, "XmlResolver set to an XmlUrlResolver resolves external entities.")
            if kname in ("TypeNameHandling",) and re.search(r"\.(All|Auto|Objects|Arrays)$", _attr_chain(info, kop) or ""):
                cx.add("SEC009", L, col, q, f"Json.NET TypeNameHandling.{_attr_chain(info, kop).split('.')[-1]} lets "
                                             "the input choose the type to create.")
        if c.method in ("setSecure", "setHttpOnly") and _lit(ins, 0) == "false":
            cx.add("SEC044", L, col, q, f"Cookie {c.method}(false).")


class _StdView:
    """A call with its ``std::`` qualifier dropped (``std::printf`` is checked like ``printf``)."""

    def __init__(self, c):
        self._c = c
        self.callee = c.callee[4:]

    def __getattr__(self, k):
        return getattr(self._c, k)


def _def(info: FunctionInfo, op: Optional[str]):
    if not op:
        return None
    for i in info.fn.all_instructions():
        if i.result == op:
            return i
    return None


def _const_value(info, op) -> Optional[str]:
    d = _def(info, op)
    return d.meta.get("const") if d is not None and d.op == IROpcode.ASSIGN else None


def _const_name(info, op) -> str:
    """The identifier passed as an argument (e.g. SSL_VERIFY_NONE), or its chain for qualified names."""
    if op and not re.fullmatch(r"t\d+", op):
        return op
    d = _def(info, op)
    if d is not None and d.op == IROpcode.ATTR:
        return d.meta.get("attr", "")
    return ""


def _attr_chain(info, op) -> str:
    d = _def(info, op)
    return d.meta.get("chain", "") if d is not None and d.op == IROpcode.ATTR else ""


def _callee_of(info, op) -> str:
    d = _def(info, op)
    return d.call.callee if d is not None and d.op == IROpcode.CALL and d.call else ""


def _origin_name(info, op, depth: int = 0) -> str:
    """Name of the value an operand carries; for a concatenation, the first sensitive-looking part."""
    if op and not re.fullmatch(r"t\d+", op):
        return op
    d = _def(info, op)
    if d is None or depth > 6:
        return ""
    if d.op == IROpcode.ATTR:
        return d.meta.get("attr", "")
    if d.op in (IROpcode.BINOP, IROpcode.BUILD) and d.meta.get("kind") != "compare":
        names = [_origin_name(info, o, depth + 1) for o in d.operands]
        names = [n for n in names if n]
        hit = next((n for n in names if _SENSITIVE.search(n) and not _NOT_SENSITIVE.search(n)), None)
        return hit or (names[0] if names else "")
    return ""


def _is_fixed_array(info: FunctionInfo, op: str) -> bool:
    return bool(op) and info.var_types.get(op + "#array") == "1"


def _is_literal_var(info, op) -> bool:
    d = _def(info, op)
    return d is not None and d.op == IROpcode.ASSIGN and d.meta.get("kind") == "string"


def _security_context(info: FunctionInfo, ins) -> Optional[str]:
    if _SEC_CTX.search(info.fn.name):
        return f"function '{info.fn.name}'"
    # the variable the random value is assigned to
    for i in info.fn.all_instructions():
        if i.op == IROpcode.ASSIGN and i.operands and i.result and i.lineno == ins.lineno and \
                not re.fullmatch(r"t\d+", i.result) and _SEC_CTX.search(i.result):
            return f"variable '{i.result}'"
    return None


# ---------------------------------------------------------------------------
# assignments: hard-coded secrets, TLS callbacks, settings
# ---------------------------------------------------------------------------

def _assignments(cx: _Ctx, info: FunctionInfo) -> None:
    q = info.fn.qualname
    for ins in info.fn.all_instructions():
        if ins.op == IROpcode.ASSIGN and ins.result and ins.operands and not re.fullmatch(r"t\d+", ins.result):
            val = _const_value(info, ins.operands[0])
            if val is not None and _secret_name(ins.result) and _secret_value(val) and \
                    _def(info, ins.operands[0]).meta.get("kind") == "string":
                cx.add("SEC003", ins.lineno, ins.col, q,
                       f"Hard-coded secret assigned to '{ins.result}' (value {_mask(val)}).", "medium",
                       ["secret identified from the variable name and a non-placeholder string literal"])
        if ins.op == IROpcode.ASSIGN and ins.meta.get("kind") == "string" and                 re.search(r"(?i)\b(password|pwd)\s*=\s*[^;'\"\s{]{3,}", ins.meta.get("const", "")):
            cx.add("SEC003", ins.lineno, ins.col, q, "Connection string with an embedded password.")
        if ins.op == IROpcode.STORE:
            target = ins.meta.get("target", "")
            attr = ins.meta.get("attr", "")
            val = _const_value(info, ins.operands[0]) if ins.operands else None
            if attr in ("ServerCertificateValidationCallback", "ServerCertificateCustomValidationCallback",
                        "RemoteCertificateValidationCallback") and \
                    re.search(r"=>\s*true|DangerousAcceptAnyServerCertificateValidator", cx.code(ins.lineno)):
                cx.add("SEC031", ins.lineno, ins.col, q, f"{attr} accepts every certificate.")
            if attr in ("Secure", "HttpOnly") and val == "false":
                cx.add("SEC044", ins.lineno, ins.col, q, f"Cookie {attr} = false.")
            if attr in ("ValidateIssuerSigningKey", "RequireSignedTokens", "RequireSignature") and val == "false":
                cx.add("SEC047", ins.lineno, ins.col, q, f"JWT validation with {attr} = false.")
            if attr == "DtdProcessing" and "Parse" in cx.code(ins.lineno):
                cx.add("SEC018", ins.lineno, ins.col, q, "DtdProcessing.Parse resolves external entities.")
            if attr == "XmlResolver" and "XmlUrlResolver" in cx.code(ins.lineno):
                cx.add("SEC018", ins.lineno, ins.col, q, "XmlResolver set to an XmlUrlResolver resolves external entities.")
            if attr == "TypeNameHandling" and re.search(r"TypeNameHandling\.(All|Auto|Objects|Arrays)", cx.code(ins.lineno)):
                cx.add("SEC009", ins.lineno, ins.col, q, "Json.NET TypeNameHandling lets the input choose the type.")
            if attr in ("Mode",) and "CipherMode.ECB" in cx.code(ins.lineno):
                cx.add("SEC034", ins.lineno, ins.col, q, "CipherMode.ECB.")
            if attr == "SslProtocols" and re.search(r"SslProtocols\.(Ssl2|Ssl3|Tls|Tls11)\b", cx.code(ins.lineno)):
                cx.add("SEC032", ins.lineno, ins.col, q, "Insecure SSL/TLS protocol version.")
            if attr in ("IV", "Key") and re.search(r"GetBytes\(\s*\"|new\s+byte\s*\[\s*\]\s*\{", cx.code(ins.lineno)):
                cx.add("SEC036", ins.lineno, ins.col, q, f"Static {attr} (a constant byte array).", "medium")
        if ins.op == IROpcode.ATTR and ins.meta.get("chain", "").endswith("CipherMode.ECB"):
            cx.add("SEC034", ins.lineno, ins.col, q, "CipherMode.ECB.")
        if ins.op == IROpcode.ATTR and re.search(r"SslProtocols\.(Ssl2|Ssl3|Tls|Tls11)$", ins.meta.get("chain", "")):
            cx.add("SEC032", ins.lineno, ins.col, q, f"Insecure protocol {ins.meta.get('chain')}.")


# ---------------------------------------------------------------------------
# XXE: Java parser factories without hardening in the same function
# ---------------------------------------------------------------------------
_JAVA_XML_FACTORIES = ("DocumentBuilderFactory.newInstance", "SAXParserFactory.newInstance",
                       "XMLInputFactory.newInstance", "XMLInputFactory.newFactory", "TransformerFactory.newInstance",
                       "SchemaFactory.newInstance", "new SAXReader", "new SAXBuilder", "XMLReaderFactory.createXMLReader")
_HARDENING = re.compile(r"disallow-doctype-decl|external-general-entities|external-parameter-entities|"
                        r"ACCESS_EXTERNAL_DTD|ACCESS_EXTERNAL_SCHEMA|FEATURE_SECURE_PROCESSING|"
                        r"setExpandEntityReferences\s*\(\s*false|IS_SUPPORTING_EXTERNAL_ENTITIES|SUPPORT_DTD|"
                        r"load-external-dtd")


def _xxe_java(cx: _Ctx, info: FunctionInfo) -> None:
    body = text(info.node, cx.src)
    if _HARDENING.search(body):
        return
    for ins in _calls(info):
        if _has(ins, *_JAVA_XML_FACTORIES):
            cx.add("SEC018", ins.lineno, ins.col, info.fn.qualname,
                   f"{ins.call.raw_callee}() is used without disabling DOCTYPEs / external entities "
                   "(the Java default resolves them).", "medium",
                   ["hardening may be applied in another method that configures the factory"])


def _xxe_c(cx: _Ctx, info: FunctionInfo) -> None:
    for ins in _calls(info):
        if ins.call.callee in ("xmlReadFile", "xmlReadMemory", "xmlCtxtReadFile", "xmlCtxtReadMemory",
                               "xmlReadDoc", "xmlCtxtUseOptions") and "XML_PARSE_NOENT" in cx.code(ins.lineno):
            cx.add("SEC018", ins.lineno, ins.col, info.fn.qualname,
                   "libxml2 parse with XML_PARSE_NOENT substitutes external entities.")


# ---------------------------------------------------------------------------
# syntax-tree checks: empty catch, TLS trust managers, unsafe code, races, auth
# ---------------------------------------------------------------------------

def _tree_checks(cx: _Ctx, info: FunctionInfo) -> None:
    q, node, lang = info.fn.qualname, info.node, cx.lang
    stack = [node]
    unsafe_depth_nodes = []
    while stack:
        n = stack.pop()
        t = n.type
        if t == "catch_clause":
            body = fld(n, "body") or (named(n)[-1] if named(n) else None)
            if body is not None and body.type in ("block", "compound_statement") and not named(body):
                cx.add("SEC049", n.start_point[0] + 1, n.start_point[1], q,
                       "Empty catch block discards the exception.", "medium",
                       ["ignoring this exception may be intentional"])
        if t in ("unsafe_block",) or (lang == "csharp" and t == "unsafe_statement"):
            unsafe_depth_nodes.append(n)
        stack.extend(named(n))
    # unsafe operations (Rust; C# unsafe blocks)
    if lang in ("rust", "csharp"):
        unsafe_fn = "unsafe" in info.modifiers or text(info.node, cx.src).lstrip().startswith(("unsafe ", "pub unsafe "))
        regions = [(u.start_point[0] + 1, u.end_point[0] + 1) for u in unsafe_depth_nodes]
        if unsafe_fn:
            regions.append((info.fn.source_lineno, info.fn.end_lineno))
        for ins in info.fn.all_instructions():
            if not any(a <= ins.lineno <= b for a, b in regions):
                continue
            what = None
            if ins.op == IROpcode.UNOP and ins.meta.get("operator") == "*":
                what = "raw pointer dereference"
            elif ins.op == IROpcode.STORE and ins.meta.get("kind") == "deref":
                what = "write through a raw pointer"
            elif ins.op == IROpcode.CALL and ins.call:
                nm = ins.meta.get("chain", "") + " " + ins.call.callee
                for api, desc in (("transmute", "mem::transmute"), ("from_raw_parts", "slice::from_raw_parts"),
                                  ("set_len", "Vec::set_len"), ("get_unchecked", "get_unchecked (no bounds check)"),
                                  ("from_utf8_unchecked", "from_utf8_unchecked"), ("ptr.read", "ptr::read"),
                                  ("ptr.write", "ptr::write"), ("copy_nonoverlapping", "ptr::copy_nonoverlapping"),
                                  ("Box.from_raw", "Box::from_raw"), ("mem.uninitialized", "mem::uninitialized"),
                                  ("offset", "pointer offset"), ("stackalloc", "stackalloc")):
                    if api in nm:
                        what = desc
                        break
            if what:
                cx.add("SEC060", ins.lineno, ins.col, q, f"Unsafe code: {what}.", "medium",
                       ["memory safety depends on invariants the compiler cannot check"])
    # TOCTOU
    checks = {}
    for ins in _calls(info):
        c = ins.call
        subj = None
        if lang in ("c", "cpp") and c.callee in ("access", "stat", "lstat", "_access", "faccessat") and c.args:
            subj = c.args[0]
        elif c.method in ("exists", "isFile", "isDirectory", "canWrite", "canRead", "try_exists", "is_file") and c.receiver:
            subj = c.receiver
        elif _has(ins, "Files.exists", "Files.notExists", "File.Exists", "Directory.Exists", "Files.isRegularFile",
                  "fs.metadata", "Path.new.exists") and c.args:
            subj = c.args[0]
        if subj and not re.fullmatch(r"t\d+", subj):
            checks.setdefault(subj, ins)
            continue
        use = None
        if lang in ("c", "cpp") and c.callee in ("open", "fopen", "creat", "unlink", "remove", "chmod", "chown",
                                                  "rename", "truncate", "freopen") and c.args:
            use = c.args[0]
        elif c.callee.startswith("new File") and c.callee.split(" ")[1] in ("FileOutputStream", "FileWriter",
                                                                              "FileInputStream", "RandomAccessFile") and c.args:
            use = c.args[0]
        elif c.method in ("createNewFile", "delete", "mkdir", "renameTo") and c.receiver:
            use = c.receiver
        elif _has(ins, "Files.write", "Files.delete", "Files.createFile", "Files.newOutputStream", "File.Open",
                  "File.Create", "File.WriteAllText", "File.Delete", "File.OpenWrite", "File.WriteAllBytes",
                  "File.create", "File.open", "fs.remove_file", "fs.write", "OpenOptions.open") and c.args:
            use = c.args[0]
        if use and use in checks and checks[use].uid < ins.uid:
            chk = checks[use]
            cx.add("SEC059", ins.lineno, ins.col, q,
                   f"'{use}' is checked on line {chk.lineno} ({chk.call.raw_callee}) and used here; another process "
                   "can replace the file in between.", "medium",
                   ["the file system location may not be shared with other users"])


def _class_level(cx: _Ctx, mod: LoweredModule) -> None:
    """Servlet / controller fields written per request; static mut in Rust; authorization attributes."""
    src = cx.src
    for info in mod.functions.values():
        q = info.fn.qualname
        ann = " ".join(info.annotations)
        cls_ann = " ".join(info.class_annotations)
        # C#: [AllowAnonymous] on a state-changing action
        if cx.lang == "csharp" and "AllowAnonymous" in ann and re.search(r"Http(Post|Put|Delete|Patch)", ann):
            cx.add("SEC061", info.name_line or info.fn.source_lineno, 0, q,
                   f"State-changing action {info.fn.name}() allows anonymous access ([AllowAnonymous]).")
        # Java: @PermitAll on a state-changing mapping
        if cx.lang == "java" and "@PermitAll" in ann and re.search(r"@(Post|Put|Delete|Patch)Mapping", ann):
            cx.add("SEC061", info.name_line or info.fn.source_lineno, 0, q,
                   f"State-changing endpoint {info.fn.name}() is annotated @PermitAll.")
        # CSRF opt-out on an action
        if cx.lang == "csharp" and "IgnoreAntiforgeryToken" in ann:
            cx.add("SEC045", info.name_line or info.fn.source_lineno, 0, q, f"{info.fn.name}() opts out of anti-forgery validation.")
        if cx.lang == "java" and re.search(r"@CrossOrigin(\s*$|\(\s*\)|\(.*origins\s*=\s*\"\*\")", ann + " " + cls_ann):
            cx.add("SEC046", info.name_line or info.fn.source_lineno, 0, q, "@CrossOrigin allows any origin.")
    # shared mutable state
    if cx.lang == "java":
        _java_fields(cx, mod)
    if cx.lang == "csharp":
        _csharp_static(cx, mod)
    if cx.lang == "rust":
        root = mod.tree.root_node
        statics = set()
        for n in _walk(root):
            if n.type == "static_item" and "mut" in text(n, src).split("=")[0]:
                nm = fld(n, "name")
                if nm is not None:
                    statics.add(text(nm, src))
        for info in mod.functions.values():
            for ins in info.fn.all_instructions():
                if ins.op == IROpcode.STORE and ins.meta.get("base_name") in statics or \
                        ins.op == IROpcode.ASSIGN and ins.result in statics:
                    nm = ins.meta.get("base_name") or ins.result
                    cx.add("SEC063", ins.lineno, ins.col, info.fn.qualname,
                           f"Write to `static mut {nm}`: a data race if more than one thread runs this code.")


def _walk(node):
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)


def _java_fields(cx: _Ctx, mod: LoweredModule) -> None:
    src = cx.src
    for n in _walk(mod.tree.root_node):
        if n.type != "class_declaration":
            continue
        head = text(n, src).split("{", 1)[0]
        mods = " ".join(text(c, src) for c in n.children if c.type == "modifiers")
        shared = re.search(r"extends\s+(HttpServlet|GenericServlet)", head) or \
            re.search(r"@(RestController|Controller|Service|Component)\b", mods)
        if not shared:
            continue
        body = fld(n, "body")
        fields = set()
        for f in named(body) if body is not None else []:
            if f.type == "field_declaration":
                fm = " ".join(text(c, src) for c in f.children if c.type == "modifiers")
                if "final" in fm or "static" in fm:
                    continue
                for d in named(f):
                    if d.type == "variable_declarator":
                        nm = fld(d, "name")
                        if nm is not None:
                            fields.add(text(nm, src))
        cname = text(fld(n, "name"), src)
        for info in mod.functions.values():
            if info.fn.class_name != cname or info.fn.name in ("<init>", cname, "init"):
                continue
            for ins in info.fn.all_instructions():
                target = None
                if ins.op == IROpcode.ASSIGN and ins.result in fields and ins.meta.get("kind") != "param" and \
                        ins.result not in info.fn.params and ins.result not in info.var_types:
                    target = ins.result
                elif ins.op == IROpcode.STORE and ins.meta.get("base_name") in ("this",) and \
                        ins.meta.get("attr") in fields:
                    target = ins.meta.get("attr")
                if target:
                    cx.add("SEC063", ins.lineno, ins.col, info.fn.qualname,
                           f"Field '{target}' of the shared {('servlet' if 'Servlet' in head else 'singleton bean')} "
                           f"{cname} is written while handling a request; concurrent requests overwrite each other.")


def _csharp_static(cx: _Ctx, mod: LoweredModule) -> None:
    src = cx.src
    for n in _walk(mod.tree.root_node):
        if n.type != "class_declaration":
            continue
        cname = text(fld(n, "name"), src)
        statics = set()
        body = fld(n, "body")
        for f in named(body) if body is not None else []:
            if f.type == "field_declaration":
                ftxt = text(f, src)
                if re.search(r"\bstatic\b", ftxt) and not re.search(r"\b(readonly|const)\b", ftxt):
                    for d in _walk(f):
                        if d.type == "variable_declarator":
                            nm = fld(d, "name") or next((c for c in named(d) if c.type == "identifier"), None)
                            if nm is not None:
                                statics.add(text(nm, src))
        if not statics or not cname.endswith("Controller"):
            continue
        for info in mod.functions.values():
            if info.fn.class_name != cname:
                continue
            body_txt = text(info.node, src)
            if re.search(r"\block\s*\(|Interlocked\.", body_txt):
                continue
            for ins in info.fn.all_instructions():
                if ins.op == IROpcode.ASSIGN and ins.result in statics and ins.result not in info.var_types:
                    cx.add("SEC063", ins.lineno, ins.col, info.fn.qualname,
                           f"Static field '{ins.result}' is written by a controller action without a lock; "
                           "concurrent requests race on it.")


def run_patterns(mod: LoweredModule) -> List[Raw]:
    cx = _Ctx(mod)
    for info in mod.functions.values():
        _crypto_and_misc(cx, info)
        _assignments(cx, info)
        _tree_checks(cx, info)
        if cx.lang == "java":
            _xxe_java(cx, info)
        if cx.lang in ("c", "cpp"):
            _xxe_c(cx, info)
    _class_level(cx, mod)
    # literals that look like real keys anywhere in the file
    for i, line in enumerate(cx.lines, 1):
        for label, pat in _KNOWN_FORMATS:
            if pat.search(line):
                cx.add("SEC003", i, 0, _function_at(mod, i), f"String literal contains a {label}.", "high",
                       [f"value matches the {label} format"])
                break
    return cx.out


def _function_at(mod: LoweredModule, line: int) -> str:
    best = "<module>"
    for info in mod.functions.values():
        if info.fn.source_lineno <= line <= info.fn.end_lineno:
            best = info.fn.qualname
    return best
