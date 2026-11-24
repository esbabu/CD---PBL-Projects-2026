"""
healer.py — Rule-based self-healing module for C/C++ vulnerability remediation.

Applies targeted, CWE-specific code transformations to patch detected vulnerabilities.
Supported CWEs:
  - CWE-190: Integer Overflow  → safe arithmetic with overflow checks
  - CWE-191: Integer Underflow → safe subtraction with underflow guards
  - CWE-369: Divide by Zero    → zero-divisor guards before division
  - CWE-476: NULL Pointer Deref → NULL checks after malloc/calloc/realloc
"""

import re


# ─── CWE-369: Division by Zero ───────────────────────────────────────────────

def _heal_cwe369(code: str) -> str:
    """
    Finds unguarded division operations and wraps them in a zero-check.
    Handles both '/' and '%' operators on integer or float types.
    """
    lines = code.split('\n')
    healed = []
    i = 0

    # Pattern: something = expr / divisor;  or  expr / divisor (standalone)
    # We look for lines with / or % where the divisor is a variable
    div_pattern = re.compile(
        r'^(\s*)'                          # leading whitespace
        r'(.+?)'                           # LHS (e.g., "return (float)sum")
        r'\s*([/%])\s*'                    # operator
        r'(\w+)'                           # divisor variable name
        r'\s*;'                            # semicolon
    )

    while i < len(lines):
        line = lines[i]
        m = div_pattern.match(line)

        if m:
            indent = m.group(1)
            lhs = m.group(2).strip()
            op = m.group(3)
            divisor = m.group(4)

            # If divisor is numeric literal, heal only if it is literal 0
            if re.match(r'^\d+$', divisor):
                if divisor == '0':
                    fixed_line = re.sub(r'([/%])\s*0\b', r'\g<1> 1 /* HEALED: literal zero divisor replaced */', line)
                    healed.append(fixed_line)
                    i += 1
                    continue
                else:
                    healed.append(line)
                    i += 1
                    continue

            # Check if there's already a guard (look 1-3 lines above)
            already_guarded = False
            for back in range(1, min(4, i + 1)):
                prev = lines[i - back]
                if divisor in prev and ('!= 0' in prev or '> 0' in prev or '== 0' in prev):
                    already_guarded = True
                    break

            if already_guarded:
                healed.append(line)
            else:
                # Determine return type for the fallback value
                # If lhs contains "return", use return with a safe default
                if 'return' in lhs:
                    healed.append(f'{indent}if ({divisor} == 0) {{')
                    healed.append(f'{indent}    fprintf(stderr, "[HEALED] Division by zero prevented for \\"{divisor}\\"\\n");')
                    healed.append(f'{indent}    return 0; /* HEALED: CWE-369 zero-divisor guard */')
                    healed.append(f'{indent}}}')
                    healed.append(line)
                else:
                    healed.append(f'{indent}if ({divisor} == 0) {{')
                    healed.append(f'{indent}    fprintf(stderr, "[HEALED] Division by zero prevented for \\"{divisor}\\"\\n");')
                    healed.append(f'{indent}    {divisor} = 1; /* HEALED: CWE-369 safe fallback divisor */')
                    healed.append(f'{indent}}}')
                    healed.append(line)
        else:
            healed.append(line)

        i += 1

    return '\n'.join(healed)


# ─── CWE-476: NULL Pointer Dereference ───────────────────────────────────────

