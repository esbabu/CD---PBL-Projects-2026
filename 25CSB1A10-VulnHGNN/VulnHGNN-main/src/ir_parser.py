import re
import json
import os

def parse_ll_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    source_file = _extract_source_file(lines)
    debug_files, debug_functions = _extract_debug_metadata(lines)
    functions   = _extract_functions(lines, debug_functions)

    return {
        "source_file": source_file,
        "functions":   functions,
    }

def _extract_source_file(lines):
    for line in lines:
        if line.startswith("source_filename"):
            match = re.search(r'"((?:\\.|[^"\\])*)"', line)
            if match:
                return _decode_llvm_string(match.group(1))
    return ""


def _decode_llvm_string(value):
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value


def _extract_debug_metadata(lines):
    debug_files = {}
    debug_functions = {}

    for line in lines:
        file_match = re.search(
            r'!(\d+)\s*=\s*!DIFile\(filename:\s*"((?:\\.|[^"\\])*)",'
            r'\s*directory:\s*"((?:\\.|[^"\\])*)"',
            line,
        )
        if file_match:
            file_id, filename, directory = file_match.groups()
            filename = _decode_llvm_string(filename)
            directory = _decode_llvm_string(directory)
            debug_files[file_id] = os.path.normpath(
                os.path.join(directory, filename) if directory else filename
            )

    for line in lines:
        subprogram_match = re.search(
            r'!(\d+)\s*=\s*(?:distinct\s+)?!DISubprogram\((.*)\)',
            line,
        )
        if subprogram_match:
            subprogram_id, metadata = subprogram_match.groups()
            file_match = re.search(r'\bfile:\s*!(\d+)', metadata)
            if file_match:
                file_id = file_match.group(1)
                debug_functions[subprogram_id] = debug_files.get(file_id)

    return debug_files, debug_functions


def filter_functions_to_source(ir_data):
    """Keep functions whose debug source location belongs to this input file."""
    source_file = ir_data.get("source_file")
    functions = ir_data.get("functions", [])
    if not source_file or not any(func.get("source_file") for func in functions):
        return ir_data

    source_path = os.path.normcase(os.path.abspath(os.path.normpath(source_file)))
    filtered = {
        **ir_data,
        "functions": [
            func for func in functions
            if func.get("source_file")
            and os.path.normcase(
                os.path.abspath(os.path.normpath(func["source_file"]))
            ) == source_path
        ],
        "source_filter_applied": True,
    }
    return filtered



_DEFINE_RE = re.compile(
    r'^define\s+'            # keyword
    r'(?:[\w]+\s+)*'        # optional qualifiers 
    r'([\w\*]+)\s+'         #return type
    r'@([\w\.\$]+)\s*'      #function name
    r'\((.*?)\)'             #parameter list
, re.IGNORECASE)

_DECLARE_RE = re.compile(
    r'^declare\s+'
    r'(?:[\w]+\s+)*'        # optional qualifiers
    r'([\w\*]+)\s+'         # return type
    r'@([\w\.\$]+)\s*'
    r'\((.*?)\)'
, re.IGNORECASE)

_BLOCK_LABEL_RE = re.compile(r'^(\d+|[\w\.]+):\s*(?:;.*)?$')

def _extract_functions(lines, debug_functions=None):
    functions = []
    i = 0
    debug_functions = debug_functions or {}

    while i < len(lines):
        line = lines[i].strip()
        m = _DECLARE_RE.match(line)
        if m:
            ret_type   = m.group(1)
            func_name  = m.group(2)
            params_raw = m.group(3)
            functions.append({
                "name":           func_name,
                "return_type":    ret_type,
                "params":         _parse_params(params_raw),
                "is_declaration": True,
                "blocks":         [],   # declarations have no body
            })
            i += 1
            continue

        m = _DEFINE_RE.match(line)
        if m:
            ret_type   = m.group(1)
            func_name  = m.group(2)
            params_raw = m.group(3)
            debug_match = re.search(r'!dbg\s+!(\d+)', line)
            source_file = (
                debug_functions.get(debug_match.group(1))
                if debug_match else None
            )

            #collect the body lines until the closing '}'
            body_lines = []
            i += 1
            while i < len(lines):
                body_line = lines[i].rstrip('\n').rstrip('\r')
                if body_line.strip() == '}':
                    i += 1   # consume the closing brace
                    break
                body_lines.append(body_line)
                i += 1

            blocks = _extract_blocks(body_lines)
            functions.append({
                "name":           func_name,
                "return_type":    ret_type,
                "params":         _parse_params(params_raw),
                "is_declaration": False,
                "blocks":         blocks,
                "source_file":    source_file,
            })
            continue

        i += 1

    return functions


def _parse_params(raw):
    raw = raw.strip()
    if not raw or raw == "...":
        return []

    params = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        clean_tokens = [t for t in tokens if t not in ("noundef", "signext", "zeroext")]
        params.append(" ".join(clean_tokens))

    return params

def _extract_blocks(body_lines):
    blocks = []
    current_label = "entry"
    current_instructions = []

    for raw_line in body_lines:
        line = raw_line.strip()

        if not line or line.startswith(";"):
            continue

        m = _BLOCK_LABEL_RE.match(line)
        if m:
            if current_instructions:
                blocks.append({
                    "label":        current_label,
                    "instructions": current_instructions,
                })
            current_label = m.group(1)
            current_instructions = []
        else:
            instruction = _parse_instruction(line)
            if instruction:
                current_instructions.append(instruction)

    if current_instructions:
        blocks.append({
            "label":        current_label,
            "instructions": current_instructions,
        })

    return blocks

_KNOWN_OPCODES = {
    "alloca", "store", "load", "br", "ret", "call", "icmp", "fcmp",
    "add", "fadd", "sub", "fsub", "mul", "fmul", "udiv", "sdiv", "fdiv",
    "urem", "srem", "frem", "shl", "lshr", "ashr", "and", "or", "xor",
    "getelementptr", "gep",
    "trunc", "zext", "sext", "fptrunc", "fpext", "fptoui", "fptosi",
    "uitofp", "sitofp", "ptrtoint", "inttoptr", "bitcast",
    "phi", "select", "switch", "unreachable", "resume",
    "extractvalue", "insertvalue", "extractelement", "insertelement",
    "shufflevector", "landingpad", "invoke",
}


def _parse_instruction(raw_line):
    text = re.sub(r',\s*!(?:dbg|llvm\.\w+)\s*![0-9]+', '', raw_line).strip()
    text = re.sub(r',\s*metadata\s+![0-9]+', '', text).strip()

    if not text:
        return None
    opcode = _identify_opcode(text)

    return {
        "text":   text,
        "opcode": opcode,
    }


def _identify_opcode(text):
    if "=" in text:
        rhs = text.split("=", 1)[1].strip()
        first_word = rhs.split()[0] if rhs else ""
    else:
        first_word = text.split()[0] if text else ""

    first_word = first_word.split("(")[0]   # handle cases like 'call('

    if first_word in _KNOWN_OPCODES:
        return first_word

    return first_word if first_word else "unknown"
