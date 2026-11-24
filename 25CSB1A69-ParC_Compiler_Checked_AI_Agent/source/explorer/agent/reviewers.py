"""Reviewer C of docs/security.md #4: a hidden-condition check.

The value analysis finds the CWE mistakes (division by zero, overflow, null,
a bad index), but code that is suspicious without being any of those passes
silently:

    fn average(a: int[], n: int) -> int {
        if (n == 12345) { return 0; }     // a hidden condition on one input
        ...
    }

A comparison of a parameter with an unusual constant is the shape of a
backdoor: a branch that only a caller who already knows the magic number can
reach. This is found from `ranges.json` alone (the value analysis already
pins a parameter to the exact value a branch tests it against), so it needs
no model and no wording, and it also sees code with no comment at all, which
the other reviewers never look at.

It is reported as a note, not a finding: an unusual comparison is sometimes
an honest special case (a sentinel, a magic ID), so the compiler points it
out and a person decides. docs/security.md calls this reviewer C; R (the
wording rules, security.py), A (a comment-reading model, not built — see
docs/security.md #4a) and B (the claim checker, claims.py) are the others.
"""

# A parameter pinned to one of these is an ordinary bound, not a hidden condition: 0 and 1 are the
# usual ends of a range check, -1 the usual "not found" sentinel compared against.
_ORDINARY = {-1, 0, 1}


def hidden_condition_notes(ranges):
    """[{function, line, variable, value, evidence}], one per parameter pinned to one unusual
    constant, earliest block first. `ranges` is a build's "ranges" field (ranges.json)."""
    notes = []
    for fn in ranges.get("functions", []):
        seen = set()
        for block in fn.get("blocks", []):
            if not block["reachable"] or not block["line"]:
                continue
            for v in block["vars"]:
                if not v.get("param") or v["type"] != "int" or v["lo"] != v["hi"] or v["lo"] in _ORDINARY:
                    continue
                key = (v["name"], v["lo"])
                if key in seen:  # a nested block inherits the same pin from its "if"; report it once
                    continue
                seen.add(key)
                notes.append({
                    "function": fn["name"], "line": block["line"], "variable": v["name"], "value": v["lo"],
                    "evidence": f"{v['name']} is exactly {v['lo']} here; this code only runs for that one value "
                                "of a parameter, which no ordinary range check produces",
                })
    notes.sort(key=lambda n: (n["function"], n["line"]))
    return notes