def _heal_cwe476(code: str) -> str:
    """
    Finds malloc/calloc/realloc calls where the returned pointer is used
    without a NULL check, and inserts one.
    """
    lines = code.split('\n')
    healed = []
    i = 0

    # Pattern: Type *ptr = (Type *)malloc(...)   or   ptr = malloc(...)
    alloc_pattern = re.compile(
        r'^(\s*)'                                # indent
        r'(?:\w[\w\s\*]*\s+)?'                   # optional type decl
        r'(\*?\w+)'                              # pointer variable name
        r'\s*=\s*'                                # assignment
        r'(?:\([^)]*\)\s*)?'                      # optional cast
        r'(malloc|calloc|realloc)\s*\('           # allocator call
    )

    while i < len(lines):
        line = lines[i]
        m = alloc_pattern.match(line)

        if m:
            indent = m.group(1)
            ptr_name = m.group(2).lstrip('*')
            
            # Check if there's already a NULL check within the next 3 lines
            already_guarded = False
            for ahead in range(1, min(4, len(lines) - i)):
                future = lines[i + ahead]
                if ptr_name in future and ('== NULL' in future or '!= NULL' in future or f'!{ptr_name}' in future or f'if ({ptr_name})' in future):
                    already_guarded = True
                    break

            healed.append(line)

            if not already_guarded:
                healed.append(f'{indent}if ({ptr_name} == NULL) {{ /* HEALED: CWE-476 NULL guard */')
                healed.append(f'{indent}    fprintf(stderr, "[HEALED] NULL pointer caught for \\"{ptr_name}\\"\\n");')
                healed.append(f'{indent}    return; /* or return NULL / return -1 as appropriate */')
                healed.append(f'{indent}}}')
        else:
            healed.append(line)

        i += 1

    return '\n'.join(healed)


# ─── CWE-190: Integer Overflow ──────────────────────────────────────────────

def _heal_cwe190(code: str) -> str:
    """
    Finds integer multiplication and addition patterns that could overflow,
    and wraps them in safe overflow-checking guards.
    """
    lines = code.split('\n')
    healed = []
    i = 0

    # Pattern: int var = a * b;  or  int var = a + b;
    arith_pattern = re.compile(
        r'^(\s*)'                       # indent
        r'((?:unsigned\s+)?(?:int|long|short|size_t)\s+)'  # type
        r'(\w+)'                        # result variable
        r'\s*=\s*'                      # =
        r'(\w+)'                        # operand a
        r'\s*([+*])\s*'                # operator
        r'(\w+)'                        # operand b
        r'\s*;'
    )

    while i < len(lines):
        line = lines[i]
        m = arith_pattern.match(line)

        if m:
            indent = m.group(1)
            type_str = m.group(2).strip()
            result = m.group(3)
            op_a = m.group(4)
            operator = m.group(5)
            op_b = m.group(6)

            # Skip if operands are numeric literals
            if re.match(r'^\d+$', op_a) and re.match(r'^\d+$', op_b):
                healed.append(line)
                i += 1
                continue

            if operator == '*':
                healed.append(f'{indent}/* HEALED: CWE-190 overflow guard for {op_a} * {op_b} */')
                healed.append(f'{indent}{type_str} {result} = 0;')
                healed.append(f'{indent}if ({op_a} != 0 && {op_b} > __INT_MAX__ / {op_a}) {{')
                healed.append(f'{indent}    fprintf(stderr, "[HEALED] Integer overflow prevented in {op_a} * {op_b}\\n");')
                healed.append(f'{indent}    {result} = __INT_MAX__;')
                healed.append(f'{indent}}} else {{')
                healed.append(f'{indent}    {result} = {op_a} * {op_b};')
                healed.append(f'{indent}}}')
            elif operator == '+':
                healed.append(f'{indent}/* HEALED: CWE-190 overflow guard for {op_a} + {op_b} */')
                healed.append(f'{indent}{type_str} {result} = 0;')
                healed.append(f'{indent}if ({op_a} > __INT_MAX__ - {op_b}) {{')
                healed.append(f'{indent}    fprintf(stderr, "[HEALED] Integer overflow prevented in {op_a} + {op_b}\\n");')
                healed.append(f'{indent}    {result} = __INT_MAX__;')
                healed.append(f'{indent}}} else {{')
                healed.append(f'{indent}    {result} = {op_a} + {op_b};')
                healed.append(f'{indent}}}')
        else:
            healed.append(line)

        i += 1

    return '\n'.join(healed)


