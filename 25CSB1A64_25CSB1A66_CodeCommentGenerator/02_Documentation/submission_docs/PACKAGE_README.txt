CODE COMMENT GENERATOR — PROJECT SUBMISSION

Team roll numbers: 25CSB1A64 and 25CSB1A66

PACKAGE CONTENTS
  01_Source_Code/       Application, tests, datasets, benchmarks, and project setup files
  02_Documentation/     User guides, security analysis, reports, figures, presentation, and demo script
  03_Screen_Recording/  GUI screen recording
  04_Results/           Training, evaluation, security-engine, and performance reports

RUNNING THE APPLICATION
  Use Python 3.12. From 01_Source_Code, run:

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -e ".[all]"
    .\.venv\Scripts\python.exe run_gui.py

The Rule-Based engine works without a trained model. ML and Neurosymbolic comment
generation are Python-only and require training; see README.md for setup and training
guidance. Rust, Java, C, C++, C#, and COBOL comment generation uses the Rule-Based engine.

The included large loan-origination sample is synthetic test code with planted
vulnerabilities. Analyze it with the app; do not deploy it.

The screen recording and demo script are included for presentation. The current saved
ML model weights are not included; reports and evaluation artifacts are included.
