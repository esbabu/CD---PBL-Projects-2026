NLP-Based Code Summarizer with Security Audits
Subject: Compiler Design / Theory of Automata & Compiler Design (CD - PBL 2026)
Department: Computer Science & Engineering, NIT Warangal
Team:
Sai Vara Prasad (Roll No: 25CSB1A43)
Sri Cheran (Roll No: 25CSB1A34)
What We're Submitting
Our submission has five parts.
Source code: 25CSB1A43_25CSB1A34_NLP_BASED_CODE_SUMMARIZER_WITH_SECURITY_AUDITS_CODE.zip. 
This is the complete working project. It includes the Tree-sitter AST parsers, the Semgrep-based vulnerability scanner, the SecurityGuardrailAgent that protects against prompt injection, and the CodeUnderstandingAgent, which uses Gemini Flash to summarize code. It also has the Streamlit web interface (web/app.py) and our test suites.
Final project report: 25CSB1A43_25CSB1A34_NLP_BASED_CODE_SUMMARIZER_WITH_SECURITY_AUDITS_DOCUMENT.docx. 
This is the full write-up of our work. It covers the abstract, architecture diagrams, how we ground summaries in the AST, our prompt injection defenses, CWE-based vulnerability classification, live fix verification, and energy usage measurements.

Demo recording: 
Via the Drive link below. This is a full walkthrough of the project in action. It shows scanning a directory, summarizing code, detecting vulnerabilities, the guardrail catching malicious code, and applying a patch in one click and re-checking it right in the browser.
Google Drive Link

Since some of these files are too large to send by email, we've uploaded them to Google Drive, as the submission guidelines allow. Anyone with an NITW email (@nitw.ac.in) can view them.

Link: https://drive.google.com/drive/folders/1ETObtqHGBCC544dDHVusQBjFBIc3SbfD?usp=sharing

The Drive folder contains the high-resolution demo video and screen recording (.mp4), plus the full codebase zip with the virtual environment dependencies.
About the Project

Our project is a tool that explains what code does and checks it for security problems at the same time. It works in four parts:

Protecting the AI itself. The SecurityGuardrailAgent sits in front of the language model. It normalizes tricky Unicode, uses canary tokens to catch data leaks, and defends against indirect prompt injection (OWASP LLM01), so malicious code can't trick the summarizer.
Two layers of static analysis. We combine Tree-sitter AST extraction with Semgrep rules and 12 custom AST-based security detectors. It works on Python, Java, JavaScript, and C.
Summaries that stay grounded. A multi-step Gemini Flash agent uses the code's actual structure (from the AST) to write executive summaries and function contracts, which keeps it from making things up.
Fixes you can verify. When a vulnerability is found, the tool suggests a patch that fits the surrounding code. You can apply it with one click and re-run the audit immediately in the browser to confirm the problem is gone.