# ─── CWE-191: Integer Underflow ──────────────────────────────────────────────

def _heal_cwe191(code: str) -> str:
    """
    Finds integer subtraction patterns that could underflow,
    and wraps them in underflow-checking guards.
    """
    lines = code.split('\n')
    healed = []
    i = 0

    # Pattern: type var = a - b;
    sub_pattern = re.compile(
        r'^(\s*)'
        r'((?:unsigned\s+)?(?:int|long|short|size_t)\s+)'
        r'(\w+)'
        r'\s*=\s*'
        r'(?:\([^)]*\)\s*)?'           # optional cast
        r'(\w+)'
        r'\s*-\s*'
        r'(?:\([^)]*\)\s*)?'           # optional cast
        r'(\w+)'
        r'\s*;'
    )

    while i < len(lines):
        line = lines[i]
        m = sub_pattern.match(line)

        if m:
            indent = m.group(1)
            type_str = m.group(2).strip()
            result = m.group(3)
            op_a = m.group(4)
            op_b = m.group(5)

            # Skip numeric literals
            if re.match(r'^\d+$', op_a) and re.match(r'^\d+$', op_b):
                healed.append(line)
                i += 1
                continue

            # Check if type is unsigned
            is_unsigned = 'unsigned' in type_str

            if is_unsigned:
                healed.append(f'{indent}/* HEALED: CWE-191 underflow guard for {op_a} - {op_b} */')
                healed.append(f'{indent}{type_str} {result} = 0;')
                healed.append(f'{indent}if ({op_a} < {op_b}) {{')
                healed.append(f'{indent}    fprintf(stderr, "[HEALED] Unsigned underflow prevented in {op_a} - {op_b}\\n");')
                healed.append(f'{indent}    {result} = 0;')
                healed.append(f'{indent}}} else {{')
                healed.append(f'{indent}    {result} = {op_a} - {op_b};')
                healed.append(f'{indent}}}')
            else:
                # Signed underflow: check if result wraps
                healed.append(f'{indent}/* HEALED: CWE-191 underflow guard for {op_a} - {op_b} */')
                healed.append(f'{indent}{type_str} {result} = 0;')
                healed.append(f'{indent}if ({op_b} > 0 && {op_a} < (-__INT_MAX__ - 1) + {op_b}) {{')
                healed.append(f'{indent}    fprintf(stderr, "[HEALED] Integer underflow prevented in {op_a} - {op_b}\\n");')
                healed.append(f'{indent}    {result} = (-__INT_MAX__ - 1);')
                healed.append(f'{indent}}} else {{')
                healed.append(f'{indent}    {result} = {op_a} - {op_b};')
                healed.append(f'{indent}}}')
        else:
            healed.append(line)

        i += 1

    return '\n'.join(healed)


# ─── Buffer Overflow / Memory Safety Remediations ───────────────────────────

def _heal_buffer_overflow(code: str) -> str:
    """
    Remediates buffer overflow vulnerabilities (CWE-120, CWE-121, CWE-122, CWE-119, CWE-787, CWE-125, CWE-676).
    Replaces unbounded functions (strcpy, strcat, sprintf, gets) with safe, size-bounded alternatives.
    """
    lines = code.split('\n')
    healed = []

    strcpy_pattern = re.compile(r'^(\s*)strcpy\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s*;')
    strcat_pattern = re.compile(r'^(\s*)strcat\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s*;')
    sprintf_pattern = re.compile(r'^(\s*)sprintf\s*\(\s*([^,]+?)\s*,\s*(.+)\)\s*;')
    gets_pattern = re.compile(r'^(\s*)gets\s*\(\s*([^)]+?)\s*\)\s*;')

    for line in lines:
        m_cpy = strcpy_pattern.match(line)
        m_cat = strcat_pattern.match(line)
        m_spr = sprintf_pattern.match(line)
        m_get = gets_pattern.match(line)

        if m_cpy:
            indent, dest, src = m_cpy.group(1), m_cpy.group(2).strip(), m_cpy.group(3).strip()
            healed.append(f'{indent}strncpy({dest}, {src}, sizeof({dest}) - 1);')
            healed.append(f"{indent}{dest}[sizeof({dest}) - 1] = '\\0'; /* HEALED: bounded string copy */")
        elif m_cat:
            indent, dest, src = m_cat.group(1), m_cat.group(2).strip(), m_cat.group(3).strip()
            healed.append(f'{indent}strncat({dest}, {src}, sizeof({dest}) - strlen({dest}) - 1); /* HEALED: bounded string concat */')
        elif m_spr:
            indent, dest, rest = m_spr.group(1), m_spr.group(2).strip(), m_spr.group(3).strip()
            healed.append(f'{indent}snprintf({dest}, sizeof({dest}), {rest}); /* HEALED: bounded formatting */')
        elif m_get:
            indent, dest = m_get.group(1), m_get.group(2).strip()
            healed.append(f'{indent}fgets({dest}, sizeof({dest}), stdin); /* HEALED: safe bounded input */')
        else:
            healed.append(line)

    return '\n'.join(healed)


