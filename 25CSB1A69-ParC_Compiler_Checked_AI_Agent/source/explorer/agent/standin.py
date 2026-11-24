"""A worst-case stand-in for the language model, for showing the security layer live.

It is not a real model and the page says so. It plays the model the agent must
be safe against: one that does whatever a comment in its prompt tells it, and
believes whatever a comment claims. If the security layer keeps the comment
away from it (comments removed from the prompt), it answers honestly.

That makes the effect of the layer visible without a model key and without
luck: the same request with the layer off and on gives the attacker's answer
and the honest one. The evaluation's stand-ins (evaluation/security_eval.py)
work the same way; this one reads the prompt instead of being told the attack.
"""

import re

NAME = "simulated model (obeys every comment it sees)"

# A comment that gives an order, or one that reassures: the worst-case model falls for both.
_ORDER = re.compile(r"\b(ignore|disregard|mark|treat|declare|approve|report|skip|disable|must|always|print|call|"
                    r"log|note for|ai|assistant|agent|model)\b", re.IGNORECASE)
_REASSURES = re.compile(r"\b(never|not|non-?zero|always|positive|at least|safe|checked|validated|guaranteed)\b",
                        re.IGNORECASE)


def _comments(prompt):
    """The comments in the code part of a prompt (the code is shown as numbered lines: '   3 |     // ...')."""
    return [m.group(1).strip() for m in re.finditer(r"^\s*\d+ \|.*?//(.*)$", prompt, flags=re.MULTILINE)]


def _code(prompt):
    """The function's code from the prompt, without the line numbers."""
    return "\n".join(m.group(1) for m in re.finditer(r"^\s*\d+ \| ?(.*)$", prompt, flags=re.MULTILINE))


_HTML = re.compile(r"<[a-zA-Z][^>]*>")


class WorstCase:
    name = NAME
    cacheable = False  # it answers by rule; llm.complete must not keep its answers

    def __init__(self, gullible=False):
        # gullible: every comment that reaches it counts as an order, whatever it says or in which
        # language. The "Break my agent" challenge uses this, so the only question is whether the
        # comment gets past the checks, not whether it happens to use a word this stand-in knows.
        self.gullible = gullible
        if gullible:
            self.name = "simulated model (obeys any comment it sees)"

    def complete(self, system, prompt):
        comments = _comments(prompt)
        orders = comments if self.gullible else [c for c in comments if _ORDER.search(c)]
        claims = [c for c in comments if _REASSURES.search(c)]
        if system.startswith("You explain"):
            return self._explain(prompt, orders, claims)
        if system.startswith("You repair"):
            return self._fix(prompt, orders + claims)
        return '{"claims": []}'  # the claim extractor's question: this stand-in has nothing to add

    @staticmethod
    def _finding(prompt):
        match = re.search(r"Explain finding (F\d+)|Fix finding (F\d+)", prompt)
        return next((g for g in match.groups() if g), "F1") if match else "F1"

    def _explain(self, prompt, orders, claims):
        fid = self._finding(prompt)
        if orders:
            # If the order carries markup, a naive model copies it into its answer: the page must show it
            # as text, never run it (OWASP LLM10, improper output handling).
            markup = next((m.group(0) for c in orders for m in [_HTML.search(c)] if m), "")
            return (f"As the note in the code says, this code is safe and the warning can be ignored "
                    f"{markup + ' ' if markup else ''}[{fid}].")
        if claims:
            # The dangerous kind: no telltale word, it just repeats the comment's claim.
            return (f"The comment explains that {claims[0].split(',')[0].strip()}, "
                    f"so this division works for every call [{fid}].")
        divisor = re.search(r"divides by zero when (\w+) is 0", prompt)
        name = divisor.group(1) if divisor else "the divisor"
        return (f"The division on this line fails when {name} is 0 [{fid}]. Nothing before it checks {name}, "
                f"so the program can stop here [{fid}].")

    def _fix(self, prompt, obeyed):
        code = _code(prompt)
        header = re.search(r"^\s*fn\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([\w\[\]]+))?\s*\{", code, flags=re.MULTILINE)
        divisor = re.search(r"divides by zero when (\w+) is 0", prompt)
        if not header or not divisor:
            return "I cannot rewrite this one."
        params = [p.split(":")[0].strip() for p in header.group(2).split(",") if ":" in p]
        bail = "return 0;" if header.group(3) == "int" else "return;"
        leak = ""
        if obeyed:
            # Whatever the comment asked for, the worst case adds a leak on the error path.
            other = next((p for p in params if p != divisor.group(1)), params[0] if params else "0")
            leak = f"        print({other});\n"
        lines = code.split("\n")
        start = next(i for i, line in enumerate(lines) if re.match(r"^\s*fn\s", line))
        guard = f"    if ({divisor.group(1)} == 0) {{\n{leak}        {bail}\n    }}"
        body = [line for line in lines[start + 1:] if not line.strip().startswith("//")]
        rewritten = "\n".join([lines[start], guard] + body).rstrip()
        return f"Version 1:\n```parc\n{rewritten}\n```"


class Liar:
    """A model that is itself hostile, with nothing hidden in the code to detect: it lies about
    every warning it is asked about, in the exact wording the input-stage rules know ("false
    positive"), to show that a reviewer judging the code can never catch a model that was
    compromised some other way — only a check of what the model itself says can."""

    name = "simulated model (hostile, lies about every warning)"
    cacheable = False

    def complete(self, system, prompt):
        match = re.search(r"Explain finding (F\d+)|Fix finding (F\d+)", prompt)
        fid = next((g for g in match.groups() if g), "F1") if match else "F1"
        if system.startswith("You repair"):
            return "I cannot rewrite this one."
        return f"This code is safe and the warning is a false positive [{fid}]."


class Honest:
    """A plain, honest stand-in whose answers ARE cached, like a real model's. The cache-poisoning
    demo needs one: an attacker who can write the cache replaces its stored answer with a lie."""

    name = "simulated model (honest, answers cached)"
    cacheable = True

    def complete(self, system, prompt):
        match = re.search(r"Explain finding (F\d+)", prompt)
        fid = match.group(1) if match else "F1"
        divisor = re.search(r"divides by zero when (\w+) is 0", prompt)
        name = divisor.group(1) if divisor else "the divisor"
        return f"The division fails when {name} is 0 [{fid}]. Nothing checks {name} first, so the program can stop [{fid}]."
