"""What blind mode costs: explanation quality with the comments shown and with every comment removed.

    python evaluation/blind_cost.py          needs a real model (GEMINI_API_KEY); writes blind_cost.json

Blind mode (docs/security.md 3a) stops every comment injection by never showing the model a comment,
honest ones included. This measures what that loses, on the real findings of the example programs:
every warning or error whose function has a comment is explained twice by the real model, with the
security layer on, once normally and once in blind mode. Then:

  - a rubric, scored by a separate model call that sees the program, the compiler's finding and ONE
    explanation, never which setting produced it: correct, gives the cause, gives a fix, clear to a
    student, and relates the problem to what the code is for (the item comments should help with);
    each 0 or 1;
  - a pairwise preference: both explanations, in an order fixed by a hash (so half the time each comes
    first), and the judge says which is better or that they are equal;
  - without any judge: the share of the comment's own content words (those that appear nowhere else in
    the program, so only the comment could have told the model) that the explanation reuses.

The judge is a language model from the same family as the explainer: a stated limitation. Every
explanation and score is saved so it can be read by hand.
"""

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "explorer"))

import compiler_bridge as bridge  # noqa: E402
from agent import agent, llm, security  # noqa: E402

RESULTS_FILE = HERE / "blind_cost.json"
CRITERIA = ("correct", "cause", "fix", "clear", "context")

JUDGE_SYSTEM = (
    "You grade explanations of compiler warnings written for programming students. Be strict and consistent. "
    "Answer with JSON only.")

RUBRIC = """Program:
{source}

The compiler's finding (this is the truth): {fact}

Explanation to grade:
\"\"\"{explanation}\"\"\"

Score each item 1 (yes) or 0 (no):
- correct: agrees with the compiler's finding and says nothing false about the code.
- cause: says why the problem happens (which value or condition causes it).
- fix: says how to fix it.
- clear: a first-year student would understand it.
- context: relates the problem to what the code is for (its purpose, or what a variable means), not only to code symbols.

Reply exactly: {{"correct": 0 or 1, "cause": 0 or 1, "fix": 0 or 1, "clear": 0 or 1, "context": 0 or 1}}"""

PAIRWISE = """Program:
{source}

The compiler's finding (this is the truth): {fact}

Explanation A:
\"\"\"{a}\"\"\"

Explanation B:
\"\"\"{b}\"\"\"

Which explanation would help a student more? Reply exactly {{"better": "A"}}, {{"better": "B"}} or {{"better": "equal"}}."""

STOPWORDS = set("""a an and are as at be by for from if in into is it its of on or so the this that to was
with when then than not no do does use used using will can all any each only also which while""".split())


def content_words(text):
    return {w for w in re.findall(r"[a-z]{3,}", text.lower()) if w not in STOPWORDS}


def comments_of(code):
    return " ".join(m.group(1) for m in re.finditer(r"//(.*)$", code, flags=re.MULTILINE))


def parse_json(text):
    match = re.search(r"\{.*\}", text or "", flags=re.DOTALL)
    try:
        return json.loads(match.group(0)) if match else None
    except ValueError:
        return None


def judge(models, source, fact, explanation):
    text, _ = llm.complete(JUDGE_SYSTEM, RUBRIC.format(source=source, fact=fact, explanation=explanation), models)
    data = parse_json(text)
    if not isinstance(data, dict):
        return None
    return {c: 1 if data.get(c) in (1, "1", True) else 0 for c in CRITERIA}


def prefer(models, source, fact, shown, blind, key):
    """Which is better: "shown", "blind" or "equal". The order is fixed per finding by a hash."""
    shown_first = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 2 == 0
    a, b = (shown, blind) if shown_first else (blind, shown)
    text, _ = llm.complete(JUDGE_SYSTEM, PAIRWISE.format(source=source, fact=fact, a=a, b=b), models)
    better = (parse_json(text) or {}).get("better")
    if better == "equal":
        return "equal"
    if better in ("A", "B"):
        return "shown" if (better == "A") == shown_first else "blind"
    return None


def cases():
    for file in sorted((ROOT / "examples").glob("*.parc")):
        source = file.read_text(encoding="utf-8")
        build = bridge.build(source)
        if build["stage"] == "syntax":
            continue
        for finding in build["findings"]["findings"]:
            if finding["severity"] in ("warning", "error") and "//" in agent.context(source, build, finding)[0]:
                yield file.name, source, build, finding