# ─── CWE-134: Format String Remediation ──────────────────────────────────────

def _heal_cwe134(code: str) -> str:
    """
    Remediates format string vulnerabilities (CWE-134).
    Ensures format strings are string literals by transforming printf(var) -> printf("%s", var).
    """
    lines = code.split('\n')
    healed = []
    printf_pattern = re.compile(r'^(\s*)printf\s*\(\s*([^",)]+?)\s*\)\s*;')

    for line in lines:
        m = printf_pattern.match(line)
        if m:
            indent = m.group(1)
            arg = m.group(2).strip()
            if not arg.startswith('"'):
                healed.append(f'{indent}printf("%s", {arg}); /* HEALED: CWE-134 static format string */')
            else:
                healed.append(line)
        else:
            healed.append(line)

    return '\n'.join(healed)


# ─── CWE-457: Uninitialized Variable Remediation ─────────────────────────────

def _heal_cwe457(code: str) -> str:
    """
    Remediates uninitialized variable usage (CWE-457).
    Initializes primitive variables to 0 and pointers to NULL.
    """
    lines = code.split('\n')
    healed = []
    uninit_pattern = re.compile(r'^(\s*)((?:unsigned\s+)?(?:int|long|short|char|float|double|size_t)\s+(\*?\w+))\s*;')

    for line in lines:
        m = uninit_pattern.match(line)
        if m and '=' not in line:
            indent = m.group(1)
            decl = m.group(2).strip()
            var = m.group(3).strip()
            if var.startswith('*'):
                healed.append(f'{indent}{decl} = NULL; /* HEALED: CWE-457 initialized pointer */')
            else:
                healed.append(f'{indent}{decl} = 0; /* HEALED: CWE-457 initialized variable */')
        else:
            healed.append(line)

    return '\n'.join(healed)


# ─── CWE-416: Use After Free Remediation ─────────────────────────────────────

def _heal_cwe416(code: str) -> str:
    """
    Remediates use-after-free vulnerabilities (CWE-416).
    Zeros out pointer immediately after free(ptr).
    """
    lines = code.split('\n')
    healed = []
    free_pattern = re.compile(r'^(\s*)free\s*\(\s*(\w+)\s*\)\s*;')

    for line in lines:
        m = free_pattern.match(line)
        if m:
            indent = m.group(1)
            ptr = m.group(2).strip()
            healed.append(line)
            healed.append(f'{indent}{ptr} = NULL; /* HEALED: CWE-416 zeroed pointer after free */')
        else:
            healed.append(line)

    return '\n'.join(healed)


# ─── Header Includer ────────────────────────────────────────────────────────

