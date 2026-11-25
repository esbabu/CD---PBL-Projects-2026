# Secure Agentic AI and Retrieval-Augmented Generation (RAG)

How the Code Comment Generator's **fix-and-verify agent** and its **RAG guidance system**
work, why they are built the way they are, and what keeps them safe. Every number in this
document was measured with the commands in [§9](#9-reproducing).

| | Where |
|---|---|
| Agent loop | `src/agent/fixer.py` |
| Fix strategies | `src/agent/strategies.py` |
| Patch verifier | `src/agent/verify.py` |
| Optional local LLM | `src/agent/llm_strategy.py` |
| RAG package | `src/rag/` (`knowledge.py`, `retriever.py`, `memory.py`, `guidance.py`, `evaluate.py`) |
| Bundled knowledge | `src/rag/data/knowledge.json` |
| Tests | `tests/test_agent.py`, `tests/test_agent_rules50.py`, `tests/test_rag.py` |

---

## 1. The ideas in one page

**An agent** is a program that works toward a goal in a loop. It looks at the situation,
decides on an action, carries it out, checks the result, and decides what to do next.
That differs from a single function call, which maps one input to one output and stops.
Our agent's goal is *"remove the security findings in this file without breaking anything
else"*. Its loop is **plan → act → observe → decide**:

```
            ┌───────────────────────────────────────────────────────────────┐
            │                    for each active finding                    │
            ▼                                                               │
   ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐   ┌─────┴──────┐
   │ PLAN         │──►│ ACT          │──►│ OBSERVE (verifier)     │──►│ DECIDE     │
   │ pick the next│   │ make a       │   │ (a) parses             │   │ accept, or │
   │ strategy for │   │ patched COPY │   │ (b) finding gone       │   │ next       │
   │ the rule     │   │ of the code  │   │ (c) nothing new        │   │ strategy   │
   └──────────────┘   └──────────────┘   │ (d) only that function │   │ (max 3),   │
          ▲                              └────────────────────────┘   │ else manual│
          │ no strategy / all failed → RETRIEVE guidance (RAG)         └────────────┘
```

**Retrieval-Augmented Generation (RAG)** first *retrieves* relevant passages from a
knowledge base, then uses them to *augment* what is produced: the answer to a person, or
the prompt of a language model. The benefit is grounding. The output is based on specific,
checkable material instead of whatever a model happens to remember. Every passage carries
its source, so a person can check where advice came from.

**"Secure"** here means two things:
1. **The agent cannot make the code worse.** Every change must pass four independent
   checks by the analyzer before it is accepted.
2. **The AI parts cannot be hijacked.** The optional LLM and the knowledge base are
   treated as untrusted *proposals* and *data*, never as commands. Nothing they produce is
   executed or accepted without verification.

---

## 2. Where the agent fits in the project

```
source file ──► security analyzer (50 rules, taint + AST) ──► findings
                                                                │
                         ┌──────────────────────────────────────┘
                         ▼
               fix-and-verify agent ──► verified patches  ──► diff for the user (Accept / Discard)
                         │                     │
                         │                     └──► (--learn) verified-fix memory ──┐
                         ▼                                                          │
               findings it cannot fix ──► RAG retrieval ◄── knowledge base ◄────────┘
                                              │           (rule cards, examples, memory)
                                              ▼
                                   guidance shown with the finding
                                   (and, with --llm, reference data in the prompt)
```

The agent never changes the input file. It returns a patched copy, the step-by-step trace
and a unified diff. In the GUI (**Security → Auto-fix**), the user accepts or discards the
patch. On the command line, `--out` writes the copy.

---

## 3. The agent in detail

### 3.1 Plan: choosing a strategy

Findings are handled **one at a time, in line order**. After every accepted patch the code
is analysed again, so the next fix starts from verified code. Line numbers shift as code
changes, so a finding is identified by *(rule, function, the sink's line of code)*.

For each finding the agent lists the strategies registered for its rule (in order), plus
the optional LLM strategy last. It tries at most `--max-attempts` of them (default 3).

| Rule | Strategy | What it rewrites |
|---|---|---|
| SEC005 SQL injection | `sql-param-qmark`, `sql-param-format` | string-built query → placeholders + parameter tuple |
| SEC002 command injection | `cmd-argv-list`, `cmd-shlex-quote` | `os.system`/`shell=True` → argument list without a shell; else `shlex.quote()` |
| SEC010 unsafe YAML | `yaml-safe-load` | `yaml.load` → `yaml.safe_load` |
| SEC004 weak hash | `hash-sha256` | MD5/SHA-1 → SHA-256 |
| SEC001 eval | `eval-literal-eval` | `eval(x)` → `ast.literal_eval(x)` |
| SEC018 XXE | `xxe-disable-entities` | external entities switched off |
| SEC024 regex injection | `regex-escape` | user pattern wrapped in `re.escape()` |
| SEC029 debug mode | `debug-off` | `debug=True` → `debug=False` |
| SEC030 TLS verification | `tls-verify-on` | `verify=False` → `verify=True` |
| SEC042 tar extraction | `tar-data-filter` | `extractall(d)` → `extractall(d, filter="data")` |
| SEC043 auto-escaping | `jinja-autoescape` | `jinja2.Environment(...)` → `autoescape=True` |
| SEC044 cookie flags | `cookie-secure` | `set_cookie(...)` → `secure=True, httponly=True` |

### 3.2 Act: producing a patch

Strategies are **deterministic AST rewrites**:
- They find the exact nodes using Python's `ast` positions and replace only those
  character spans.
- No regular expression ever edits the source.
- A needed import is added after the existing imports.

A strategy **declines** with a reason when a mechanical fix would be wrong. Examples:
- a value spliced in as SQL syntax (`ORDER BY <column>`), which needs an allow-list;
- a query built by the caller;
- `exec` of a statement, which `literal_eval` cannot replace;
- SSRF and open redirect, which need a human decision about which hosts are allowed.

Declining is safer than guessing.

### 3.3 Observe: the verifier (the core of "secure")

`verify.verify_patch` accepts a patch only if **all four** checks pass:

| Check | How | Prevents |
|---|---|---|
| (a) parses | `ast.parse(patched)` | broken code |
| (b) finding gone | rerun the analyzer: fewer findings of this rule in this function | "fixes" that do not fix |
| (c) nothing new | no (rule, function) pair is reported more often than before | trading one vulnerability for another |
| (d) in scope | `difflib` line diff: only lines of the reported function changed (plus a new top-level import) | edits to unrelated code |

The verifier is the same compiler-style analyzer that found the problem (taint analysis
over the IR and CFG), not a language model. That makes the loop **closed**: the agent's
"opinion" that a fix works is never trusted on its own.

### 3.4 Decide

- **Accept:** use the patched code, re-analyse, and move to the next finding.
- **Reject:** record the failed checks in the trace and try the next strategy.
- **Give up:** after the last strategy, mark the finding *needs manual fix* and attach
  retrieved guidance (§4).

Every step is an `AgentStep` (`finding`, `plan`, `act`, `observe`, `decide`, `done`). The
CLI (`--trace`), the JSON output and the GUI show the same trace.

### 3.5 The optional LLM strategy

With `--llm` and a local Ollama server (`localhost:11434`), a language model is tried
after the templates.
- **Input:** the function, the finding, the evidence trace, the remediation text, and the
  top RAG passages (§4.5).
- **Output:** a rewritten function only.
- **Checks:** its reply is treated exactly like a template patch. It must be a single
  function with the same name, and it goes through the four verifier checks.
- **Offline:** without a model the strategy is skipped and everything else still works.
- **Privacy:** no code leaves the machine. Only a local server is contacted.

---

## 4. The RAG system in detail

### 4.1 Why RAG here

The agent can fix 12 of the 50 rules mechanically. For everything else (XSS, path
traversal, LDAP injection, SSRF, …) the user needs to know **how to fix this particular
finding**. A generic remediation sentence is weak, and an LLM answer from memory is
unverifiable. Retrieval gives concrete, sourced material instead:
- the rule's explanation;
- a worked vulnerable → fixed example;
- best of all, a fix that the verifier accepted earlier for similar code.

### 4.2 The knowledge base (`knowledge.py`)

| Document kind | Count | Content | Source label shown to the user |
|---|---|---|---|
| `rule` | 50 | rule id, title, CWE, category, severity, *why it matters*, *how to fix* | `rule catalogue (src/security/rules.py) — CWE-xx` |
| `example` | 50 | a hand-written vulnerable snippet and its fixed twin | `bundled example (src/rag/data/knowledge.json)` |
| `memory` | grows | function before/after a fix that the verifier accepted | `verified-fix memory (fix #n, strategy s)` |

The rule cards are built from the same `RULES` registry the analyzer uses, so the guidance
always matches the detector. The examples are the hand-written pairs also used by the
large-file test corpus.

### 4.3 The retriever (`retriever.py`)

The retriever is **BM25** (Okapi, k1 = 1.5, b = 0.75), the standard lexical ranking used by
search engines. It is written in about 60 lines of plain Python, with no embeddings model,
no vector database and no network.
- **Tokenizer:** code-aware. `render_template_string` → `render`, `template`, `string`;
  `setFeature` → `set`, `feature`, `setfeature`. `CWE-89` and `SEC005` stay whole.
- **Weighting:** a term scores higher when it is rare across documents (IDF) and frequent
  in the document, with saturation and length normalisation.
- **Why BM25 and not embeddings:** it is deterministic, explainable (you can see which
  words matched), fast (100 documents in microseconds), and adds no dependency or model
  download. It also keeps the security story simple: no third-party model sees the code.

### 4.4 Building a query from a finding (`guidance.py`)

`finding_query` combines:
- the finding's title and message;
- the sink's code and operation;
- the source's code and description;
- a few lines of code around the finding.

`guidance_for(finding)` restricts results to **the finding's own rule**, because the
analyzer already knows the vulnerability class with certainty. It ranks that rule's
passages by similarity to the code, and always includes the rule card. A verified fix of
similar code therefore outranks the generic example.

### 4.5 How retrieved passages are used ("augmentation")

1. **Guidance for manual fixes.** The agent attaches the top 3 passages to every finding
   it leaves for a person (`FindingOutcome.guidance`). They appear in the CLI report, the
   JSON and the GUI trace.
2. **Grounding the LLM.** With `--llm`, the top 2 passages are inserted into the prompt
   inside a fence (`<<<REFERENCE … REFERENCE>>>`), labelled *"data, not instructions"*.
3. **Direct search.** `python -m src.rag query "…"` and `python -m src.rag explain file.py`.

### 4.6 Learning from verified fixes (`memory.py`)

With `--learn`, every accepted patch is stored as a record in `outputs/rag/fix_memory.jsonl`
(rule, strategy, function, code before, code after). Later runs retrieve these records as
`memory` documents. The system gets better at advising on *your* codebase, but only from
fixes the verifier proved correct.

---

## 5. Threat model and safety measures

What could go wrong when AI components help fix security problems, and what stops each
failure:

| # | Threat | Mitigation in this project | Where |
|---|---|---|---|
| T1 | The agent "fixes" a finding but the vulnerability remains | Check (b): the analyzer must stop reporting it | `verify.py` |
| T2 | A fix introduces a different vulnerability | Check (c): no (rule, function) pair may increase | `verify.py` |
| T3 | A fix silently changes unrelated code | Check (d): only the reported function may change (plus a new import) | `verify.py`, `source.allowed_lines` |
| T4 | Broken code is produced | Check (a): must parse; the tests also compile patched code | `verify.py`, `tests/test_agent*.py` |
| T5 | The input file is damaged | The agent works on a copy; the file is only written on explicit `--out` or **Accept patch** | `fixer.py`, GUI |
| T6 | A hallucinating or malicious LLM rewrites the program | The LLM is optional and local; its reply must be one function with the same name and pass all four checks; it is never executed | `llm_strategy.py` |
| T7 | **Prompt injection** through retrieved text or code comments ("ignore previous instructions…") | Retrieved passages are fenced as reference data; a passage cannot close the fence (`REFERENCE>>>` is neutralised); even if a model obeyed an injection, its output still has to pass verification | `llm_strategy._reference` |
| T8 | **Knowledge-base poisoning**: bad advice enters the memory | Only patches the verifier *accepted* are stored; `--learn` is off by default; the bundled knowledge is read-only data in the repository | `fixer.py`, `memory.remember` |
| T9 | Tampering with the memory file by hand | Each record carries a SHA-256 digest over its fields; records whose digest does not match, or that are not valid JSON or valid Python, are skipped on load | `memory.load` |
| T10 | Secrets leaking into the knowledge base | String literals assigned to names like `password`, `token`, `api_key` are masked (`****`) before a record is stored | `memory._clean` |
| T11 | Oversized or junk records slow the system or inject huge text | Code fields are capped at 4,000 characters and must parse as Python; duplicates are not stored | `memory._clean`, `memory.remember` |
| T12 | Code sent to an external service | No network access in the RAG; the LLM strategy talks only to `localhost` | `rag/*`, `llm_strategy.py` |
| T13 | Retrieved text is executed | Retrieved passages are only displayed or placed in a prompt; nothing in `src/rag/` calls `eval`, `exec` or imports retrieved content | `src/rag/` |
| T14 | Infinite loop or runaway agent | Hard stop of `4 × findings + 4` iterations; at most `--max-attempts` strategies per finding; each finding is handled once | `fixer.py` |
| T15 | Over-trusting the agent | Every result says *fixed and verified* or *needs manual fix*, with the reason; verified means re-analysed and parsed, **not executed**; the user reviews the diff before accepting | CLI, GUI, docs |

The principle behind all of these: **AI components may propose, only the verifier may
accept, and only the user may apply.**

---

## 6. Measured results

### 6.1 Agent (no LLM, at most 3 attempts per finding)

| Dataset | Findings | Attempted | Fixed and verified | Needs manual fix | Patches rejected |
|---|---|---|---|---|---|
| Labelled fixtures | 74 | 43 | 25 | 49 | 0 |
| OWASP BenchmarkPython (1230 files) | 2033 | 164 | 130 | 1903 | 0 |

On OWASP:
- weak hash 71/71;
- SQL injection 5/5;
- YAML 5/5;
- XXE 9/9;
- cookie flags 24/24;
- `eval` 16/35 (the rest are `exec`, which the agent declines);
- command injection 0/15 (`sh -c` built across branches, left for a person).

No patch was rejected by the verifier, because the strategies decline instead of guessing.
The rejection path is covered by tests that use a deliberately bad strategy.

### 6.2 RAG retrieval

`python -m src.rag evaluate` scores **free-text retrieval from raw vulnerable code**.
- **Queries:** 452 OWASP BenchmarkPython true-vulnerability cases in 14 categories.
- **Ground truth:** OWASP's own category label. The analyzer is not used.
- **Scoring:** a hit at rank k means a document of a correct rule is among the top k.

| Measure | Value |
|---|---|
| recall@1 | 0.493 |
| recall@3 | 0.655 |
| recall@5 | 0.810 |
| MRR | 0.615 |
| chance (1 of 50 rules) | 0.020 |

Per category: LDAP, XPath, XXE, SQL, weak hash and secure cookie are at 1.000 recall@1.
XSS (0.00) and weak randomness (0.00) are low. Every OWASP case contains the same HTML
response and random-number boilerplate, so code alone does not say which of those is the
problem. This is the harder setting. In the agent, retrieval is restricted to the rule the
analyzer already found, so only ranking within that rule matters.

### 6.3 Tests

`tests/test_rag.py` (14 tests) checks:
- the tokenizer and BM25 ranking;
- coverage of all 50 rules;
- free-text retrieval for five rules;
- guidance restricted to the finding's rule;
- memory rejecting invalid or duplicate records and masking credentials;
- **tampered records being ignored**;
- the agent learning a verified fix and ranking it first afterwards;
- nothing being written without `--learn`;
- manual findings carrying guidance.

`tests/test_agent_rules50.py` checks that each new strategy fixes its snippet and that
the verifier accepts the fix.

---

## 7. Limitations (honest list)

- **Verified ≠ correct behaviour.** The verifier re-runs a static analyzer and parses the
  code; it does not run the program or its tests. Several fixes change behaviour on
  purpose (`check=True`, SHA-256 digests, `literal_eval`, `secure=True` cookies), so the
  diff must be reviewed.
- **The verifier is only as good as the analyzer.** A false negative of the analyzer can
  make a wrong fix look verified.
- **Coverage.** 12 of 50 rules have automatic strategies. The most common unfixed findings
  are XSS and path traversal.
- **Lexical retrieval.** BM25 matches words, not meaning. Synonyms the knowledge base does
  not use are missed, and free-text retrieval is weak for XSS and weak-randomness code (§6.2).
- **Small knowledge base.** One card and one example per rule. The memory grows only with
  `--learn` and only with mechanical fixes that the verifier accepted.
- **LLM not evaluated.** The LLM path is tested with a stub. No model quality numbers are
  claimed.
- **Single user.** The memory file is a local JSON-lines file with no locking. It is meant
  for one user's runs, not for a shared server.

---

## 8. Glossary

| Term | Meaning |
|---|---|
| Agent | A program that pursues a goal by repeatedly observing, choosing and taking actions, and checking the results |
| Plan / act / observe / decide | The four phases of our agent's loop |
| Strategy | A deterministic code rewrite for one rule |
| Verifier | The four checks that a patch must pass (parses, finding gone, nothing new, in scope) |
| RAG | Retrieval-Augmented Generation: retrieve relevant passages, then use them to ground the output |
| Knowledge base | The documents that can be retrieved: rule cards, examples, verified-fix memory |
| BM25 | A ranking formula that scores documents by term frequency and rarity, with length normalisation |
| recall@k | Fraction of queries with a correct document in the top k |
| MRR | Mean reciprocal rank: the average of 1/rank of the first correct document |
| Prompt injection | Text that tries to make a language model follow instructions hidden in its input |
| Poisoning | Getting wrong or malicious content into a knowledge base so it is retrieved later |
| Taint analysis | Tracking untrusted data from where it enters (source) to dangerous operations (sink) |

### Questions you may be asked

1. **Why not let the LLM fix everything?** Its output cannot be trusted. The verifier must
   check it anyway, and deterministic strategies are reproducible and explainable. The LLM
   is a last resort, off by default.
2. **What makes the agent "secure"?** A closed loop: proposals (template or LLM) are
   accepted only if the analyzer confirms the finding is gone, nothing new appeared, the
   code parses and nothing else changed. The file changes only when the user accepts.
3. **Why BM25 instead of embeddings?** It is offline, deterministic, explainable, needs no
   model download and is fast enough. The knowledge base is small and code vocabulary is
   distinctive.
4. **How do you stop the memory from learning bad fixes?** Only verifier-accepted patches
   are stored. Records are hashed, so tampering is detected, and credentials are masked.
5. **How is retrieval evaluated without circularity?** Against OWASP's own labels, with
   the vulnerable code as the query. The analyzer is not used to make the ground truth.
6. **What is prompt injection, and how is it handled?** Hidden instructions in input text.
   Retrieved text is fenced as data, and whatever the model returns must still pass
   verification.

---

## 9. Reproducing

```bash
python -m src.agent tests/security_fixtures/agent/mixed_demo.py --trace          # agent with trace
python -m src.agent tests/security_fixtures/agent/mixed_demo.py --learn          # also store verified fixes
python -m src.rag stats                                                          # knowledge-base contents
python -m src.rag query "jwt decode without verifying the signature"
python -m src.rag explain tests/inputs/demo_15_vulns.py                          # findings + guidance
python -m src.rag evaluate --out outputs/benchmarks/final/rag_retrieval_eval.json   # needs .benchmarks/ (benchmarks/fetch.py)
python -m src.agent.evaluate                                                     # agent on fixtures + OWASP
python -m pytest -q tests/test_rag.py tests/test_agent.py tests/test_agent_rules50.py
```
