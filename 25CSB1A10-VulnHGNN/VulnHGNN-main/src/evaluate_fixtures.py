"""Run a reproducible diagnostic evaluation on the repository's C fixtures."""

import argparse
import json
import logging
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import CLASS_THRESHOLDS, DEFAULT_MODEL, DEFAULT_SUPPORT, load_model, predict_file


logger = logging.getLogger("evaluate_fixtures")
EXPECTED_CWES = {
    "test_01_clean.c": [],
    "test_02_cwe190.c": ["CWE-190"],
    "test_03_cwe191.c": ["CWE-191"],
    "test_04_cwe369.c": ["CWE-369"],
    "test_05_cwe476.c": ["CWE-476"],
    "test_06_dual_190_191.c": ["CWE-190", "CWE-191"],
    "test_07_dual_369_476.c": ["CWE-369", "CWE-476"],
    "test_08_triple_190_191_369.c": ["CWE-190", "CWE-191", "CWE-369"],
    "test_09_triple_191_369_476.c": ["CWE-191", "CWE-369", "CWE-476"],
    "test_10_all_vulnerabilities.c": ["CWE-190", "CWE-191", "CWE-369", "CWE-476"],
}
CWE_NAMES = ("CWE-190", "CWE-191", "CWE-369", "CWE-476")


def _metrics(records):
    counts = {
        cwe: {"true_positive": 0, "false_positive": 0, "false_negative": 0}
        for cwe in CWE_NAMES
    }
    for record in records:
        expected = set(record["expected_cwes"])
        predicted = set(record["detected_cwes"])
        for cwe in CWE_NAMES:
            if cwe in expected and cwe in predicted:
                counts[cwe]["true_positive"] += 1
            elif cwe in predicted:
                counts[cwe]["false_positive"] += 1
            elif cwe in expected:
                counts[cwe]["false_negative"] += 1

    total_tp = sum(count["true_positive"] for count in counts.values())
    total_fp = sum(count["false_positive"] for count in counts.values())
    total_fn = sum(count["false_negative"] for count in counts.values())
    per_cwe = {}
    for cwe, count in counts.items():
        precision = count["true_positive"] / (count["true_positive"] + count["false_positive"]) if count["true_positive"] + count["false_positive"] else 0.0
        recall = count["true_positive"] / (count["true_positive"] + count["false_negative"]) if count["true_positive"] + count["false_negative"] else 0.0
        per_cwe[cwe] = {
            **count,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
        }

    micro_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn else 0.0
    return {
        "micro_precision": round(micro_precision, 4),
        "micro_recall": round(micro_recall, 4),
        "micro_f1": round(
            2 * micro_precision * micro_recall / (micro_precision + micro_recall),
            4,
        ) if micro_precision + micro_recall else 0.0,
        "per_cwe": per_cwe,
    }


def evaluate_fixtures(test_dir: Path, model_path: Path, support_dir: Path) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, checkpoint = load_model(str(model_path), device)
    records = []

    for filename, expected_cwes in EXPECTED_CWES.items():
        source_path = test_dir / filename
        if not source_path.is_file():
            raise FileNotFoundError(f"Expected diagnostic fixture is missing: {source_path}")

        result = predict_file(
            source_path=source_path,
            model=model,
            device=device,
            support_dir=str(support_dir),
            threshold=0.5,
            verbose=False,
        )
        if not result.get("success"):
            raise RuntimeError(
                f"Fixture evaluation failed for {filename}: {result.get('error', 'unknown error')}"
            )

        records.append({
            "file": filename,
            "expected_cwes": expected_cwes,
            "detected_cwes": sorted(
                prediction["class"]
                for prediction in result["probabilities"]
                if prediction["detected"]
                and prediction["class"] in CWE_NAMES
            ),
            "scores": {
                prediction["class"]: prediction["probability"]
                for prediction in result["probabilities"]
            },
            "elapsed_sec": round(result["elapsed"], 4),
        })

    return {
        "evaluation_type": "diagnostic fixtures; not an independent held-out benchmark",
        "warning": (
            "These fixtures may overlap model training or tuning data. Do not interpret "
            "these metrics as generalization performance."
        ),
        "model": str(model_path),
        "checkpoint_epoch": checkpoint.get("epoch"),
        "checkpoint_validation_f1": checkpoint.get("val_f1"),
        "device": str(device),
        "thresholds": CLASS_THRESHOLDS,
        "fixture_count": len(records),
        "metrics": _metrics(records),
        "fixtures": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", type=Path, default=Path("test_files"))
    parser.add_argument("--model", type=Path, default=Path(DEFAULT_MODEL))
    parser.add_argument("--support", type=Path, default=Path(DEFAULT_SUPPORT))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = evaluate_fixtures(args.test_dir, args.model, args.support)
    serialized = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
        print(f"Diagnostic results saved to {args.output}")
    else:
        print(serialized)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