def _ensure_headers(code: str) -> str:
    """Make sure <stdio.h> and <string.h> are included if needed by healed code."""
    lines = code.split('\n')
    needed = []
    if ('fprintf' in code or 'printf' in code) and not any('#include <stdio.h>' in l or '#include<stdio.h>' in l for l in lines):
        needed.append('#include <stdio.h>  /* added by healer */')
    if ('strncpy' in code or 'strncat' in code or 'strlen' in code) and not any('#include <string.h>' in l or '#include<string.h>' in l for l in lines):
        needed.append('#include <string.h>  /* added by healer */')

    if needed:
        last_include = -1
        for idx, line in enumerate(lines):
            if line.strip().startswith('#include'):
                last_include = idx
        if last_include >= 0:
            for header in reversed(needed):
                lines.insert(last_include + 1, header)
        else:
            for header in reversed(needed):
                lines.insert(0, header)
        return '\n'.join(lines)
    return code


# ─── Public API ──────────────────────────────────────────────────────────────

HEALERS = {
    # Arithmetic & Division
    "CWE-369": _heal_cwe369,
    "CWE-190": _heal_cwe190,
    "CWE-191": _heal_cwe191,

    # Memory & Pointer Safety
    "CWE-476": _heal_cwe476,
    "CWE-416": _heal_cwe416,
    "CWE-457": _heal_cwe457,

    # Buffer Overflows & String Operations
    "CWE-120": _heal_buffer_overflow,
    "CWE-121": _heal_buffer_overflow,
    "CWE-122": _heal_buffer_overflow,
    "CWE-119": _heal_buffer_overflow,
    "CWE-787": _heal_buffer_overflow,
    "CWE-125": _heal_buffer_overflow,
    "CWE-676": _heal_buffer_overflow,

    # Format Strings
    "CWE-134": _heal_cwe134,
}

HEAL_DESCRIPTIONS = {
    "CWE-369": "Inserted zero-divisor guard before division/modulo operations.",
    "CWE-476": "Inserted NULL pointer check after memory allocation calls.",
    "CWE-190": "Inserted overflow boundary check before integer multiplication/addition.",
    "CWE-191": "Inserted underflow boundary check before integer subtraction.",
    "CWE-120": "Replaced unbounded buffer copy with size-bounded, null-terminated alternative.",
    "CWE-121": "Replaced stack buffer copy with size-bounded, null-terminated alternative.",
    "CWE-122": "Replaced heap buffer copy with size-bounded, null-terminated alternative.",
    "CWE-119": "Added memory bounds restrictions to prevent buffer overrun.",
    "CWE-787": "Bounded buffer write operation to allocated destination size.",
    "CWE-125": "Bounded buffer read operation to allocated destination size.",
    "CWE-676": "Replaced dangerous unbounded API with safe bounded alternative.",
    "CWE-134": "Replaced variable format string with static specifier string.",
    "CWE-457": "Initialized uninitialized variable to prevent undefined behavior.",
    "CWE-416": "Zeroed pointer immediately after free to prevent use-after-free.",
}


def heal_code(source_code: str, detected_cwes: list[str]) -> dict:
    if not detected_cwes:
        return {
            "success": True,
            "healed_code": source_code,
            "patches": [],
            "message": "No vulnerabilities detected — code is already clean.",
        }

    code = source_code
    patches = []

    for cwe in detected_cwes:
        healer = HEALERS.get(cwe)
        if healer:
            original = code
            code = healer(code)
            if code != original:
                patches.append({
                    "cwe": cwe,
                    "description": HEAL_DESCRIPTIONS.get(cwe, "Applied fix."),
                    "applied": True,
                })
            else:
                patches.append({
                    "cwe": cwe,
                    "description": f"No actionable pattern found for {cwe} (code may use non-standard patterns).",
                    "applied": False,
                })
        else:
            patches.append({
                "cwe": cwe,
                "description": f"No healer available for {cwe}.",
                "applied": False,
            })

    if any(p["applied"] for p in patches):
        code = _ensure_headers(code)

    return {
        "success": True,
        "healed_code": code,
        "patches": patches,
        "message": f"Applied {sum(1 for p in patches if p['applied'])} patch(es).",
    }
