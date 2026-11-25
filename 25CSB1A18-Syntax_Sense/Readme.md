# SyntaxSense: Multi-Language Syntax Error Diagnostics & AST Classifier

SyntaxSense is a full-stack compiler design and syntax error diagnostic system combining deterministic Abstract Syntax Tree (AST) analysis, token-level parsing, source heuristics, and machine learning classification to diagnose, locate, and explain syntax errors with precise line and column numbers.

---

## 1. System Architecture

SyntaxSense features a modular, multi-language architecture with a centralized **Analyzer Registry**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SyntaxSense Frontend (Port 5173)                     │
│  React 19 • TypeScript • Vite • Monaco Editor • Real-time Diagnostics  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP POST /api/v1/analyze { language, code }
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Port 8000)                        │
│                 Validation • Routing • Health Endpoints                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Analyzer Registry (`registry.py`)                    │
│            Dispatches based on normalized language identifier          │
└───────────┬───────────────────────┬───────────────────────┬────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────────┐ ┌───────────────────┐ ┌────────────────────────┐
│      CppAnalyzer      │ │   PythonAnalyzer  │ │      JavaAnalyzer      │
│     (Implemented)     │ │   (Implemented)   │ │     (Implemented)      │
├───────────────────────┤ ├───────────────────┤ ├────────────────────────┤
│ • Lexer (`lexer.py`)  │ │ • Safe ast.parse  │ │ • Java Lexical Tokenizer
│ • Recursive Descent   │ │ • Tokenizer pass  │ │ • Delimiter Balancing  │
│   AST Parser          │ │ • Colons, indents │ │ • Semicolon & Grammar  │
│ • 30 AST Features     │ │ • Delimiters      │ │ • Zero execution       │
│ • Random Forest ML    │ │ • Zero execution  │ │ ➜ Line & Col Diags    │
│ ➜ Line & Col Diags    │ │ ➜ Line & Col Diags│ │                        │
└───────────────────────┘ └───────────────────┘ └────────────────────────┘
```

---

## 2. Multi-Language Support Matrix

| Language | Status | Engine / Method | Error Coverage |
|---|---|---|---|
| **C++** | **Active & Supported** | Recursive Descent AST + Source Heuristics + Random Forest ML (30 features) | Missing semicolons, unmatched braces/parentheses, invalid assignments, malformed conditionals/loops, missing operands, extra tokens. |
| **Python** | **Active & Supported** | Safe Python AST (`ast.parse`) + `tokenize` + Non-executing Heuristics | Missing colons (`def`, `if`, `for`, `while`, `class`), unexpected indents, unindent mismatches, unmatched delimiters `()[]{}` , unterminated strings, invalid assignments. |
| **Java** | **Active & Supported** | Lightweight Java Tokenizer + Deterministic Syntactic Analysis + Grammar Checks | Missing semicolons, unmatched braces/parentheses/brackets, malformed class/method declarations, invalid conditionals/loops, invalid assignments, unexpected tokens, unterminated strings/comments. |

---

## 3. Error Categories

### C++ Syntax Diagnostics
- `MISSING_SEMICOLON` — Omitted `;` at statement or declaration termination
- `UNMATCHED_BRACE` — Unbalanced or unclosed `{` or `}` braces
- `UNMATCHED_PARANTHESES` — Unbalanced `(` or `)` in expressions or conditionals
- `INVALID_ASSIGNMENT` — Non-lvalue constant/literal on left side of `=`
- `INVALID_CONDITIONAL` — Malformed conditional headers (`if x > 0`)
- `INVALID_LOOP` — Malformed `for` or `while` loop conditions
- `INVALID_EXPRESSION` — Incomplete binary operators or missing operands (`+ ;`)
- `EXTRA_TOKENS` — Illegal or unexpected lexical tokens (e.g. `@`)
- `INVALID_TYPE` — Duplicate or incompatible type specifiers
- `INVALID_ARRAY_DECL` — Malformed array bracket declarations
- `INVALID_FUNCTION_DECL` — Incomplete or malformed function signatures
- `MISPLACED_KEYWORD` — Reserved keywords outside valid syntax contexts
- `UNTERMINATED_STRING` — Unclosed string literals (`"hello`)

### Python Syntax Diagnostics
- `MISSING_COLON` — Missing `:` at the end of `def`, `class`, `if`, `elif`, `else`, `for`, `while`, `try`, `except`, `with` headers
- `UNEXPECTED_INDENT` — Unexpected indentation at statement level
- `UNINDENT_MISMATCH` — Indentation unindent not matching any outer block level
- `INDENTATION_ERROR` — Inconsistent indentation formatting
- `UNMATCHED_DELIMITER` — Unclosed or mismatched `(`, `[`, or `{`
- `UNTERMINATED_STRING` — Unclosed single, double, or triple-quoted string
- `INVALID_ASSIGNMENT` — Attempted assignment to literal or expression
- `INVALID_SYNTAX` — General Python syntax error

