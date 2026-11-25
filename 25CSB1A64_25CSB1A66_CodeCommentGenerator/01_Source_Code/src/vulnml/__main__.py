"""
python -m src.vulnml train      — train, tune and test the ML detectors on the security dataset
python -m src.vulnml evaluate   — print the saved test metrics of every language

Both delegate to the reproducible pipeline in ``src.vulnml.pipeline`` (dataset splits 70/15/15,
hyperparameters chosen on validation, one final test score). ``python -m src.vulnml.pipeline evaluate``
additionally compares the rule-based, ML and neuro-symbolic engines on the same test units.

The earlier Juliet-only trainer (``model.train_language``) is kept as a library function, but the
CLI no longer calls it: it would overwrite the dataset-trained models in ``outputs/vulnml/``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ..config import configure_stdio
from .pipeline import DATASET, LANGS, MODEL_DIR, train


def main(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.vulnml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--dataset", default=DATASET)
    sub.add_parser("evaluate")
    args = ap.parse_args(argv)
    if args.cmd == "train":
        train(args.dataset)
        return 0
    for lang in LANGS:
        p = os.path.join(MODEL_DIR, f"{lang}_metrics.json")
        c = os.path.join(MODEL_DIR, f"{lang}_config.json")
        if not (os.path.isfile(p) and os.path.isfile(c)):
            print(f"{lang}: no trained model (python -m src.vulnml train)")
            continue
        m, cfg = json.load(open(p, encoding="utf-8")), json.load(open(c, encoding="utf-8"))
        if "test_binary" not in m:
            print(f"{lang}: metrics in an old format; retrain")
            continue
        b = m["test_binary"]
        print(f"{lang}: train/val/test {cfg['counts']}; chosen {cfg['chosen']}"
              f"{' (small-n)' if cfg.get('small_n') else ''}\n"
              f"   test P {b['precision']} R {b['recall']} F1 {b['f1']} FPR {b['fpr']} FNR {b['fnr']}; "
              f"family accuracy {m['test_family']['accuracy']}, macro-F1 {m['test_family']['macro_f1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
