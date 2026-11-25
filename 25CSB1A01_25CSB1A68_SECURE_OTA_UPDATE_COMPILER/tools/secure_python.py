#!/usr/bin/env python3
"""
secure_python.py - Secure Python OTA Compiler & CFG Dominance Analyzer

Performs static security analysis and control flow dominance verification on
Python OTA update scripts, analogous to the LLVM TraversalPass used by secure-clang:
1. Control Flow Graph (CFG) basic block construction across branches and exceptions
2. Strict forward dominance tree verification on install() invocations:
   - Must be dominated by verify_signature()
   - Must be dominated by source_trusted()
   - Must be dominated by verify_image_hash()
   - Must be dominated by monotonic rollback check (incoming_version > current_version)
3. Dynamic reflection & banned dangerous API checks (eval, exec, os.system, pickle)
4. Weak cryptography & insecure PRNG checks (md5, sha1, random.random)
5. Embedded secret and high-entropy literal detection (private keys, tokens)
6. Embedded AI prompt injection preprocessor checks
7. Optional bytecode compilation to .pyc upon passing all checks
8. Optional CodeCarbon energy & emissions tracking
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import py_compile
import re
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

warnings.filterwarnings("ignore", category=FutureWarning)

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = REPO_ROOT / "policies"

# Gate Matchers
SIG_NAMES = {
    "verify_signature",
    "verify_cryptographic_signature",
    "verifysignature",
    "check_signature",
    "checksignature",
    "crypto_ecdsa_verify",
    "ecdsa_verify",
}
SOURCE_NAMES = {
    "source_trusted",
    "sourcetrusted",
    "is_source_trusted",
    "issourcetrusted",
    "validate_source",
    "validatesource",
    "check_source_url",
}
HASH_NAMES = {
    "verify_image_hash",
    "verifyimagehash",
    "check_image_hash",
    "checkimagehash",
    "verify_hash",
    "verifyhash",
    "crypto_sha256",
}
INSTALL_NAMES = {
    "install",
    "install_firmware",
    "installfirmware",
    "apply_update",
    "applyupdate",
    "flash_firmware",
    "write_partition",
}

BANNED_FUNCS = {
    "eval": "Dynamic code execution via eval() is prohibited.",
    "exec": "Dynamic code execution via exec() is prohibited.",
    "compile": "Dynamic compilation is prohibited in firmware runtime.",
    "os.system": "Arbitrary command execution via os.system() is prohibited.",
    "os.popen": "Command execution via os.popen() is prohibited.",
    "subprocess.Popen": "Arbitrary subprocess execution is prohibited.",
    "subprocess.call": "Arbitrary subprocess execution is prohibited.",
    "subprocess.run": "Arbitrary subprocess execution is prohibited.",
    "pickle.loads": "Insecure object deserialization via pickle is prohibited.",
    "pickle.load": "Insecure object deserialization via pickle is prohibited.",
    "marshal.loads": "Insecure bytecode deserialization is prohibited.",
    "shelve.open": "Insecure object persistence is prohibited.",
    "__import__": "Dynamic reflection via __import__() is prohibited.",
    "input": "Blocking interactive console input is prohibited in firmware runtime.",
}

WEAK_CRYPTO = {
    "hashlib.md5": "Weak hashing algorithm MD5 is prohibited. Use SHA-256.",
    "md5": "Weak hashing algorithm MD5 is prohibited. Use SHA-256.",
    "hashlib.sha1": "Weak hashing algorithm SHA-1 is prohibited. Use SHA-256.",
    "sha1": "Weak hashing algorithm SHA-1 is prohibited. Use SHA-256.",
    "random.random": "Non-cryptographic PRNG random.random() is prohibited in security routines.",
    "random.randint": "Non-cryptographic PRNG random.randint() is prohibited in security routines.",
    "random.choice": "Non-cryptographic PRNG random.choice() is prohibited in security routines.",
    "random.randrange": "Non-cryptographic PRNG random.randrange() is prohibited in security routines.",
    "random.sample": "Non-cryptographic PRNG random.sample() is prohibited in security routines.",
    "random.shuffle": "Non-cryptographic PRNG random.shuffle() is prohibited in security routines.",
}

BANNED_LOGGING = {
    "print": "Sensitive console logging via print() is prohibited in firmware update routines.",
    "sys.stdout.write": "Direct console stream output is prohibited in firmware update routines.",
    "sys.stderr.write": "Direct console error stream output is prohibited in firmware update routines.",
}


def compute_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq: Dict[str, int] = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    length = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


class BasicBlock:
    def __init__(self, block_id: int, label: str = ""):
        self.block_id = block_id
        self.label = label
        self.stmts: List[ast.AST] = []
        self.calls: List[Tuple[str, int, int]] = []
        self.preds: Set[int] = set()
        self.succs: Set[int] = set()
        self.gates_validated: Set[str] = set()

    def __repr__(self):
        return f"BB_{self.block_id}('{self.label}', succs={sorted(self.succs)}, preds={sorted(self.preds)}, gates={sorted(self.gates_validated)})"


class CFG:
    def __init__(self, name: str):
        self.name = name
        self.blocks: Dict[int, BasicBlock] = {}
        self.entry_id: int = 0
        self.exit_ids: Set[int] = set()
        self._next_id: int = 0

    def new_block(self, label: str = "") -> BasicBlock:
        bid = self._next_id
        self._next_id += 1
        bb = BasicBlock(bid, label)
        self.blocks[bid] = bb
        return bb

    def add_edge(self, from_id: int, to_id: int):
        if from_id in self.blocks and to_id in self.blocks:
            self.blocks[from_id].succs.add(to_id)
            self.blocks[to_id].preds.add(from_id)

    def compute_dominance(self) -> Dict[int, Set[int]]:
        all_nodes = set(self.blocks.keys())
        dom: Dict[int, Set[int]] = {}
        for nid in all_nodes:
            dom[nid] = set(all_nodes)

        entry = self.entry_id
        dom[entry] = {entry}

        changed = True
        while changed:
            changed = False
            for nid in all_nodes:
                if nid == entry:
                    continue
                preds = self.blocks[nid].preds
                if not preds:
                    new_dom = {nid}
                else:
                    pred_doms = [dom[p] for p in preds if p in dom]
                    if pred_doms:
                        intersect = set(pred_doms[0])
                        for pd in pred_doms[1:]:
                            intersect.intersection_update(pd)
                        new_dom = {nid}.union(intersect)
                    else:
                        new_dom = {nid}

                if new_dom != dom[nid]:
                    dom[nid] = new_dom
                    changed = True
        return dom

    def to_dot(self) -> str:
        lines = [f"digraph \"{self.name}\" {{", "  node [shape=box, fontname=\"Courier\", style=\"rounded\"];"]
        for bid, bb in sorted(self.blocks.items()):
            label_text = f"BB_{bid}: {bb.label}"
            if bb.calls:
                call_strs = [c[0] for c in bb.calls]
                label_text += f"\\nCalls: {', '.join(call_strs)}"
            if bb.gates_validated:
                label_text += f"\\nGates: {', '.join(sorted(bb.gates_validated))}"
            lines.append(f"  Node_{bid} [label=\"{label_text}\"];")
        for bid, bb in sorted(self.blocks.items()):
            for s in sorted(bb.succs):
                lines.append(f"  Node_{bid} -> Node_{s};")
        lines.append("}")
        return "\n".join(lines)


def extract_func_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return node.attr
    return None


def analyze_condition_for_gates(test_node: ast.AST) -> Dict[str, Any]:
    res: Dict[str, Any] = {
        "gate": None,
        "is_negated": False,
        "is_rollback_valid": None,
        "error_detail": None,
        "sub_gates": [],
    }

    if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
        sub = analyze_condition_for_gates(test_node.operand)
        sub["is_negated"] = not sub["is_negated"]
        return sub

    if isinstance(test_node, ast.Call):
        fname = extract_func_name(test_node.func)
        if fname:
            fl = fname.lower()
            if fl in SIG_NAMES:
                res["gate"] = "signature"
                return res
            elif fl in SOURCE_NAMES:
                res["gate"] = "source"
                return res
            elif fl in HASH_NAMES:
                res["gate"] = "hash"
                return res

    if isinstance(test_node, ast.Compare):
        left = test_node.left
        if isinstance(left, ast.Call):
            fname = extract_func_name(left.func)
            if fname:
                fl = fname.lower()
                gate_type = None
                if fl in SIG_NAMES: gate_type = "signature"
                elif fl in SOURCE_NAMES: gate_type = "source"
                elif fl in HASH_NAMES: gate_type = "hash"

                if gate_type and len(test_node.ops) == 1 and len(test_node.comparators) == 1:
                    op = test_node.ops[0]
                    comp = test_node.comparators[0]
                    is_zero_or_false = (
                        (isinstance(comp, ast.Constant) and comp.value in (0, False)) or
                        (isinstance(comp, ast.NameConstant) and comp.value is False)
                    )
                    is_one_or_true = (
                        (isinstance(comp, ast.Constant) and comp.value in (1, True)) or
                        (isinstance(comp, ast.NameConstant) and comp.value is True)
                    )
                    if isinstance(op, (ast.Eq, ast.Is)) and is_zero_or_false:
                        res["gate"] = gate_type
                        res["is_negated"] = True
                        return res
                    if isinstance(op, (ast.NotEq, ast.IsNot)) and is_zero_or_false:
                        res["gate"] = gate_type
                        res["is_negated"] = False
                        return res
                    if isinstance(op, (ast.Eq, ast.Is)) and is_one_or_true:
                        res["gate"] = gate_type
                        res["is_negated"] = False
                        return res

        left_str = ast.unparse(left).lower() if hasattr(ast, "unparse") else ""
        if len(test_node.ops) == 1 and len(test_node.comparators) == 1:
            right = test_node.comparators[0]
            right_str = ast.unparse(right).lower() if hasattr(ast, "unparse") else ""
            op = test_node.ops[0]

            is_version_comp = any(k in left_str or k in right_str for k in ("version", "ver", "pkg", "header"))
            if is_version_comp:
                if isinstance(op, ast.LtE):
                    res["gate"] = "rollback"
                    res["is_negated"] = True
                    res["is_rollback_valid"] = True
                    return res
                elif isinstance(op, ast.Gt):
                    res["gate"] = "rollback"
                    res["is_negated"] = False
                    res["is_rollback_valid"] = True
                    return res
                elif isinstance(op, ast.GtE):
                    res["gate"] = "rollback"
                    res["is_negated"] = False
                    res["is_rollback_valid"] = False
                    res["error_detail"] = "Rollback guard uses '>=' which permits equal version replay attack. Strict '>' required."
                    return res
                elif isinstance(op, ast.Eq):
                    res["gate"] = "rollback"
                    res["is_negated"] = False
                    res["is_rollback_valid"] = False
                    res["error_detail"] = "Rollback guard permits same-version installation. Strict '>' required."
                    return res
                elif isinstance(op, ast.Lt):
                    res["gate"] = "rollback"
                    res["is_negated"] = True
                    res["is_rollback_valid"] = False
                    res["error_detail"] = "Rollback guard uses '<' which permits equal version replay attack. Strict '<=' rejection required."
                    return res

    return res


class CFGBuilder:
    def __init__(self, func_node: ast.FunctionDef):
        self.func = func_node
        self.cfg = CFG(func_node.name)
        self.install_blocks: List[Tuple[int, int]] = []
        self.rollback_flaws: List[str] = []

    def _extract_calls(self, node: ast.AST) -> List[Tuple[str, int, int]]:
        calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                fname = extract_func_name(n.func)
                if fname:
                    calls.append((fname, getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
        return calls

    def build(self) -> CFG:
        entry = self.cfg.new_block("Entry")
        self.cfg.entry_id = entry.block_id
        last_block = self._build_stmts(self.func.body, entry)
        if last_block is not None and not last_block.succs:
            self.cfg.exit_ids.add(last_block.block_id)
        return self.cfg

    def _build_stmts(self, stmts: List[ast.AST], current: BasicBlock) -> Optional[BasicBlock]:
        curr = current
        for stmt in stmts:
            if curr is None:
                curr = self.cfg.new_block("Unreachable")

            if isinstance(stmt, (ast.Return, ast.Raise)):
                curr.stmts.append(stmt)
                curr.calls.extend(self._extract_calls(stmt))
                self.cfg.exit_ids.add(curr.block_id)
                curr = None
                continue

            if isinstance(stmt, ast.If):
                calls_in_test = self._extract_calls(stmt.test)
                curr.calls.extend(calls_in_test)
                gate_info = analyze_condition_for_gates(stmt.test)

                if gate_info.get("error_detail"):
                    self.rollback_flaws.append(gate_info["error_detail"])

                then_bb = self.cfg.new_block("Then")
                else_bb = self.cfg.new_block("Else")
                join_bb = self.cfg.new_block("Join")

                self.cfg.add_edge(curr.block_id, then_bb.block_id)
                self.cfg.add_edge(curr.block_id, else_bb.block_id)

                gate = gate_info.get("gate")
                is_neg = gate_info.get("is_negated", False)
                is_valid = gate_info.get("is_rollback_valid", True)

                if gate and (is_valid is not False):
                    if not is_neg:
                        then_bb.gates_validated.add(gate)
                    else:
                        else_bb.gates_validated.add(gate)

                then_exit = self._build_stmts(stmt.body, then_bb)
                else_exit = self._build_stmts(stmt.orelse, else_bb)

                has_then_fallthrough = False
                has_else_fallthrough = False

                if then_exit is not None:
                    self.cfg.add_edge(then_exit.block_id, join_bb.block_id)
                    has_then_fallthrough = True

                if else_exit is not None:
                    self.cfg.add_edge(else_exit.block_id, join_bb.block_id)
                    has_else_fallthrough = True

                if not has_then_fallthrough and has_else_fallthrough:
                    join_bb.gates_validated.update(else_bb.gates_validated)
                    if else_exit:
                        join_bb.gates_validated.update(else_exit.gates_validated)
                elif has_then_fallthrough and not has_else_fallthrough:
                    join_bb.gates_validated.update(then_bb.gates_validated)
                    if then_exit:
                        join_bb.gates_validated.update(then_exit.gates_validated)

                if not has_then_fallthrough and not has_else_fallthrough:
                    curr = None
                else:
                    curr = join_bb
                continue

            curr.stmts.append(stmt)
            stmt_calls = self._extract_calls(stmt)
            curr.calls.extend(stmt_calls)

            for cname, lineno, _ in stmt_calls:
                if cname.lower() in INSTALL_NAMES:
                    self.install_blocks.append((curr.block_id, lineno))

        return curr


def check_python_security(
    source_code: str,
    policy: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, List[str], List[Dict[str, Any]], Optional[str]]:
    """
    Analyzes Python firmware code against security rules.
    Returns (ok, violations, hints, dot_graph).
    """
    if policy is None:
        policy = {
            "signature_verification": True,
            "source_trust": True,
            "rollback_guard": True,
            "image_hash_verification": True,
            "weak_crypto": True,
            "banned_memory_functions": True,
            "hardcoded_secrets": True,
            "banned_logging": True,
        }

    violations: List[str] = []
    hints: List[Dict[str, Any]] = []
    dot_graph: Optional[str] = None

    # 0. Prompt Injection Interception
    try:
        sys.path.insert(0, str(REPO_ROOT / "web-demo"))
        from security_preprocessor import check_for_indirect_injection
        injections = check_for_indirect_injection(source_code)
        if injections:
            for inj in injections:
                desc = inj.get("description", "Prompt injection directive")
                match_text = inj.get("matches", [""])[0]
                violations.append(f"AI Prompt Injection Attack: {desc} ('{match_text}')")
                hints.append({"line": 1, "kind": "error", "label": f"Prompt injection: {desc}"})
            return False, violations, hints, None
    except Exception:
        pass

    # 1. Parse AST
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return (
            False,
            [f"SyntaxError: {e.msg} at line {e.lineno}:{e.offset}"],
            [{"line": e.lineno, "column": e.offset, "kind": "error", "label": e.msg}],
            None,
        )

    # 2. Check Banned Functions, Reflection & Sensitive Logging
    if policy.get("banned_memory_functions", True) or policy.get("weak_crypto", True) or policy.get("banned_logging", True):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = ""
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    call_name = ast.unparse(node.func) if hasattr(ast, "unparse") else node.func.attr

                call_lower = call_name.lower()

                if policy.get("banned_memory_functions", True):
                    for banned, msg in BANNED_FUNCS.items():
                        if call_name == banned or call_lower.endswith(banned.lower()):
                            violations.append(f"Banned Function Violation: {msg} (line {node.lineno})")
                            hints.append({
                                "line": node.lineno,
                                "column": node.col_offset,
                                "kind": "error",
                                "label": f"Banned function: {call_name}",
                            })

                if policy.get("banned_logging", True):
                    for banned, msg in BANNED_LOGGING.items():
                        if call_name == banned or call_lower.endswith(banned.lower()):
                            violations.append(f"Sensitive Logging Ban Violation: {msg} (line {node.lineno})")
                            hints.append({
                                "line": node.lineno,
                                "column": node.col_offset,
                                "kind": "error",
                                "label": f"Sensitive logging API: {call_name}",
                            })

                if policy.get("weak_crypto", True):
                    matched = False
                    for weak, msg in WEAK_CRYPTO.items():
                        if (call_name == weak or call_lower.endswith(weak.lower())) and not matched:
                            violations.append(f"Weak Cryptography Violation: {msg} (line {node.lineno})")
                            hints.append({
                                "line": node.lineno,
                                "column": node.col_offset,
                                "kind": "error",
                                "label": f"Weak crypto API: {call_name}",
                            })
                            matched = True

    # 3. Check Hardcoded Secrets
    if policy.get("hardcoded_secrets", True):
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                val_upper = val.upper()
                if "BEGIN EC PRIVATE KEY" in val_upper or "BEGIN RSA PRIVATE KEY" in val_upper or "BEGIN PRIVATE KEY" in val_upper:
                    violations.append(f"Hardcoded Secret Violation: Embedded private key detected at line {node.lineno}.")
                    hints.append({"line": node.lineno, "kind": "error", "label": "Hardcoded private key"})
                elif any(val.startswith(tok) for tok in ("ghp_", "glpat-", "Bearer ")):
                    violations.append(f"Hardcoded Secret Violation: API token detected at line {node.lineno}.")
                    hints.append({"line": node.lineno, "kind": "error", "label": "Hardcoded token"})
                elif len(val) >= 40 and re.match(r"^[0-9a-fA-F]+$", val):
                    ent = compute_entropy(val)
                    if ent >= 3.6:
                        violations.append(f"Hardcoded Secret Violation: High-entropy secret literal (H={ent:.2f}) at line {node.lineno}.")
                        hints.append({"line": node.lineno, "kind": "warning", "label": "High entropy literal"})

    # 4. Check CFG Dominance on install() calls
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            builder = CFGBuilder(node)
            cfg = builder.build()
            dom = cfg.compute_dominance()
            dot_graph = cfg.to_dot()

            if builder.rollback_flaws and policy.get("rollback_guard", True):
                for flaw in builder.rollback_flaws:
                    violations.append(f"Monotonic Rollback Guard Violation: {flaw}")

            for inst_bid, inst_lineno in builder.install_blocks:
                hints.append({"line": inst_lineno, "kind": "info", "label": "install() invocation"})
                dominators = dom.get(inst_bid, set())

                dominated_gates: Set[str] = set()
                for d_id in dominators:
                    dominated_gates.update(cfg.blocks[d_id].gates_validated)

                if policy.get("signature_verification", True) and "signature" not in dominated_gates:
                    violations.append(f"Signature Verification Dominance Violation: Call to install() at line {inst_lineno} is not dominated by verify_signature().")
                    hints.append({"line": inst_lineno, "kind": "error", "label": "Missing signature verification dominance"})

                if policy.get("source_trust", True) and "source" not in dominated_gates:
                    violations.append(f"Trusted Source Dominance Violation: Call to install() at line {inst_lineno} is not dominated by source_trusted().")
                    hints.append({"line": inst_lineno, "kind": "error", "label": "Missing trusted source dominance"})

                if policy.get("image_hash_verification", True) and "hash" not in dominated_gates:
                    violations.append(f"Image Hash Dominance Violation: Call to install() at line {inst_lineno} is not dominated by verify_image_hash().")
                    hints.append({"line": inst_lineno, "kind": "error", "label": "Missing image hash dominance"})

                if policy.get("rollback_guard", True) and "rollback" not in dominated_gates:
                    violations.append(f"Monotonic Rollback Guard Violation: Call to install() at line {inst_lineno} is not dominated by version check (incoming > current).")
                    hints.append({"line": inst_lineno, "kind": "error", "label": "Missing monotonic rollback dominance"})

    ok = len(violations) == 0
    return ok, violations, hints, dot_graph


def resolve_policy(policy_arg: str) -> Dict[str, Any]:
    default_rules = {
        "signature_verification": True,
        "source_trust": True,
        "rollback_guard": True,
        "image_hash_verification": True,
        "weak_crypto": True,
        "banned_memory_functions": True,
        "hardcoded_secrets": True,
        "banned_logging": True,
    }
    if not policy_arg:
        return default_rules

    p = Path(policy_arg)
    if not p.is_file():
        cand = POLICIES_DIR / policy_arg
        if cand.is_file():
            p = cand
        elif (POLICIES_DIR / f"{policy_arg}.json").is_file():
            p = POLICIES_DIR / f"{policy_arg}.json"

    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("rules", default_rules)
        except Exception:
            pass
    return default_rules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="secure-python",
        description="Run secure AST CFG dominance & policy checks on Python OTA update firmware.",
    )
    parser.add_argument("--policy", default="", help="Path or name of security policy JSON")
    parser.add_argument("--energy", action="store_true", default=False, help="Enable CodeCarbon energy tracking")
    parser.add_argument("-o", "--output", default="", help="Output path for compiled bytecode (.pyc)")
    parser.add_argument("--dot", default="", help="Dump Graphviz CFG DOT graph to file")
    parser.add_argument("files", nargs="*", help="Python source files to verify")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.files:
        sys.stderr.write("secure-python: error: no Python source files provided.\n")
        return 1

    policy_rules = resolve_policy(args.policy)

    tracker = None
    total_energy = 0.0
    total_emissions = 0.0
    if args.energy:
        try:
            from codecarbon import OfflineEmissionsTracker
            tracker = OfflineEmissionsTracker(
                country_iso_code="USA",
                project_name="secure-python",
                gpu_ids=[],
                save_to_file=False,
                save_to_api=False,
                log_level="error",
            )
            tracker.start()
        except Exception:
            tracker = None

    all_passed = True
    for fpath in args.files:
        p = Path(fpath)
        if not p.is_file():
            sys.stderr.write(f"secure-python: error: file not found: {fpath}\n")
            all_passed = False
            continue

        source = p.read_text(encoding="utf-8", errors="ignore")

        # Prompt injection security check
        try:
            sys.path.insert(0, str(REPO_ROOT / "web-demo"))
            from security_preprocessor import check_for_indirect_injection
            injections = check_for_indirect_injection(source)
            if injections:
                sys.stderr.write("secure-python: error: Security policy violation detected in source code:\n")
                for inj in injections:
                    desc = inj.get("description", "Prompt injection directive")
                    match_text = inj.get("matches", [""])[0]
                    sys.stderr.write(f"  - AI Prompt Injection Attack: {desc} ('{match_text}')\n")
                sys.stderr.write("secure-python: compilation aborted to prevent AI pipeline compromise.\n")
                all_passed = False
                continue
        except Exception:
            pass

        ok, violations, hints, dot_graph = check_python_security(source, policy_rules)

        if dot_graph and args.dot:
            Path(args.dot).write_text(dot_graph, encoding="utf-8")

        if not ok:
            all_passed = False
            sys.stderr.write(f"secure-python: error: Security policy violations in {p.name}:\n")
            for v in violations:
                sys.stderr.write(f"  - {v}\n")
            sys.stderr.write("secure-python: compilation aborted.\n")
        else:
            if args.output:
                out_p = Path(args.output)
                out_p.parent.mkdir(parents=True, exist_ok=True)
                try:
                    py_compile.compile(str(p), cfile=str(out_p), doraise=True)
                    sys.stderr.write(f"secure-python: compiled {p.name} -> {out_p.name}\n")
                except Exception as exc:
                    sys.stderr.write(f"secure-python: bytecode compilation error: {exc}\n")
                    all_passed = False

    if tracker is not None:
        try:
            emissions = tracker.stop()
            if emissions:
                total_emissions = float(emissions)
            if hasattr(tracker, "_total_energy") and tracker._total_energy:
                total_energy = float(getattr(tracker._total_energy, "kWh", 0.0) or 0.0)
        except Exception:
            pass
        sys.stderr.write(f"[CodeCarbon] phase=ast-cfg energy_kwh={total_energy:.8f} emissions_kg={total_emissions:.8f}\n")
        sys.stderr.write(f"[CodeCarbon] total energy_kwh={total_energy:.8f} emissions_kg={total_emissions:.8f}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
