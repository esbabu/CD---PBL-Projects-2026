"""The compiler gate: the judge of every proposed rewrite.

A candidate is a whole new source text in which one function was rewritten.
It is accepted only if it passes every check, in this order, stopping at the
first failure:

    1. scope      nothing outside the flagged function changed
    2. compiles   all phases run without an error
    3. fixed      the finding it was written for is gone
    4. no harm    no warning appeared that was not there before
    5. error path where the finding's guard holds (b == 0 for a division by b),
                  the original fails, so there is no result to compare with.
                  There the rewrite may only return a value known when
                  compiling or stop: no print, call, array store or new array,
                  and no return of a value that comes from the inputs. The
                  blocks are found by the compiler's value analysis
                  (ranges.json), so it does not matter how the condition is
                  written.
    6. behaviour  on inputs where the original function worked, the rewrite
                  returns and prints exactly the same; on inputs where it
                  failed, the rewrite prints nothing the original had not
                  printed before it failed, and it returns

Each check is something the compiler measures, so the verdict can be defended.
Passing candidates are then ranked: fewest remaining warnings first, then the
smallest change to the user's code.
"""

import ast
import difflib
import operator
import os
import random
import re

import compiler_bridge as bridge

INPUTS_PER_FUNCTION = 40
INTERESTING_INTS = [0, 1, 2, 3, 5, 10, -1, -7, 100, 1000, 2147483647, -2147483648]


# ---------------------------------------------------------------- the function a finding is in

def function_span(source, name):
    """(first line, last line) of function `name`, 1-based, found by matching braces.

    Strings and comments are skipped, so a brace inside them does not count.
    Returns None if there is no such function.
    """
    match = re.search(rf"^[ \t]*fn\s+{re.escape(name)}\s*\(", source, flags=re.MULTILINE)
    if not match:
        return None
    first = source.count("\n", 0, match.start()) + 1
    depth = 0
    i = match.end()
    seen_open = False
    while i < len(source):
        ch = source[i]
        if source.startswith("//", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end
            continue
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            i = len(source) if end < 0 else end + 2
            continue
        if ch == '"':
            i += 1
            while i < len(source) and source[i] not in '"\n':
                i += 2 if source[i] == "\\" else 1
        elif ch == "{":
            depth += 1
            seen_open = True
        elif ch == "}":
            depth -= 1
            if seen_open and depth == 0:
                return first, source.count("\n", 0, i) + 1
        i += 1
    return None


def function_text(source, name):
    span = function_span(source, name)
    if not span:
        return ""
    return "\n".join(source.split("\n")[span[0] - 1: span[1]])


def replace_function(source, name, new_text):
    """The source with function `name` replaced by `new_text`, or None if it has no such function."""
    span = function_span(source, name)
    if not span:
        return None
    lines = source.split("\n")
    return "\n".join(lines[: span[0] - 1] + new_text.strip("\n").split("\n") + lines[span[1]:])


def _outside(source, name):
    span = function_span(source, name)
    if not span:
        return None
    lines = source.split("\n")
    return lines[: span[0] - 1] + ["<function>"] + lines[span[1]:]


# ---------------------------------------------------------------- comparing findings

def identity(finding):
    """What makes two findings "the same" before and after a rewrite: line numbers move, these do not."""
    return finding.get("kind", ""), finding.get("function", ""), finding.get("subject", "")


def _problems(build):
    """The identities of the errors and warnings (notes are not problems)."""
    return [identity(f) for f in build["findings"]["findings"] if f["severity"] in ("error", "warning")]


def _count(items, item):
    return sum(1 for other in items if other == item)


# ---------------------------------------------------------------- test inputs

def _parameter_types(build, function):
    for symbol in build.get("symbols", {}).get("symbols", []):
        if symbol["kind"] == "function" and symbol["name"] == function:
            inside = symbol["type"][symbol["type"].index("(") + 1: symbol["type"].index(")")]
            return [part.split(":")[1].strip() for part in inside.split(",") if ":" in part]
    return None


def _value(rng, type_text):
    if type_text.endswith("[]"):
        if rng.random() < 0.1:
            return "null"
        base = type_text[:-2]
        return "[" + ",".join(_value(rng, base) for _ in range(rng.randint(0, 6))) + "]"
    if type_text == "bool":
        return rng.choice(["true", "false"])
    if type_text == "float":
        return rng.choice(["0.0", "1.0", "-2.5", "0.5", "100.0", "3.25"])
    if rng.random() < 0.6:
        return str(rng.randint(-20, 20))
    return str(rng.choice(INTERESTING_INTS))


def test_inputs(types, count=INPUTS_PER_FUNCTION):
    """Argument lists for a function with these parameter types. Always the same ones (fixed seed)."""
    rng = random.Random(20261001)
    return [" ".join(_value(rng, t) for t in types) for _ in range(count)]


def _clean(result):
    return result["ok"] and result["overflows"] == 0 and result["races"] == 0


def _never_returns(result):
    """The VM gave up on this call after its step limit: an endless loop."""
    return not result["ok"] and "steps and was stopped" in result["error"]


# ---------------------------------------------------------------- the error path (check 5)

# What a fix may do where the original fails: return a known value, or stop.
ERROR_PATH_EFFECTS = {"print": "prints", "call": "calls", "store": "writes to an array",
                      "alloc": "allocates an array"}

_CLAUSE = re.compile(r"^\s*([A-Za-z_]\w*)\s*(==|!=|<=|>=|<|>)\s*(.+?)\s*$")
_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.FloorDiv: operator.floordiv}


