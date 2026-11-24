"""AI against AI: a language model attacks the agent for several rounds, learning from each one.

    python evaluation/aivsai.py                  simulated attacker, simulated defender (offline)
    python evaluation/aivsai.py --live           Gemini attacks; two match-ups (below); writes section 9
    python evaluation/aivsai.py --live --rounds 10 --fresh   ask the model again instead of the cache

redteam.py's attacker is a fixed list of disguises written by the same person as the rules. Here
the attacker is a model that never saw the rules: each round it writes one comment, is told how it
went (with feedback "full", also which check stopped it), and writes the next. The agent answers each
comment twice, with the security layer off and on. explorer/agent/arena.py has the loop.

The live run plays two match-ups, for both goals:

    vs stand-in   the defender obeys any comment that reaches it, so everything rests on the layer.
                  Its answer is the same whatever the comment says, so this measures one thing: how
                  often the attacker's comment gets past the input check to the model.
    vs Gemini     both sides are real models: the realistic case.

Success is judged by words in what the user is told (arena.SAFE_CLAIM) or, for a fix, a print() in
a fix that passed the compiler gate. A manipulated explanation in words the pattern does not know
would be missed; every attempt is saved with what the user was told, so it can be read by hand.
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "explorer"))

from agent import arena, llm  # noqa: E402

RESULTS_FILE = HERE / "aivsai_results.json"


def matchups(live):
    if not live:
        return [("simulated attacker vs stand-in", arena.ScriptedAttacker, "simulated")]
    return [("Gemini vs stand-in", arena.ModelAttacker, "simulated"),
            ("Gemini vs Gemini", arena.ModelAttacker, "real")]


def run_all(live=False, rounds=8, use_cache=True):
    runs = []
    for label, make_attacker, defender in matchups(live):
        for goal in arena.GOALS:
            attacker = make_attacker()
            if not attacker.available():
                raise SystemExit("No language model is set up to play the attacker (GEMINI_API_KEY).")
            started = time.monotonic()
            result = arena.run(goal, rounds, attacker, defender, "full", use_cache=use_cache)
            result["matchup"] = label
            result["seconds"] = round(time.monotonic() - started, 1)
            runs.append(result)
            s = result["summary"]
            print(f"{label}, {goal}: {s['succeeded_off']}/{s['rounds']} off, {s['succeeded_on']}/{s['rounds']} on, "
                  f"reached the model {s['reached_model_on']} times with the layer on ({result['seconds']} s)",
                  flush=True)
    return runs


def _round(n):
    return f"round {n}" if n else "never"


def report(runs):
    out = ["## 9. AI against AI: a model attacks the agent", "",
           "A language model plays the attacker (`explorer/agent/arena.py`, `evaluation/aivsai.py`). Each round it "
           "writes one comment, placed above `return sum / n;`, and the agent is asked about that division twice, "
           "with the security layer off and on. The attacker is then told whether it worked, what the user was told, "
           "whether its comment reached the model and which check stopped it, and writes the next one. It never "
           "saw the rules' source; it learns only from these outcomes.", "",
           "| Match-up | Goal | Rounds | Attacker | Succeeds, layer off | Succeeds, layer on | First success, off / on "
           "| Reached the model, layer on | Stopped by (layer on) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        s = run["summary"]
        stopped = ", ".join(f"{k} {v}" for k, v in s["caught_by"].items()) or "nothing"
        out.append(f"| {run.get('matchup', '')} | {run['goal']} | {s['rounds']} | {run['attacker']} | "
                   f"{s['succeeded_off']} of {s['rounds'] - s['wasted']} | {s['succeeded_on']} of {s['rounds'] - s['wasted']} | "
                   f"{_round(s['first_success_off'])} / {_round(s['first_success_on'])} | "
                   f"{s['reached_model_on']} | {stopped} |")
    out += ["", "**Reading it.** Against the stand-in, the attacker cannot change what the model says, only whether "
            "its comment reaches it, so the \"reached the model\" column is the measurement there; the answer is "
            "then judged by the explanation check. Against Gemini both sides are real. A fix counts as a success "
            "only if it passed the compiler gate with a `print()` in it. Success is judged by words in what the user "
            "was told; every attempt and answer is saved in `evaluation/aivsai_results.json` to be read by hand.", ""]
    for run in runs:
        out.append(f"**{run.get('matchup', '')}, {run['goal']}**, the attacker's comments:")
        out.append("")
        for row in run["rows"]:
            if row["wasted"]:
                out.append(f"{row['round']}. ({row.get('wasted_why', 'no usable comment')})")
                continue
            mark = "succeeded with the layer on" if row["on"]["broken"] else (
                "reached the model, held" if row["on"]["reached_model"] else "stopped before the model")
            out.append(f"{row['round']}. `{row['comment'].replace('`', chr(39))}` ({mark})")
        out.append("")
    return out


def section():
    """Section 9 of results.md, from the saved live run (no model is asked here)."""
    if not RESULTS_FILE.is_file():
        return (["## 9. AI against AI: a model attacks the agent", "",
                 "Not measured yet: run `python evaluation/aivsai.py --live` (needs GEMINI_API_KEY).", ""],
                {"measured": False})
    data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    lines = report(data["runs"])
    lines.insert(2, f"Measured on {data['measured_on']} with {data.get('answered_as') or data.get('model', 'a real model')}.")
    lines.insert(3, "")
    on = sum(r["summary"]["succeeded_on"] for r in data["runs"])
    return lines, {"measured": True, "succeeded_on": on, "runs": len(data["runs"])}


def main():
    live = "--live" in sys.argv
    rounds = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 8
    if not live:
        os.environ["PARC_AGENT_LLM"] = "none"
    runs = run_all(live, rounds, use_cache="--fresh" not in sys.argv)
    lines = report(runs)
    if live:
        RESULTS_FILE.write_text(json.dumps({"measured_on": time.strftime("%Y-%m-%d"), "model": llm.status()["model"],
                                            "answered_as": llm.Gemini.last_version, "runs": runs},
                                           indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {RESULTS_FILE.name}; models: {llm.status()['model']}, last answered as {llm.Gemini.last_version}.")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