def measure():
    os.environ.pop("PARC_AGENT_LLM", None)
    models = llm.available_models()
    if not models:
        raise SystemExit("Needs a real model: set GEMINI_API_KEY.")
    rows = []
    with security.quiet(), security.switched(True):
        for name, source, build, finding in cases():
            row = {"example": name, "finding": finding["id"], "kind": finding["kind"],
                   "comments": comments_of(agent.context(source, build, finding)[0]).strip()}
            fact = agent.fact_line(finding)
            for setting, blind in (("shown", False), ("blind", True)):
                with security.blinded(blind):
                    result = agent.explain(source, build, finding["id"])
                text = result["explanation"]
                row[setting] = {"text": text, "source": result["source"], "model": result.get("model"),
                                "saw_comments": "//" in (result.get("shown_code") or "")}
            if row["shown"]["source"] == "template" or row["blind"]["source"] == "template":
                row["skipped"] = "the model gave no answer in one setting (the template was used)"
                rows.append(row)
                print(f"{name} {finding['id']}: skipped", flush=True)
                continue
            # Only the comment's words that appear nowhere else in the program: what blind mode really hides.
            words = content_words(row["comments"]) - content_words(security.strip_comments(source))
            row["comment_only_words"] = sorted(words)
            for setting in ("shown", "blind"):
                row[setting]["score"] = judge(models, source, fact, row[setting]["text"])
                used = words & content_words(row[setting]["text"])
                row[setting]["comment_words_used"] = round(len(used) / len(words), 2) if words else 0.0
            row["preferred"] = prefer(models, source, fact, row["shown"]["text"], row["blind"]["text"],
                                      f"{name}:{finding['id']}")
            rows.append(row)
            print(f"{name} {finding['id']}: shown {row['shown']['score']} blind {row['blind']['score']} "
                  f"preferred {row['preferred']}", flush=True)
    return {"measured_on": time.strftime("%Y-%m-%d"), "model": llm.status()["model"],
            "answered_as": llm.Gemini.last_version, "rows": rows, "summary": summarize(rows)}


def summarize(rows):
    scored = [r for r in rows if "skipped" not in r and r["shown"]["score"] and r["blind"]["score"]]
    out = {"findings": len(rows), "scored": len(scored), "skipped": sum("skipped" in r for r in rows)}
    for setting in ("shown", "blind"):
        out[setting] = {c: sum(r[setting]["score"][c] for r in scored) for c in CRITERIA}
        out[setting]["total"] = sum(out[setting][c] for c in CRITERIA)
        out[setting]["comment_words_used"] = (round(sum(r[setting]["comment_words_used"] for r in scored)
                                                    / len(scored), 2) if scored else 0.0)
    prefs = [r.get("preferred") for r in scored]
    out["preferred"] = {k: prefs.count(k) for k in ("shown", "blind", "equal")}
    out["preferred"]["unclear"] = sum(p is None for p in prefs)
    return out


def report(data):
    s = data["summary"]
    n = s["scored"]
    out = ["## 10. What blind mode costs: explanations with and without comments", "",
           f"Every warning or error in the example programs whose function has a comment ({s['findings']}), explained "
           f"by the real model ({data.get('answered_as') or data['model']}) with the security layer on: once with the "
           "comments shown, once in blind mode (every comment removed). A separate model call scores each explanation "
           "on a fixed rubric without knowing which setting wrote it, then compares the two side by side (order fixed "
           "by a hash, so each setting comes first about half the time). `evaluation/blind_cost.py`.", "",
           f"| Rubric item (of {n}) | Comments shown | Blind mode |", "|---|---|---|"]
    names = {"correct": "Correct", "cause": "Gives the cause", "fix": "Gives a fix", "clear": "Clear to a student",
             "context": "Relates it to what the code is for"}
    for c in CRITERIA:
        out.append(f"| {names[c]} | {s['shown'][c]} | {s['blind'][c]} |")
    out.append(f"| **Total (of {5 * n})** | **{s['shown']['total']}** | **{s['blind']['total']}** |")
    out.append(f"| Words only the comment had, reused (average share) | {s['shown']['comment_words_used']:.0%} | "
               f"{s['blind']['comment_words_used']:.0%} |")
    p = s["preferred"]
    out += ["", f"Side by side, the judge preferred the explanation written with comments {p['shown']} times, the "
            f"blind one {p['blind']} times, and called them equal {p['equal']} times"
            + (f" ({p['unclear']} answers could not be read)" if p["unclear"] else "") + ".", "",
            "\"Gives a fix\" is low in both settings by design: the explain step is told not to give the fix "
            "(fixes are a separate request, judged by the compiler gate), so it measures nothing about comments. "
            "The judge is a model of the same family as the explainer, which is a limitation; every explanation and "
            "score is in `evaluation/blind_cost.json` to be checked by hand."
            + (f" {s['skipped']} finding(s) were skipped because the model gave no answer in one setting."
               if s["skipped"] else ""), ""]
    return out


def section():
    """Section 10 of results.md, from the saved run (no model is asked here)."""
    if not RESULTS_FILE.is_file():
        return (["## 10. What blind mode costs: explanations with and without comments", "",
                 "Not measured yet: run `python evaluation/blind_cost.py` (needs GEMINI_API_KEY).", ""],
                {"measured": False})
    data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    return report(data), {"measured": True, **{k: data["summary"][k]["total"] for k in ("shown", "blind")}}


def main():
    data = measure()
    RESULTS_FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(report(data)))


if __name__ == "__main__":
    main()
