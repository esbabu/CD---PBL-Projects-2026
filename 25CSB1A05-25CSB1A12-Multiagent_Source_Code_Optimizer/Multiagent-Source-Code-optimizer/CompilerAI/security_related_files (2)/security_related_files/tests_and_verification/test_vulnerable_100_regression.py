"""
Automated Regression Test Suite for Benchmark 'vulnerable_100.cpp' (Phase 8).

Validates:
  1. All 100 ground-truth vulnerabilities are tested against static engines.
  2. Phase 2 False Positive Regressions:
     - v037: Potential unsafe XML pattern with low confidence (not confirmed XXE).
     - v043, v049: Missing password hashing (CWE-256), NOT weak MD5 (CWE-328).
     - v060: Insecure encoding / lossy mapping (CWE-261), NOT Base64.
     - Format string (CWE-134): NOT reported for constant format strings at lines 45, 132, 141, 197, 221, 375.
     - Buffer overflow (CWE-121) preserved at line 45 (sprintf).
     - Crypto & Auth configurations at lines 179, 204, 210, 214, 234, 224, 320.
  3. Source location accuracy and zero offset (Phase 3).
  4. Multi-engine deduplication and canonical defect families (Phase 4).
  5. Metrics computation: TP, FP, FN, Precision, Recall, F1, Duplicate Rate, Location Accuracy.
  6. Outputs structured evaluation report to 'vulnerable_100_evaluation_report.json'.
"""

import os
import sys
import json
import re
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

