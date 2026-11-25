"""
ML vulnerability detector and neuro-symbolic fusion
=====================================================
  families.py  CWE → vulnerability family (the ML label space) and family → rules
  dataset.py   labelled functions: NIST SARD Juliet 1.3 (Java, C, C++, C#) and
               OWASP BenchmarkPython (Python), with label-leaking names and
               comments removed
  model.py     load / explain a saved model (and the earlier Juliet-only trainer,
               kept as a library function)
  pipeline.py  the reproducible pipeline: dataset splits (70/15/15 by group),
               hyperparameter search on validation, one test score per language,
               and the side-by-side evaluation of the rule-based, ML and
               neuro-symbolic engines on the same test units
  detector.py  predicts a family and a probability per function of a file, with
               the tokens that drove the prediction
  fusion.py    the neuro-symbolic engine: combines rule findings, ML predictions
               and semantic checks from the knowledge base

    python -m src.vulnml.pipeline all      # train + compare the three engines
    python -m src.vulnml train             # = pipeline train
    python -m src.vulnml evaluate          # print saved test metrics
"""