def _constant(text):
    """The value of a constant like 0, -1 or 2147483647 - 1000 (how guards are written), else None."""
    text = text.strip().replace("/", "//")
    try:
        tree = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None

    def value(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = value(node.operand)
            return None if inner is None else -inner
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = value(node.left), value(node.right)
            if left is None or right is None or (isinstance(node.op, ast.FloorDiv) and right == 0):
                return None
            return _BINARY[type(node.op)](left, right)
        return None
    return value(tree)


def _clause_holds(clause, variables):
    """True when every value the analysis allows for the variable satisfies `x op c`.

    None when the clause is not of that shape or the variable is not known
    (the guard is on an expression, say): then nothing can be said."""
    match = _CLAUSE.match(clause)
    if not match:
        return None
    name, op, right = match.groups()
    var = variables.get(name)
    if var is None:
        return None
    if right.strip() == "null":
        if var["type"] != "array" or op not in ("==", "!="):
            return None
        return var["null"] == "yes" if op == "==" else var["null"] == "no"
    c = _constant(right)
    if c is None or var["type"] != "int":
        return None
    lo, hi = var["lo"], var["hi"]
    return {"==": lo == c == hi, "!=": c < lo or c > hi or (c == 0 and var["nonzero"]),
            "<": hi < c, "<=": hi <= c, ">": lo > c, ">=": lo >= c}[op]


def guard_holds(guard, variables):
    """Whether the compiler's facts at a block prove the finding's guard.

    `variables` maps a name to its fact from ranges.json. The guard is the
    condition the compiler puts in a finding: "b == 0", "a == null",
    "x > 2147483647 - 1000", "i < 0 || i >= len(a)". One clause of an || that
    holds is enough; every clause of an && must hold. Returns None when the
    guard cannot be decided from the facts."""
    if not guard:
        return None
    alternatives = []
    for part in guard.split("||"):
        clauses = [_clause_holds(c, variables) for c in part.split("&&")]
        alternatives.append(None if None in clauses else all(clauses))
    if any(a is True for a in alternatives):
        return True
    return None if None in alternatives else False


def error_path_blocks(ranges, function, guard):
    """The blocks of `function` in which the guard is known to hold, from ranges.json.

    Returns None when the guard cannot be decided at all (no facts, or a guard
    on an expression), and [] when it can be decided but holds nowhere."""
    facts = next((f for f in (ranges or {}).get("functions", []) if f["name"] == function), None)
    if facts is None:
        return None
    decided, found = False, []
    for block in facts["blocks"]:
        if not block["reachable"]:
            continue
        holds = guard_holds(guard, {v["name"]: v for v in block["vars"]})
        decided |= holds is not None
        if holds:
            found.append(block)
    return found if decided else None


def error_path_problem(block, guard):
    """What a block on the error path does that a fix may not do there, as a sentence, or ""."""
    for effect in block["effects"]:
        where = f"on line {effect['line']}, where {guard} (the error path)"
        if effect["kind"] in ERROR_PATH_EFFECTS:
            what = effect.get("callee") or effect["subject"]
            return f"it {ERROR_PATH_EFFECTS[effect['kind']]} {what!r} {where}"
        if effect["kind"] == "return" and not effect["constant"]:
            return f"it returns {effect['subject']!r}, a value that comes from the inputs, {where}"
    return ""


# ---------------------------------------------------------------- the gate

def diff_size(original, candidate):
    """How many lines were added, removed or changed."""
    changed = 0
    for line in difflib.ndiff(original.split("\n"), candidate.split("\n")):
        if line.startswith(("+ ", "- ")):
            changed += 1
    return changed


def judge(original, original_build, finding, candidate):
    """Runs the gate on one candidate source. Returns a verdict:

        {"passed": bool, "failed_at": "", "reason": "", "evidence": [...],
         "warnings": int, "diff": int}
    """
    function = finding.get("function", "")
    verdict = {"passed": False, "failed_at": "", "reason": "", "evidence": [], "warnings": 0,
               "diff": diff_size(original, candidate)}

    def fail(stage, reason):
        verdict["failed_at"] = stage
        verdict["reason"] = reason
        return verdict

    # 1. Scope: only the flagged function may change.
    before, after = _outside(original, function), _outside(candidate, function)
    if before is None or after is None or before != after:
        return fail("scope", f"the rewrite changes code outside the function '{function}'")
    if verdict["diff"] == 0:
        return fail("scope", "the rewrite is identical to the original")

    # 2. It compiles through every phase.
    try:
        build = bridge.build(candidate)
    except bridge.CompilerTimeout:
        return fail("compiles", "the compiler did not finish on the rewrite")
    if build["stage"] != "complete":
        first = build["errors"][0] if build["errors"] else {"line": 0, "message": "it does not compile"}
        return fail("compiles", f"it does not compile: line {first['line']}: {first['message']}")
    verdict["evidence"].append("compiles through all phases")

    # 3. The finding is gone.
    target = identity(finding)
    is_note = finding["severity"] == "info"
    old_all = [identity(f) for f in original_build["findings"]["findings"]]
    new_all = [identity(f) for f in build["findings"]["findings"]]
    if _count(new_all, target) >= _count(old_all, target):
        return fail("fixed", f"the compiler still reports it: {finding['message']}")
    verdict["evidence"].append(f"{finding['id']} is gone")

    # 4. Nothing new went wrong.
    old_problems = _problems(original_build)
    new_problems = _problems(build)
    for problem in set(new_problems):
        if _count(new_problems, problem) > _count(old_problems, problem):
            message = next(f["message"] for f in build["findings"]["findings"] if identity(f) == problem)
            return fail("no harm", f"a new warning appeared: {message}")
    verdict["warnings"] = len(new_problems)
    verdict["evidence"].append("no new warnings" if not is_note else "no warnings were added")

    # 5. The error path: where the original fails, a fix may only return a known value or stop.
    guard = finding.get("guard", "")
    blocks = error_path_blocks(build.get("ranges"), function, guard) if guard else None
    if blocks:
        for block in blocks:
            problem = error_path_problem(block, guard)
            if problem:
                return fail("error path", problem + "; a fix may only return a value known when compiling there, "
                                                    "or stop")
        lines = sorted({b["line"] for b in blocks if b["line"]})
        verdict["evidence"].append(f"on the error path ({guard}, line{'s' if len(lines) > 1 else ''} "
                                   f"{', '.join(map(str, lines))}) it only returns a known value")
    elif guard and blocks is None:
        verdict["evidence"].append(f"the compiler cannot place the error path ({guard}); "
                                   "only the test inputs check it")

    # 6. Behaviour. First the whole program, exactly as it is.
    try:
        old_run = bridge.run(original, optimize=False)
        new_run = bridge.run(candidate, optimize=False)
    except bridge.CompilerTimeout:
        return fail("behaviour", "the rewritten program did not finish in time")
    if old_run.get("compiled") and _clean(old_run):
        if not new_run.get("compiled") or not _clean(new_run):
            error = new_run.get("error", {}).get("message", "it overflows or races")
            return fail("behaviour", f"the program ran cleanly before and now does not: {error}")
        # Printing order inside a parallel loop depends on the schedule, so compare lines as a set there.
        same = old_run["output"] == new_run["output"]
        if not same and (old_run["parallel_loops"] or new_run["parallel_loops"]):
            same = sorted(old_run["output"].split("\n")) == sorted(new_run["output"].split("\n"))
        if not same:
            return fail("behaviour", "the program prints something different: expected "
                        f"{old_run['output'][:80]!r}, got {new_run['output'][:80]!r}")
        verdict["evidence"].append("the program prints exactly the same as before")
    elif old_run.get("compiled"):
        problem = old_run.get("error", {}).get("message") or "an int overflow"
        if new_run.get("compiled") and _clean(new_run):
            verdict["evidence"].append(f"the original run had a problem ({problem}); the rewrite runs cleanly")
        else:
            verdict["evidence"].append(f"the original run had a problem ({problem}), so its output is no reference")

    # Then the flagged function alone, on many inputs. Wherever the original
    # worked without trouble, the rewrite must do exactly the same.
    types = _parameter_types(original_build, function)
    if types and function != "main":
        inputs = test_inputs(types)
        try:
            old_results = bridge.call(original, function, inputs, optimize=False)
            new_results = bridge.call(candidate, function, inputs, optimize=False)
        except bridge.CompilerTimeout:
            return fail("behaviour", "the rewritten function did not finish in time on the test inputs")
        if old_results is None:
            return verdict | {"passed": True}  # the function can't be run on its own; the checks above stand
        if new_results is None:
            return fail("behaviour", "the rewrite changed the function's parameters")
        same_on = fixed = 0
        for old, new in zip(old_results, new_results):
            if not _clean(old):
                # The original went wrong here, so there is no result to compare with.
                # One thing is still worse than any error: not coming back at all.
                if _never_returns(new) and not _never_returns(old):
                    return fail("behaviour", f"for the arguments ({old['args']}) the original stops with an error "
                                             "and the rewrite never returns (an endless loop)")
                # Nor printing what the original never printed: that is a leak on the error path,
                # also where the compiler could not place that path itself.
                if not old["output"].startswith(new["output"]):
                    extra = new["output"][len(os.path.commonprefix([old["output"], new["output"]])):]
                    return fail("error path", f"for the arguments ({old['args']}) the original stops with an error, "
                                              f"and the rewrite prints {extra.strip()[:60]!r}, which the original "
                                              "never printed")
                fixed += 1 if _clean(new) else 0
                continue
            if (not _clean(new) or old["returned"] != new["returned"] or old["output"] != new["output"]
                    or old["arrays"] != new["arrays"]):
                got = new["error"] or new["returned"] or new["output"]
                return fail("behaviour", f"for the arguments ({old['args']}) the original gives {old['returned'] or old['output']!r} "
                                         f"and the rewrite gives {got!r}")
            same_on += 1
        verdict["evidence"].append(f"same result on {same_on} of {len(inputs)} test inputs where the original works")
        if fixed:
            verdict["evidence"].append(f"{fixed} inputs that made the original fail now work")

    verdict["passed"] = True
    return verdict


def rank(candidates):
    """Orders judged candidates: passing ones first, then fewest warnings, then smallest change."""
    return sorted(candidates, key=lambda c: (not c["verdict"]["passed"], c["verdict"]["warnings"], c["verdict"]["diff"]))