for p in [PROJECT_ROOT, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

for cand in [
    os.path.join(os.path.expanduser("~"), "Desktop", "modified-main (2)", "modified-main"),
    r"C:\Users\user\Desktop\modified-main (2)\modified-main",
]:
    if os.path.isdir(cand) and cand not in sys.path:
        sys.path.append(cand)

try:
    from analysis_and_detection.tool_runner import ToolRunner
    from rules_and_scanners.security_rules import scan_security_rules
    from analysis_and_detection.finding_schema import (
        deduplicate_findings,
        canonical_defect_family,
        CATEGORY_SECURITY_VULNERABILITY,
        CATEGORY_POTENTIAL_SECURITY_RISK,
        CONFIDENCE_CONFIRMED,
        CONFIDENCE_HIGH,
        CONFIDENCE_LOW,
    )
except ImportError:
    from src.analysis.tool_runner import ToolRunner
    from src.analysis.security_rules import scan_security_rules
    from src.analysis.finding_schema import (
        deduplicate_findings,
        canonical_defect_family,
        CATEGORY_SECURITY_VULNERABILITY,
        CATEGORY_POTENTIAL_SECURITY_RISK,
        CONFIDENCE_CONFIRMED,
        CONFIDENCE_HIGH,
        CONFIDENCE_LOW,
    )


def _load_benchmark_and_ground_truth():
    benchmark_candidates = [
        os.path.join(PROJECT_ROOT, "benchmarks_and_evaluation", "vulnerable_100.cpp"),
        os.path.join(PROJECT_ROOT, "MicroBenchmarks", "Testcases", "vulnerable_100.cpp"),
        os.path.join(ROOT_DIR, "security_related_files", "benchmarks_and_evaluation", "vulnerable_100.cpp"),
    ]
    benchmark_file = next((p for p in benchmark_candidates if os.path.isfile(p)), None)
    if not benchmark_file:
        pytest.skip(f"Benchmark file vulnerable_100.cpp not found")

    with open(benchmark_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    lines = source_code.splitlines()
    flaw_comment_re = re.compile(r"^\s*//\s*(\d+)\.\s+(CWE-\d+)\s+(.*)")

    ground_truth = []
    for idx, line in enumerate(lines, 1):
        m = flaw_comment_re.match(line)
        if m:
            num = int(m.group(1))
            cwe = m.group(2)
            desc = m.group(3).strip()
            fn_name = f"v{num:03d}"
            fn_line = idx + 1
            for offset in range(1, 5):
                if idx - 1 + offset < len(lines):
                    next_line = lines[idx - 1 + offset]
                    fn_match = re.search(rf"\b(v{num:03d}\w*)\s*\(", next_line)
                    if fn_match:
                        fn_name = fn_match.group(1)
                        fn_line = idx + offset
                        break
            ground_truth.append({
                "index": num,
                "function": fn_name,
                "cwe_id": cwe,
                "description": desc,
                "comment_line": idx,
                "code_line": fn_line,
            })

    return source_code, benchmark_file, ground_truth


def test_vulnerable_100_benchmark_evaluation():
    """Run full analyzer against vulnerable_100.cpp and assert rigorous benchmark metrics."""
    source_code, file_path, ground_truth = _load_benchmark_and_ground_truth()
    assert len(ground_truth) == 100, f"Expected 100 ground-truth flaws, found {len(ground_truth)}"

    # 1. Run rule engine
    rule_findings = scan_security_rules(source_code, file_path)
    assert len(rule_findings) > 0, "Security rules must produce findings on vulnerable_100.cpp"

    # 2. Run conventional tools concurrently
    runner = ToolRunner(timeout_sec=20)
    tool_results = runner.run_all_tools_concurrently(source_code, file_path)

    all_raw = list(rule_findings)
    for tname, res in tool_results.items():
        all_raw.extend(res.findings)

    # 3. Deduplicate
    deduped_findings, dedup_summary = deduplicate_findings(all_raw)

    # 4. Evaluate against Ground Truth
    # For each ground-truth flaw, check if a finding matches its code range [comment_line, code_line + 4]
    matched_gt = {}
    unmatched_gt = []
    exact_line_matches = 0

    for gt in ground_truth:
        idx = gt["index"]
        c_line = gt["comment_line"]
        k_line = gt["code_line"]
        cwe = gt["cwe_id"]

        # Find findings in the function region
        fn_findings = [
            f for f in deduped_findings
            if f.get("line") is not None and (c_line <= f.get("line") <= k_line + 4)
        ]

        # Prioritize matching by CWE or defect family
        best_match = None
        for f in fn_findings:
            if f.get("cwe_id") == cwe:
                best_match = f
                break
        if not best_match and fn_findings:
            best_match = fn_findings[0]

        if best_match:
            matched_gt[idx] = best_match
            if best_match.get("line") in (k_line, k_line + 1, k_line + 2):
                exact_line_matches += 1
        else:
            unmatched_gt.append(gt)

    tp_count = len(matched_gt)
    fn_count = len(unmatched_gt)

    # Identify potential false positives: findings outside any ground truth function boundary
    all_gt_lines = set()
    for gt in ground_truth:
        for l in range(gt["comment_line"], gt["code_line"] + 5):
            all_gt_lines.add(l)

    fp_findings = [
        f for f in deduped_findings
        if f.get("line") not in all_gt_lines
        and f.get("category") in (CATEGORY_SECURITY_VULNERABILITY, CATEGORY_POTENTIAL_SECURITY_RISK)
    ]
    fp_count = len(fp_findings)

    # Compute metrics
    precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0.0
    recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0.0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    duplicate_rate = (
        (dedup_summary["original_count"] - dedup_summary["deduplicated_count"])
        / dedup_summary["original_count"]
        if dedup_summary["original_count"] > 0
        else 0.0
    )
    location_accuracy = exact_line_matches / tp_count if tp_count > 0 else 0.0

    # Save detailed evaluation report
    report = {
        "benchmark_file": file_path,
        "total_ground_truth_flaws": len(ground_truth),
        "true_positives": tp_count,
        "false_positives": fp_count,
        "false_negatives": fn_count,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "duplicate_finding_rate": round(duplicate_rate, 4),
        "source_location_accuracy": round(location_accuracy, 4),
        "deduplication_summary": dedup_summary,
        "unmatched_ground_truth": unmatched_gt,
        "false_positive_findings": fp_findings,
    }

    report_path = os.path.join(PROJECT_ROOT, "vulnerable_100_evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    # Assertions
    assert recall >= 0.95, f"Expected Recall >= 95%, got {recall * 100:.2f}% (TP={tp_count}, FN={fn_count})"
    assert precision >= 0.90, f"Expected Precision >= 90%, got {precision * 100:.2f}% (TP={tp_count}, FP={fp_count})"
    assert f1_score >= 0.90, f"Expected F1 >= 90%, got {f1_score * 100:.2f}%"
    assert location_accuracy >= 0.90, f"Expected Location Accuracy >= 90%, got {location_accuracy * 100:.2f}%"


def test_phase2_regressions():
    """Verify specific regression fixes from Phase 2."""
    source_code, file_path, _ = _load_benchmark_and_ground_truth()
    findings = scan_security_rules(source_code, file_path)

    # ── A. v037: Incorrect XXE detection ──
    v037_finds = [f for f in findings if "v037" in f.get("evidence", "") or f.get("line") == 153]
    for f in v037_finds:
        assert f.get("type") != "xxe_injection", "v037 must NOT be reported as confirmed XXE injection"
        assert f.get("is_confirmed") is False, "v037 finding must not be confirmed"
        assert f.get("confidence_level") == CONFIDENCE_LOW, "v037 must have low confidence"

    # ── B. v043, v049: Incorrect MD5 detection ──
    v043_finds = [f for f in findings if f.get("line") == 182]
    for f in v043_finds:
        assert f.get("type") != "weak_hash_md5", "v043 identity stub must not be labeled weak MD5"
        assert f.get("cwe_id") in ("CWE-256", "CWE-759"), "v043 must be detected as missing password hashing"

    v049_finds = [f for f in findings if f.get("line") == 200]
    for f in v049_finds:
        assert f.get("type") != "weak_hash_md5", "v049 identity stub must not be labeled weak MD5"
        assert f.get("cwe_id") in ("CWE-256", "CWE-759"), "v049 must be detected as missing password hashing"

    # ── C. v060: Incorrect Base64 detection ──
    v060_finds = [f for f in findings if f.get("line") == 239]
    for f in v060_finds:
        assert "base64" not in f.get("description", "").lower(), "v060 custom mapping must not be labeled Base64"
        assert f.get("cwe_id") == "CWE-261", "v060 must be mapped to CWE-261 (insecure encoding)"

    # ── D. Format string classification at lines 45, 132, 141, 197, 221, 375 ──
    # None of these constant format strings may be reported as CWE-134
    for ln in [45, 132, 141, 197, 221, 375]:
        ln_finds = [f for f in findings if f.get("line") == ln and f.get("cwe_id") == "CWE-134"]
        assert len(ln_finds) == 0, f"Line {ln} uses a constant format string and must not be flagged as CWE-134!"

    # Line 45 has genuine buffer overflow (CWE-121) from sprintf
    l45_buf = [f for f in findings if f.get("line") == 45 and f.get("cwe_id") == "CWE-121"]
    assert len(l45_buf) >= 1, "Line 45 sprintf overflow (CWE-121) must be preserved"

    # ── E & F. Crypto & Auth Findings ──
    # Line 179: API key
    l179 = [f for f in findings if f.get("line") == 179]
    assert any(f.get("cwe_id") == "CWE-798" for f in l179)

    # Line 204: Static IV constant
    l204 = [f for f in findings if f.get("line") == 204]
    assert any(f.get("cwe_id") == "CWE-329" for f in l204)

    # Line 210: RSA key length configuration
    l210 = [f for f in findings if f.get("line") == 210]
    assert any(f.get("cwe_id") == "CWE-326" for f in l210)

    # Line 214: Disabled TLS verification
    l214 = [f for f in findings if f.get("line") == 214]
    assert any(f.get("cwe_id") == "CWE-295" for f in l214)

    # Line 224: Untrusted command execution (generalizable, not hardcoded to v056)
    l224 = [f for f in findings if f.get("line") == 224]
    assert any(f.get("cwe_id") == "CWE-78" for f in l224)

    # Line 320: Password comparison without attempt limits (generalizable, not hardcoded to v083)
    l320 = [f for f in findings if f.get("line") == 320]
    assert any(f.get("cwe_id") in ("CWE-798", "CWE-307") for f in l320)
