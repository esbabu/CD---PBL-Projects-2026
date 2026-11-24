# Algo Agent — Groq edition

A small, API-backed code optimization tool for **C, C++, Python, and JavaScript**.

It sends the source code to a Groq model, asks for a conservative optimization, performs a syntax check where the required local tools are installed, and saves the returned source plus a JSON report.

## 1. Project structure

```text
algo_agent_groq/
├── algo_agent/
│   ├── __init__.py
│   ├── llm.py
│   ├── optimizer.py
│   └── validation.py
├── examples/
│   ├── sample.c
│   ├── sample.cpp
│   ├── sample.js
│   └── sample.py
├── tests/
│   ├── __init__.py
│   ├── test_llm.py
│   └── test_optimizer.py
├── .env.example
├── .gitignore
├── main.py
└── requirements.txt
```

## 2. Windows installation (PowerShell)

Open PowerShell in the folder containing `main.py`.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and enter your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Keep the key private. Do not paste it into chat or source files.

If PowerShell blocks environment activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Run the optimizer

```powershell
python main.py examples\sample.py
python main.py examples\sample.c
python main.py examples\sample.cpp
python main.py examples\sample.js
```

You can explicitly set the language and model:

```powershell
python main.py source.txt --language cpp --model openai/gpt-oss-120b
```

Optional arguments:

- `--language`: `c`, `cpp`, `python`, or `javascript`
- `--model`: overrides `GROQ_MODEL`
- `--output-dir`: output directory (default `output`)
- `--validation-timeout`: syntax-check timeout in seconds (default 15)

## 4. Output

The program creates:

```text
output/
├── optimized.py       # extension follows input language
└── optimization_report.json
```

The report contains the original source, generated source, theoretical complexity estimates, summary, changes, validation results, warnings, and elapsed pipeline time.

## 5. Language validation

- **Python:** uses Python's built-in parser/compiler; it does not execute the program.
- **JavaScript:** uses `node --check` if Node.js is installed.
- **C:** uses Clang/GCC syntax-only mode, or MSVC `/Zs` if available.
- **C++:** uses Clang++/G++ syntax-only mode, or MSVC `/Zs` if available.

Install a compiler/runtime to enable its validation:
- Node.js for JavaScript.
- LLVM/Clang or MinGW-w64 GCC for C/C++.
- For MSVC, launch the program from Visual Studio Developer PowerShell so `cl.exe` and its environment are available.

If a tool is missing, the program reports that validation was skipped. It does not claim that the source compiled successfully.

## 6. Tests

The tests use mocked Groq responses and do not need an API key or internet connection:

```powershell
python -m unittest discover -s tests -v
```

## 7. Important limitations

- The tool does not execute arbitrary submitted code.
- Syntax checks do not prove that optimized code preserves behavior.
- It does not measure real runtime or memory usage.
- Big-O values are model-generated theoretical estimates, not benchmark results.
- Review generated code and test it with your own trusted input/output test cases before using it.
