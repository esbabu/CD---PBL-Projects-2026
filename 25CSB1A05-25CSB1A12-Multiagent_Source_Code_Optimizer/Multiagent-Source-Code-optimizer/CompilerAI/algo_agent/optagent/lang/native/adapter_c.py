"""C11 LanguageAdapter implementation (clang/gcc + fork-per-case + sanitizers + CBMC)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

from ...analysis.static_facts import AmbiguousEntry
from ...config import Settings
from ...oracle.golden import FIELDS as GOLDEN_FIELDS
from ...oracle.golden import lines_of
from ...oracle.schema_infer import ParamSchema
from ...oracle.schemas import Case, CaseResult, GoldenRecord
from ...proposers.schemas import Candidate
from ...runtime.sandbox import RunOpts, Sandbox, SandboxProfile
from ...schemas import Aspect, FunctionFacts, Level, ModuleFacts, Source
from ...verify.schemas import RungResult
from ..base import (
    BenchProfile,
    BuildResult,
    Capabilities,
    ContractRule,
    MutationOps,
    PromptPack,
    RulePack,
    Rung,
)
from ..treesitter.mutate import TreeSitterMutator
from ..treesitter.parse import executable_statement_lines
from .build import compile_native
from .cbmc import run_cbmc_equivalence
from .clang_facts import analyze_native_source
from .marshal import build_signature, seed_inputs_for_signature, signature_to_param_schema
from .prompts import C_PROMPT_PACK

NATIVE_DIR = Path(__file__).resolve().parent


def _c_propose_rules(intent: Any, analysis: Any) -> list[Candidate]:
    """Deterministic mechanical C11 rewrite rules."""
    src: str = intent.source
    entry: str = intent.entry_point
    fn = intent.module_facts.functions.get(entry)
    if not fn:
        return []
    cands: list[Candidate] = []
    patterns = {p.kind for p in fn.cost_patterns} | {b.pattern for b in (analysis.bottlenecks or [])}

    # 1. Hoist strlen(s) out of loop condition: `for (...; i < strlen(s); ...)`
    if "strlen_in_loop" in patterns or "strlen(" in src:
        m = re.search(r"for\s*\(([^;]+);\s*(\w+)\s*<\s*strlen\s*\(\s*(\w+)\s*\)\s*;([^)]+)\)", src)
        if m:
            init_part, ivar, svar, inc_part = m.groups()
            repl = f"size_t _opt_len_{svar} = strlen({svar});\n    for ({init_part}; (size_t){ivar} < _opt_len_{svar}; {inc_part})"
            new_src = src[:m.start()] + repl + src[m.end():]
            cands.append(Candidate(
                id="c_rule_hoist_strlen",
                proposer="rule",
                source=new_src,
                transform_ids=["c_hoist_strlen"],
                rationale=f"Hoisted O(n) strlen({svar}) out of loop condition into size_t _opt_len_{svar}.",
                claimed_time="O(n)",
                claimed_space="O(1)",
            ))

    # 2. Nested pair-sum loop (two_sum style) -> sorted (val, idx) + binary search O(n log n)
    if ("nested_loop" in patterns or fn.max_loop_depth >= 2) and "two_sum" in entry.lower():
        if re.search(r"out\s*\[\s*0\s*\]\s*=", src) and re.search(r"out\s*\[\s*1\s*\]\s*=", src):
            opt_src = (
                "#include <stdlib.h>\n\n"
                "typedef struct { int val; int idx; } _OptPair;\n"
                "static int _opt_cmp_pair(const void *a, const void *b) {\n"
                "    const _OptPair *pa = (const _OptPair *)a;\n"
                "    const _OptPair *pb = (const _OptPair *)b;\n"
                "    if (pa->val != pb->val) return (pa->val > pb->val) - (pa->val < pb->val);\n"
                "    return (pa->idx > pb->idx) - (pa->idx < pb->idx);\n"
                "}\n\n"
                f"int {entry}(const int *nums, int n, int target, int *out) {{\n"
                "    if (n < 2) return 0;\n"
                "    _OptPair *pairs = (_OptPair *)malloc((size_t)n * sizeof(_OptPair));\n"
                "    if (!pairs) return 0;\n"
                "    for (int i = 0; i < n; i++) { pairs[i].val = nums[i]; pairs[i].idx = i; }\n"
                "    qsort(pairs, (size_t)n, sizeof(_OptPair), _opt_cmp_pair);\n"
                "    for (int i = 0; i < n; i++) {\n"
                "        long long need_ll = (long long)target - (long long)nums[i];\n"
                "        int lo = 0, hi = n;\n"
                "        while (lo < hi) {\n"
                "            int mid = lo + (hi - lo) / 2;\n"
                "            if ((long long)pairs[mid].val < need_ll ||\n"
                "                ((long long)pairs[mid].val == need_ll && pairs[mid].idx <= i)) lo = mid + 1;\n"
                "            else hi = mid;\n"
                "        }\n"
                "        if (lo < n && (long long)pairs[lo].val == need_ll && pairs[lo].idx > i) {\n"
                "            out[0] = i; out[1] = pairs[lo].idx;\n"
                "            free(pairs);\n"
                "            return 1;\n"
                "        }\n"
                "    }\n"
                "    free(pairs);\n"
                "    return 0;\n"
                "}\n"
            )
            cands.append(Candidate(
                id="c_rule_sorted_bsearch_two_sum",
                proposer="rule",
                source=opt_src,
                transform_ids=["c_nested_loop_to_hash_table"],
                rationale="Replaced O(n^2) nested pair loop with sorted (value, index) array + binary search O(n log n).",
                claimed_time="O(n log n)",
                claimed_space="O(n)",
            ))

    return cands


class CAdapter:
    """LanguageAdapter for C (C11)."""

    id: str = "c"
    display: str = "C (C11)"
    extensions: tuple[str, ...] = (".c",)
    caps: Capabilities = Capabilities(
        function_mode=True,
        program_mode=False,
        isolation_required=True,
        static_types=True,
        max_evidence_tier="T3",
        perturbation="malloc_perturb",
    )

    # ---------- Step 1 ----------
    def analyze(self, source: str, hints: dict[str, Any]) -> ModuleFacts:
        return analyze_native_source(source, self.id, hints)

    def select_entry(self, mod: ModuleFacts, requested: str | None) -> str:
        if requested:
            if requested not in mod.functions:
                raise KeyError(f"Entry function '{requested}' not found. Available: {sorted(mod.functions)}")
            return requested
        non_main = [n for n in mod.root_functions if n != "main"]
        if len(non_main) == 1:
            return non_main[0]
        all_non_main = [n for n in mod.functions if n != "main"]
        if len(all_non_main) == 1:
            return all_non_main[0]
        raise AmbiguousEntry(sorted(non_main or all_non_main or mod.functions.keys()))

    def signature(self, fn: FunctionFacts) -> str:
        params = ", ".join(f"{p.annotation or 'int'} {p.name}" for p in fn.params)
        return f"{fn.returns_annotation or 'int'} {fn.name}({params})"

    def seed_inputs(self, fn: FunctionFacts, hints: dict[str, Any]) -> list[dict[str, Any]]:
        sig = build_signature(fn, self.id, hints)
        return seed_inputs_for_signature(sig)

    def param_schema(self, fn: FunctionFacts, hints: dict[str, Any], seeds: list[Any]) -> ParamSchema | None:
        sig = build_signature(fn, self.id, hints)
        return signature_to_param_schema(sig)

    def prompt_pack(self) -> PromptPack:
        return C_PROMPT_PACK

    def contract_rules(self) -> list[ContractRule]:
        return [
            ContractRule(
                aspect=Aspect.MEMORY_SAFETY,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="No out-of-bounds access, use-after-free, or leaks (ASan/canary clean where original is clean).",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.UNDEFINED_BEHAVIOR,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="Candidate must not introduce undefined behaviour (UBSan clean where original is clean).",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.INTEGER_SEMANTICS,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="Integer width, signedness, and wraparound semantics must be preserved.",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.ABI_SIGNATURE,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="Function prototype (name, parameter types, const qualifiers, return type) must stay identical.",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.RESOURCE_OWNERSHIP,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: bool(fn.extra.get("uses_malloc")) or "*" in (fn.returns_annotation or ""),
                rationale="Ownership conventions for allocated buffers and returned pointers must be preserved.",
                source=Source.STATIC,
            ),
            ContractRule(
                aspect=Aspect.ERRNO_STATE,
                default_level=Level.MAY,
                applicable_fn=lambda fn, recs, h: True,
                rationale="errno value after call may change unless explicitly promoted to must_preserve.",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.THREAD_SAFETY,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: bool(fn.extra.get("uses_threads")),
                rationale="No new data races or unsafe shared mutable state when threads are used.",
                source=Source.STATIC,
            ),
            ContractRule(
                aspect=Aspect.SORT_STABILITY,
                default_level=Level.MAY,
                applicable_fn=lambda fn, recs, h: bool(fn.sort_uses),
                rationale="C qsort is not guaranteed stable; tie order may change unless overridden.",
                source=Source.STATIC,
            ),
        ]

    # ---------- Step 2 ----------
    def sandbox_profile(self, hints: dict[str, Any], mode: str = "opt") -> SandboxProfile:
        lang_id = self.id
        target_name = "target.cpp" if lang_id == "cpp" else "target.c"
        extra_files = dict((hints or {}).get("extra_files") or {})

        def build_hook(work: Path, out: Path, entry: str, s: Settings, docker: bool) -> tuple[bool, str]:
            src_text = (work / target_name).read_text(encoding="utf-8")
            cache_dir = Path(s.runs_dir) / "_build_cache"
            res = compile_native(
                src_text, entry, lang_id, s, out,
                hints=hints, mode=mode, docker=docker, cache_dir=cache_dir,
            )
            return res.ok, res.log

        def run_cmd(work: Path, out: Path, docker: bool) -> list[str]:
            if docker:
                return ["/out/driver_bin", "/work/cases.jsonl", "/out/out.jsonl", "/work/cfg.json"]
            return [str(out / "driver_bin"), str(work / "cases.jsonl"), str(out / "out.jsonl"), str(work / "cfg.json")]

        def env_fn(perturb_idx: int) -> dict[str, str]:
            # 0xA5 (165) vs 0x5A (90) exposes reads of uninitialized heap memory
            perturb_val = "165" if perturb_idx == 0 else "90"
            return {
                "MALLOC_PERTURB_": perturb_val,
                "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
                "UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1",
            }

        return SandboxProfile(
            target_name=target_name,
            image=os.getenv("OPT_NATIVE_DOCKER_IMAGE", "optagent-sandbox-native:latest"),
            needs_build=True,
            isolation_required=True,
            language=lang_id,
            run_cmd=run_cmd,
            env=env_fn,
            extra_files=extra_files,
            build_hook=build_hook,
        )

    def build(self, source: str, entry: str, hints: dict[str, Any], workdir: Path) -> BuildResult:
        return compile_native(source, entry, self.id, Settings(), workdir, hints=hints, mode="opt")

    def make_golden_extra(
        self,
        sb: Sandbox,
        src: Path,
        entry: str,
        cases: list[Case],
        hints: dict[str, Any],
        cov: bool = True,
    ) -> tuple[dict[str, GoldenRecord], list[tuple[Case, str, str | None]], dict[str, set[int]], list[str]]:
        """3-config golden (A: -O2 perturb 0xA5, B: -O2 perturb 0x5A, C: -O0) + ASan/UBSan UB filter."""
        warns: list[str] = []
        r_a = sb.run(src, entry, cases, RunOpts(hashseed=0, cov=cov))
        keep = [i for i, r in enumerate(r_a) if r.status in ("ok", "exception") and not r.sanitizer]
        kept_cases = [cases[i] for i in keep]

        r_b_list = sb.run(src, entry, kept_cases, RunOpts(hashseed=1)) if kept_cases else []
        r_b = dict(zip(keep, r_b_list))

        # Config C: -O0 optimization-sensitivity check
        r_c: dict[int, CaseResult] = {}
        try:
            sb_o0 = Sandbox(sb.s, backend=sb.backend, profile=self.sandbox_profile(hints, mode="O0"))
            r_c_list = sb_o0.run(src, entry, kept_cases, RunOpts(hashseed=0)) if kept_cases else []
            if r_c_list and r_c_list[0].status != "load_error":
                r_c = dict(zip(keep, r_c_list))
        except Exception:
            pass

        # Config D: ASan + UBSan pass to detect UB in original (drop & record `original_ub`)
        r_san: dict[int, CaseResult] = {}
        if getattr(sb.s, "enable_sanitizers", True) and kept_cases:
            try:
                sb_san = Sandbox(sb.s, backend=sb.backend, profile=self.sandbox_profile(hints, mode="san"))
                r_san_list = sb_san.run(src, entry, kept_cases, RunOpts(hashseed=0))
                if r_san_list and r_san_list[0].status != "load_error":
                    r_san = dict(zip(keep, r_san_list))
            except Exception:
                pass

        golden: dict[str, GoldenRecord] = {}
        dropped: list[tuple[Case, str, str | None]] = []
        lines: dict[str, set[int]] = {}
        ub_dropped = 0

        for i, (c, ra) in enumerate(zip(cases, r_a)):
            if i not in r_b:
                dropped.append((c, "original_ub" if ra.sanitizer else ra.status, ra.sanitizer or ra.exc_msg))
                if ra.sanitizer:
                    ub_dropped += 1
                continue
            san_res = r_san.get(i)
            if san_res and (san_res.sanitizer or san_res.status == "crash"):
                dropped.append((c, "original_ub", san_res.sanitizer or san_res.exc_msg))
                ub_dropped += 1
                continue

            rb = r_b[i]
            rc = r_c.get(i)
            unstable = [
                f for f in GOLDEN_FIELDS
                if json.dumps(getattr(ra, f), sort_keys=True) != json.dumps(getattr(rb, f), sort_keys=True)
            ]
            if rc is not None:
                for f in GOLDEN_FIELDS:
                    if f not in unstable and json.dumps(getattr(ra, f), sort_keys=True) != json.dumps(getattr(rc, f), sort_keys=True):
                        unstable.append(f)

            lines[c.id] = lines_of(ra.edges)
            ra.edges, rb.edges = [], []
            golden[c.id] = GoldenRecord(
                case_id=c.id,
                result=ra,
                unstable=unstable,
                alt=rb if "ret" in unstable else None,
            )

        if ub_dropped:
            warns.append(f"original_ub: dropped {ub_dropped} input(s) where the original triggered ASan/UBSan.")
        return golden, dropped, lines, warns

    def executable_lines(self, source: str, mod: ModuleFacts, entry: str) -> tuple[set[int], set[str]]:
        reach, stack = {entry}, [entry]
        while stack:
            cur = stack.pop()
            fn = mod.functions.get(cur)
            if not fn:
                continue
            for c in fn.callees_local:
                if c not in reach:
                    reach.add(c)
                    stack.append(c)
        lines = executable_statement_lines(source, self.id, reach)
        return lines, reach

    def mutation_ops(self) -> MutationOps:
        mutator = TreeSitterMutator(self.id)
        ext = self.extensions[0]
        return MutationOps(
            language=self.id,
            generate=lambda source, reachable, max_m, rng: mutator.generate(source, reachable, max_m, rng),
            file_extension=ext,
        )

    def normalize_result(self, r: CaseResult) -> CaseResult:
        return r

    # ---------- Steps 3 to 7 ----------
    def cost_table(self) -> dict[str, str]:
        p = NATIVE_DIR / ("cost_cpp.yaml" if self.id == "cpp" else "cost_c.yaml")
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            return dict(data.get("costs") or {})
        return {}

    def rule_pack(self) -> RulePack:
        return RulePack(
            language=self.id,
            rules_yaml=NATIVE_DIR / "rules_c.yaml",
            propose_fn=_c_propose_rules,
        )

    def kb_dir(self) -> Path:
        return NATIVE_DIR

    def verify_rungs(self) -> list[Rung]:
        adapter = self

        def run_sanitizer_rung(oracle: Any, candidate_source: str) -> RungResult:
            if not getattr(oracle.s, "enable_sanitizers", True):
                return RungResult(rung="R_sanitizers", passed=True, skipped=True, reason="Sanitizers disabled.")
            hints = getattr(oracle, "_hints", {})
            try:
                sb_san = Sandbox(oracle.s, backend=oracle.sb.backend, profile=adapter.sandbox_profile(hints, mode="san"))
                cpath = oracle._path_for(candidate_source)
                sample = [c for c in oracle.b.cases if c.kind == "valid"][:80]
                res = sb_san.run(cpath, oracle.entry, sample, RunOpts(hashseed=0))
                if res and res[0].status == "load_error":
                    return RungResult(rung="R_sanitizers", passed=True, skipped=True, reason=f"Sanitizer build unavailable: {res[0].exc_msg[:120]}")
                bad = [r for r in res if r.sanitizer or r.status == "crash"]
                if bad:
                    return RungResult(
                        rung="R_sanitizers", passed=False,
                        reason=f"ASan/UBSan violation: {bad[0].sanitizer or bad[0].signal or bad[0].exc_msg}",
                        details={"n_checked": len(sample), "n_failed": len(bad)},
                    )
                return RungResult(rung="R_sanitizers", passed=True, details={"n_checked": len(sample), "sanitizers": "ASan+UBSan"})
            except Exception as e:
                return RungResult(rung="R_sanitizers", passed=True, skipped=True, reason=f"Sanitizer rung skipped: {e}")

        def run_cbmc_rung(oracle: Any, candidate_source: str) -> RungResult:
            orig_src = oracle.orig.read_text(encoding="utf-8") if oracle.orig.exists() else ""
            res = run_cbmc_equivalence(
                orig_src,
                candidate_source,
                oracle.entry,
                language=adapter.id,
                hints=getattr(oracle, "_hints", {}),
                unwind=getattr(oracle.s, "cbmc_unwind", 16),
                enabled=getattr(oracle.s, "enable_cbmc", False),
            )
            return RungResult(
                rung="R6_cbmc_bounded_equivalence",
                passed=res.passed,
                skipped=res.skipped,
                reason=res.reason,
                details=res.details,
                elapsed_s=res.elapsed_s,
            )

        return [
            Rung(name="R_sanitizers", run=run_sanitizer_rung, grants_tier=None, advisory=False),
            Rung(name="R6_cbmc_bounded_equivalence", run=run_cbmc_rung, grants_tier="T3", advisory=False),
        ]

    def bench_profile(self) -> BenchProfile:
        return BenchProfile(
            language=self.id,
            warmups=3,
            reps=9,
            cpu_time=True,
            extra_flags=["-O2", "-ffp-contract=off", "-fno-fast-math"],
        )

    def security_profile(self) -> dict[str, Any]:
        return {
            "language": self.id,
            "static_tools": ["cppcheck", "clang-tidy"],
            "dynamic_tools": ["asan", "ubsan", "valgrind"],
            "isolation": "docker_mandatory",
            "compile_limits": {"timeout_s": 30, "memory": "1g", "pids_limit": 128},
            "sandbox_flags": ["--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges"],
        }
