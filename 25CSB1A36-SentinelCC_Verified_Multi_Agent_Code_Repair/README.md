# SentinelCC: A Verified Multi-Agent Framework for Automated Error Repair and Security Hardening of Multi-Language Codebases
Green Self Healing Compiler

- Student: Gagan Sai Sathvik Tottanapudi
- Roll Number: 25CSB1A36
- Branch: CSE (AI & DS), NIT Warangal
- Course: Compiler Design, Project-Based Learning (PBL) 2026
- Project repository: https://github.com/TgaganSS/25CSB1A36_SentinelCC-Verified-Multi-Agent-Code-Repair

## About the project

A self-healing front-end layered on top of g++. It compiles code, explains errors in plain English, classifies them (rules + a small ML model), runs a CWE-labelled security analysis, and repairs the code with a multi-agent pipeline. A fix is kept only if it is verified: the program still compiles and the reported problem is gone. Unsafe input is blocked by a safety gate before any compiler runs.

previously "Green Self Healing Compiler"

## Files uploaded

- Readme.md: this file, with the title, student details and a description of every upload.
- Project_Report.pdf: full project report (PDF).
- Project_Report.docx: full project report (editable Word version).
- Source_Code.zip: complete source code (folder green_self_healing_compiler with src, tests, demo, tools, docs and requirements.txt). Zipped because it has 190+ files.
- Output_Screenshots.zip: output screenshots of Demos A to F (error explanation, security hardening, optimisation, multi-file project, ZIP-in/ZIP-out, unsafe-input blocking), test-suite and benchmark evidence, and the figures used in the report. INDEX.txt inside describes each image.
- Screen recording (Google Drive, anyone with an NITW mail can access): https://drive.google.com/file/d/11-G4vp6xe5jKfWH-JEmUcL0jN5iqk9Yb/view?usp=sharing

## How to run

```
sudo apt install g++ binutils python3 python3-pip
cd green_self_healing_compiler
pip install -r requirements.txt
python3 src/main.py demo/01_null_deref.cpp
python3 src/main.py demo/02_vulnerable.cpp --harden
```

Full guided demo: see PRESENTATION_GUIDE.md and DEMO.md inside the source zip.

## Note

Deliberately malicious demo samples, nested sample archives and the demo notebook were removed from this copy because antivirus tools flag them. The full set is available on request.
