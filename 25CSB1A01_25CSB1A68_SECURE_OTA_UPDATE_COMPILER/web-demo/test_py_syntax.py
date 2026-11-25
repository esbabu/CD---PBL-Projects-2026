import re, difflib, ast

py_code = """
dfe updateFirmware(dev: DeviceState, pkg: OtaPackage) -> UpdateStatus
    if not pkg
        retun UpdateStatus.ERR_INVALID_PACKGE

    if not verifySignature(pkg, dev.public_key_pem
        retun UpdateStatus.ERR_SIGNATURE_INVALID

    if pkg.verison <= dev.currnet_version
        retun UpdateStatus.ERR_VERSION_ROLLBACK_BLOCKD

    install(pkg, dev.master_key)
    dev.current_version = pkg.version
    dev.pending_slot = dev.boot_slot ^ 1
    retun UpdateStatus.OTA_UPDATE_SUCCESS
"""

def remediate_python_syntax_errors(code: str, raw_output: str = "") -> str:
    # 1. Keyword typos
    typos = [
        (r'\b(?:dfe|deff)\s+', 'def '),
        (r'\b(?:calss|clas)\s+', 'class '),
        (r'\b(?:improt|importt)\b', 'import'),
        (r'\bform\s+([a-zA-Z0-9_\.]+)\s+import\b', r'from \1 import'),
        (r'\b(?:retun|retrun|retunr)\b', 'return'),
        (r'\b(?:whlie|wihle)\b', 'while'),
        (r'\b(?:flase|Flase)\b', 'False'),
        (r'\b(?:ture|Ture)\b', 'True'),
        (r'\b(?:elsif|eilf)\b', 'elif'),
    ]
    for pat, rep in typos:
        code = re.sub(pat, rep, code)

    # 2. Symbol and attribute fuzzy repair
    known_symbols = [
        'OtaPackage', 'DeviceState', 'UpdateStatus',
        'verifySignature', 'sourceTrusted', 'verifyImageHash', 'decryptPayloadAesGcm', 'install', 'updateFirmware',
        'verify_signature', 'source_trusted', 'verify_image_hash', 'decrypt_payload_aes_gcm', 'update_firmware',
        'public_key_pem', 'master_key', 'current_version', 'boot_slot', 'pending_slot', 'version', 'ciphertext',
        'OTA_UPDATE_SUCCESS', 'ERR_INVALID_PACKAGE', 'ERR_SIGNATURE_INVALID', 'ERR_SOURCE_UNTRUSTED',
        'ERR_IMAGE_HASH_INVALID', 'ERR_DECRYPTION_FAILED', 'ERR_VERSION_ROLLBACK_BLOCKED'
    ]

    # Fuzzy match attributes (e.g. .verison -> .version, .currnet_version -> .current_version)
    for m in re.finditer(r'\.([a-zA-Z_]\w*)', code):
        tok = m.group(1)
        if tok not in known_symbols:
            close = difflib.get_close_matches(tok, known_symbols, n=1, cutoff=0.6)
            if close and close[0] != tok:
                code = re.sub(rf'\.{re.escape(tok)}\b', f'.{close[0]}', code)

    # 3. Line by line balance parentheses and missing colons
    lines = code.splitlines()
    for i, line in enumerate(lines):
        s = line.rstrip()
        trimmed = s.strip()
        if not trimmed or trimmed.startswith('#'):
            continue

        # Balance unclosed parentheses on conditional / definition statements
        if trimmed.count('(') > trimmed.count(')'):
            diff = trimmed.count('(') - trimmed.count(')')
            if s.endswith(':'):
                s = s[:-1].rstrip() + (')' * diff) + ':'
            else:
                s = s + (')' * diff)
            lines[i] = s
            trimmed = s.strip()

        # Accidental assignment '=' in if/elif/while
        if re.match(r'^(?:if|elif|while)\b', trimmed):
            # replace isolated '=' not part of '==', '<=', '>=', '!='
            s = re.sub(r'(?<![=!<>+\-*/&|^])=(?![=])', '==', s)
            lines[i] = s
            trimmed = s.strip()

        # Missing colon on compound statements
        compound_keywords = ('def ', 'class ', 'if ', 'elif ', 'else', 'while ', 'for ', 'try', 'except', 'finally')
        if any(trimmed == kw or trimmed.startswith(kw) for kw in compound_keywords):
            # Strip comments
            m_comm = re.search(r'#.*$', s)
            code_part = s[:m_comm.start()].rstrip() if m_comm else s
            comm_part = s[m_comm.start():] if m_comm else ''
            if not code_part.endswith(':'):
                lines[i] = code_part + ':' + comm_part

    repaired = '\n'.join(lines)
    return repaired

fixed = remediate_python_syntax_errors(py_code)
print("FIXED CODE:\n", fixed)

# Test AST parse
try:
    ast.parse(fixed)
    print("SUCCESS: AST parsed cleanly without any SyntaxError!")
except SyntaxError as e:
    print(f"FAILED to parse at line {e.lineno}: {e.msg}")