### Java Syntax Diagnostics
- `MISSING_SEMICOLON` — Omitted `;` at statement, field, or return termination
- `UNMATCHED_BRACE` — Unbalanced, unclosed, or extraneous `{` or `}` braces
- `UNMATCHED_PARANTHESES` — Unbalanced or unclosed `(` or `)` in expressions, method calls, or conditionals
- `UNMATCHED_BRACKET` — Unbalanced or unclosed `[` or `]` in array types or index access
- `INVALID_ASSIGNMENT` — Assignment to a constant literal or non-assignable expression on left side of `=`
- `INVALID_CONDITIONAL` — Missing parentheses in `if` statement conditions
- `INVALID_LOOP` — Missing parentheses in `while` or `for` loop headers
- `INVALID_CLASS_DECL` — Malformed class declaration or missing class identifier
- `EXTRA_TOKENS` — Unexpected or illegal characters (e.g. `#`)
- `UNTERMINATED_STRING` — Unterminated string literal, char literal, or block comment

---

## 4. Project Structure

```
CD_Project/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI routes & error handlers
│   │   └── services/
│   │       ├── base_analyzer.py        # BaseAnalyzer abstract interface
│   │       ├── registry.py             # Multi-language registry & dispatch
│   │       ├── cpp_analyzer.py         # C++ adapter wrapping cpp_analysis
│   │       ├── cpp_analysis.py         # C++ AST parser, heuristics & ML service
│   │       ├── python_analyzer.py      # Python AST & tokenizer analyzer
│   │       └── java_analyzer.py        # Java tokenizer & deterministic syntax analyzer
│   └── tests/
│       ├── test_api.py                 # Multi-language API endpoint tests
│       ├── test_registry.py            # Analyzer registry unit tests
│       ├── test_python_analyzer.py     # Python analyzer unit tests
│       ├── test_java_analyzer.py       # Java analyzer unit tests
│       └── test_cpp_analysis.py        # C++ analysis service unit tests
├── frontend/
│   ├── src/
│   │   ├── components/                 # Monaco editor, cards, diagnostics list
│   │   ├── constants/samples.ts        # Built-in 1-click test snippets
│   │   ├── services/api.ts             # Backend HTTP client
│   │   └── App.tsx                     # Main layout & analysis state management
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_diagnostic_quality.py      # Quality & zero-false-positive regressions
│   ├── test_colon_tokens.py            # Switch/label colon token tests
│   └── test_comment_stripping.py       # Comment preservation & stripping tests
├── cpp_parser.py                       # C++ Recursive descent AST parser
├── lexer.py                            # C++ lexical analyzer
├── ast_features.py                     # C++ AST feature extractor (30 features)
├── predict.py                          # CLI diagnostic and prediction runner
├── model.pkl                           # Trained Random Forest classifier (C++)
├── scaler.pkl                          # C++ feature scaler
└── README.md
```

---

## 5. Quickstart & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies (if not already installed)
pip install fastapi uvicorn pydantic scikit-learn pandas numpy joblib httpx

# 3. Start the FastAPI backend
uvicorn backend.app.main:app --reload --port 8000
```
- Health check: `http://localhost:8000/api/v1/health`
- Swagger docs: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 6. Automated Verification & Test Suites

SyntaxSense has automated unit, regression, and integration test suites:

### 1. Backend API, Registry, Python & Java Analyzers (51 tests)
```bash
./.venv/bin/python -m unittest discover backend/tests
```
Covers C++ delegation, Python AST diagnostics, Java deterministic tokenizer & delimiter syntax checks, empty/oversized inputs, and registry dispatch.

### 2. Root C++ & Multi-Language Integration Suite (24 tests)
```bash
./.venv/bin/python -m unittest discover tests
```
Verifies unknown tokens, missing operands, unary/binary operators, nested blocks, zero false positives on standard library streaming operators, and end-to-end integration for all C++, Python, and Java sample snippets.

### 3. Lexer Token & Comment Stripping Suite (7 tests)
```bash
./.venv/bin/python -m unittest tests/test_comment_stripping.py tests/test_colon_tokens.py
```

### 4. Frontend Production Build
```bash
cd frontend && npm run build
```
Verifies TypeScript compilation and bundle generation.

---

## 7. License & Credits

Educational Compiler Design Project. Built with React, Monaco Editor, FastAPI, Scikit-Learn, and Python AST.
---

## Project Submission Files

### 1. Source Code
Contains the complete Syntax Sense frontend, backend, analyzers, and supporting files.

### 2. Documentation
- Mid-Evaluation Report
- End-Evaluation Report
- AI Detection Report

### 3. Screen Recording
Contains the demonstration recording of the Syntax Sense application.
