# Large Realistic Program Corpus Generator

This package generates a benchmark corpus of 92 single-file programs ranging from 2,000 to 5,000 lines in four programming languages: **C++ (C++17)**, **C (C11)**, **Python (3.11+)**, and **Java (Java 17+)**.

## 1. Corpus Layout

```
test_cases/large/
├── benign/
│   ├── cpp/           # 10 clean C++17 programs (2000-5000 lines)
│   ├── c/             # 10 clean C11 programs (2000-5000 lines)
│   ├── python/        # 10 clean Python 3 programs (2000-5000 lines)
│   └── java/          # 10 clean Java programs (2000-5000 lines)
├── hard_negative/
│   ├── cpp/           # 5 benign C++ programs with suspicious patterns
│   ├── c/             # 5 benign C programs with suspicious patterns
│   ├── python/        # 5 benign Python programs with suspicious patterns
│   └── java/          # 5 benign Java programs with suspicious patterns
└── broken/
    ├── cpp/           # 8 broken C++ programs with 1-5 injected compile errors
    ├── c/             # 8 broken C programs with 1-5 injected compile errors
    ├── python/        # 8 broken Python programs with 1-5 injected compile errors
    └── java/          # 8 broken Java programs with 1-5 injected compile errors
```

## 2. Groups

| Group | Total Files | Files / Lang | Description | Validation |
|:---|:---:|:---:|:---|:---|
| **Benign** | 40 | 10 | Real-world modular architectures (logger, LRU cache, JSON parser, matrix math, graph algorithms, AVL tree, bank ledger, inventory). | Compiles with 0 errors & 0 warnings |
| **Hard Negative** | 20 | 5 | Benign code with patterns that trigger naive scanners (prompt security evaluation strings, safe `popen` constants, Base64, salted password hashing, `getenv`, WAF attack regexes, secret masking). | Compiles with 0 errors & 0 warnings |
| **Broken** | 32 | 8 | Clean large programs with 1 to 5 compile errors injected at varied depths (~2%, 40%, 75%, 98%). Error types: missing semicolon, missing brace, undeclared variable, type mismatch, wrong return type, bad indentation, missing symbol. | Guaranteed compilation failure |
| **Total** | **92** | **23** | | |

## 3. Size Tiers & Line Counting

Lines are counted using strict `wc -l` semantics (POSIX newline counts). Each file includes a trailing newline.
Tiers are spread evenly across the corpus:
- **2000 tier**: 1900 - 2100 lines (2000 +/- 5%)
- **3000 tier**: 2850 - 3150 lines (3000 +/- 5%)
- **4000 tier**: 3800 - 4200 lines (4000 +/- 5%)
- **5000 tier**: 4750 - 5250 lines (5000 +/- 5%)

All files fall strictly within the configurable `[1900, 5300]` line range.

## 4. Deterministic Regeneration

All code composition and error injection is seeded deterministically:

```bash
# Regenerate all 92 files and manifests (runs compiler validation on all targets):
python -m scripts.generate_large.generate_all

# Or run individual group generators:
python -m scripts.generate_large.generate_benign
python -m scripts.generate_large.generate_hard_negative
python -m scripts.generate_large.generate_broken
```

## 5. Manifest Schemas

Manifests are stored in `data/large/`:
- `manifest_benign.jsonl`: 60 records (40 benign + 20 hard negative)
- `manifest_broken.jsonl`: 32 records (with `errors` array recording injected error line numbers and types)

Fields:
```json
{
  "id": "large_benign_cpp_01",
  "path": "test_cases/large/benign/cpp/system_service_01.cpp",
  "language": "cpp",
  "group": "benign",
  "lines": 2000,
  "sha256": "7e7c7edc...",
  "seed": 1000,
  "modules": ["logging_system", "lru_cache", "json_parser", ...]
}
```

For broken programs:
```json
{
  "id": "large_broken_cpp_01",
  "path": "test_cases/large/broken/cpp/service_node_01.cpp",
  "language": "cpp",
  "group": "broken",
  "lines": 2001,
  "sha256": "86705d47...",
  "seed": 8000,
  "modules": [...],
  "errors": [
    {"line": 801, "type": "undeclared_variable"}
  ]
}
```

## 6. Verification with Pytest

```bash
# Fast verification (manifests, file existence, SHA-256 hashes, line counts in ~0.2s):
python -m pytest tests/test_large_corpus.py -m "not slow"

# Full verification including real toolchain compilation checks:
python -m pytest tests/test_large_corpus.py
```
