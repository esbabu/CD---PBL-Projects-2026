# ParC: Securing an AI Code Explanation Agent with Compiler Proven Facts

**Name:** Pranav Napolean
**Roll Number:** 25CSB1A69
**Course:** CS2201 Theory of Automata and Compiler Design, NIT Warangal

## Project Summary

ParC is a teaching compiler for a small C like language with built in parallel loops. Every phase of the compiler (scanner, parser, semantic analysis, IR and control flow graph, data flow optimizer, loop dependence test, code generator and register virtual machine) is written from scratch in C++20, and each phase explains what it found and why. When the compiler reports a bug it attaches a proof, a weakness class (CWE) and the exact condition under which the program fails.

On top of the compiler sits an AI agent that explains each finding in plain language and proposes fixes. Every explanation is checked against what the compiler proved, and every fix must pass a compiler gate before it is shown. A security layer detects prompt injection attacks hidden in code comments, scores their risk, blocks them and logs every event. It was tested with simulated attacks, an adaptive red team and a second AI playing the attacker.

## Files Uploaded

| File or Folder | Description |
|---|---|
| `Readme.md` | This file. Title, summary and the list of uploaded files. |
| `report/ParC_End_Report.pdf` | Final project report in the course template format (PDF). |
| `report/ParC_End_Report.docx` | The same report as an editable Word document. |
| `recording/ParC_End_Recording.mp4` | Screen recording demonstrating the compiler, the explorer UI, the AI agent and the security layer. |
| `screenshots/` | Output screenshots (34 images) of every compiler phase, the agent and the security tests. |
| `source/README.md` | Overview of the source code with build and run instructions. |
| `source/CMakeLists.txt` | CMake build file for the compiler and its test programs. |
| `source/compiler/` | The compiler in C++20. One folder per phase (scanner, parser, semantic, ir, optimizer, codegen, vm), the metrics module and the command line tool, each with its tests. |
| `source/explorer/` | The web explorer (Python, Flask) that shows every phase, plus the explain and fix agent and its security layer. |
| `source/examples/` | 20 example ParC programs and their expected outputs. |
| `source/evaluation/` | Evaluation scripts and results. Comparison with Clang, random testing, agent metrics and attack simulations. |

## How to Run

1. Build the compiler with CMake (Visual Studio 2022 or any C++20 compiler).
   `cmake -S source -B build` then `cmake --build build --config Release`
2. Run the tests with `ctest --test-dir build -C Release`.
3. Install Flask with `pip install -r source/explorer/requirements.txt`.
4. Start the explorer with `python source/explorer/app.py` and open http://127.0.0.1:5000.

Full instructions are in `source/README.md`.
