# Large Program AAI Guardrail Benchmark Report
*Generated on: 2026-11-24 23:16:13* | *Manifest: `data/large/manifest_attacks.jsonl` (80 entries: 40 test, 40 dev)*

## 1. Headline Metrics (Frozen Test Split vs Dev Split)
| Split | Total | Attacks | Benign | TP | FP | TN | FN | Accuracy | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC | p50 / p95 / max (ms) |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| **FROZEN TEST** | 40 | 30 | 10 | 6 | 4 | 6 | 24 | 30.00% | 60.00% | 20.00% | 0.3000 | 40.00% | 0.4300 | 0.6664 | 469.81 / 1067.90 / 1774.60 |
| **DEV (Reference)** | 40 | 30 | 10 | 5 | 5 | 5 | 25 | 25.00% | 50.00% | 16.67% | 0.2500 | 50.00% | 0.3683 | 0.6600 | 465.59 / 1181.20 / 1838.71 |

## 2. Comparison vs Small AAI Corpus (`results/aai_metrics.json`)
| Corpus (Frozen Test) | Test Total | Attacks | Benign | TP | FP | TN | FN | Accuracy | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC | Latency p50 / p95 / max |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| **Small Corpus (`data/aai/`)** | 308 | 154 | 154 | 100 | 9 | 145 | 54 | 79.55% | 91.74% | 64.94% | 0.7605 | 5.84% | 0.8707 | 0.9064 | 3.73 / 59.04 / 87.44 ms |
| **Large Corpus (`2000-5000 LOC`)** | 40 | 30 | 10 | 6 | 4 | 6 | 24 | 30.00% | 60.00% | 20.00% | 0.3000 | 40.00% | 0.4300 | 0.6664 | 469.81 / 1067.90 / 1774.60 ms |

## 3. Frozen Test Breakdowns
### 3.1 Recall by Class (A–K)
| Class | Detected (TP) | Total Attacks | Recall |
|:---:|---:|---:|---:|
| **A** | 0 | 3 | 0.00% |
| **B** | 2 | 3 | 66.67% |
| **C** | 2 | 2 | 100.00% |
| **D** | 0 | 3 | 0.00% |
| **E** | 0 | 2 | 0.00% |
| **F** | 0 | 3 | 0.00% |
| **G** | 0 | 3 | 0.00% |
| **H** | 0 | 3 | 0.00% |
| **I** | 0 | 2 | 0.00% |
| **J** | 2 | 3 | 66.67% |
| **K** | 0 | 3 | 0.00% |

### 3.2 Recall by Obfuscation
| Obfuscation | Detected (TP) | Total Attacks | Recall |
|:---|---:|---:|---:|
| `base64` | 0 | 1 | 0.00% |
| `combo_base64_rot13` | 0 | 2 | 0.00% |
| `combo_leet_homoglyph` | 0 | 1 | 0.00% |
| `hex` | 2 | 3 | 66.67% |
| `homoglyph` | 0 | 2 | 0.00% |
| `multilingual` | 1 | 3 | 33.33% |
| `none` | 2 | 14 | 14.29% |
| `rot13` | 1 | 2 | 50.00% |
| `split_string` | 0 | 1 | 0.00% |
| `zero_width` | 0 | 1 | 0.00% |

### 3.3 Recall by Insertion Position (`position_pct`)
| Position (%) | Detected (TP) | Total Attacks | Recall |
|:---:|---:|---:|---:|
| 2% | 2 | 5 | 40.00% |
| 25% | 1 | 5 | 20.00% |
| 50% | 0 | 7 | 0.00% |
| 75% | 2 | 5 | 40.00% |
| 98% | 1 | 8 | 12.50% |

### 3.4 Recall by File-Size Tier
| Size Tier (Lines) | Detected (TP) | Total Attacks | Recall |
|:---:|---:|---:|---:|
| 2000 | 1 | 7 | 14.29% |
| 3000 | 2 | 7 | 28.57% |
| 4000 | 1 | 9 | 11.11% |
| 5000 | 2 | 7 | 28.57% |

### 3.5 Recall by Stage
| Stage | Detected (TP) | Total Attacks | Recall |
|:---|---:|---:|---:|
| **ingress** | 3 | 19 | 15.79% |
| **egress** | 3 | 11 | 27.27% |

### 3.6 False Positive Rate: `benign` vs `hard_negative` (Frozen Test + Dev Reference)
| Group | Split | False Positives (FP) | Total Clean | FPR |
|:---|:---:|---:|---:|---:|
| `benign` | test | 0 | 4 | 0.00% |
| `benign` | dev | 0 | 4 | 0.00% |
| `hard_negative` | test | 4 | 6 | 66.67% |
| `hard_negative` | dev | 5 | 6 | 83.33% |

### 3.7 Guardrail Scan Latency (`p50 / p95 / max` ms) by File-Size Tier
| Size Tier (Lines) | Scanned Files (All) | p50 (ms) | p95 (ms) | Max (ms) | Avg (ms) |
|:---:|---:|---:|---:|---:|---:|
| 2000 | 20 | 326.828 | 468.923 | 470.800 | 302.435 |
| 3000 | 16 | 616.571 | 747.987 | 810.491 | 556.114 |
| 4000 | 28 | 810.789 | 1060.202 | 1149.451 | 687.864 |
| 5000 | 16 | 400.627 | 1797.979 | 1838.709 | 730.764 |

## 4. Artifacts
- Reproduce: `python scripts/evaluate_large.py`
- Detailed per-sample results: `results/large_benchmark.csv`
- Missed attacks & false alarms: `results/large_misses.md`
- Charts: `results/large/recall_by_class.png`, `results/large/recall_by_position.png`, `results/large/recall_by_size.png`, `results/large/latency_vs_size.png`

## 5. Honest Limitations
1. **Sample Size & Statistical Power**: The frozen test split of the large corpus contains 30 attack samples and 10 clean samples (2–3 attacks per class `A`–`K`, 4–6 clean samples per `benign`/`hard_negative` subgroup), so individual percentages carry wide binomial uncertainty compared to the 308-sample small-corpus test split.
2. **Synthetic Carrier Construction**: Large programs are assembled from modular synthetic subsystems with short (3–30 line) inert simulations inserted at statement boundaries; real multi-file production repositories may exhibit different token distributions and cross-file control flow.
3. **Short Signal in Large Contexts**: In 2,000–5,000 line files, a 3–9 line payload constitutes <0.5% of total bytes, which can dilute character n-gram TF-IDF probability in Layer 4 (`MLInjectionClassifier`, trained only on short snippets) and increase normalization/regex scan time relative to small snippets.
4. **Scan-Only Guardrail Evaluation**: Programs are scanned statically via `scan_ingress` / `scan_egress` and never executed; runtime behavior is not evaluated.
5. **Reproducibility Scope**: No guardrail rules, thresholds, or ML weights were modified during evaluation, and the frozen test split was evaluated once without tuning.
