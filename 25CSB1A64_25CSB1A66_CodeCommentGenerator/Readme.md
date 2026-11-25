# Code Comment Generator

**Team roll numbers:** 25CSB1A64 and 25CSB1A66  
**Project:** Code Comment Generator

## Project overview

This project extends a code-comment generator with tools for understanding and reviewing source code. Its Rule-Based, ML-Based, and Neuro-Symbolic engines generate code documentation, while the security layer analyzes code for potential vulnerabilities.

This can support security and maintenance teams in banks and fintech companies that need to review long-lived legacy systems, especially when the original developers are no longer available. Generated documentation can help engineers understand unfamiliar code; vulnerability findings and verified patch suggestions can support security review.

## What was added

- A dedicated vulnerability-detection layer and an agentic patching workflow that checks proposed fixes.
- A retrieval-augmented generation (RAG) system that provides vulnerability and remediation guidance. OWASP benchmark cases are included in security evaluation; see the evaluation documentation for benchmark scope and results.
- Per-model performance reporting for the Rule-Based, ML-Based, and Neuro-Symbolic documentation engines.
- Multi-language analysis for Python, C, C++, Rust, COBOL, Java, and C#.
- Evaluation on large source files, alongside benchmark and dataset results.

## Submission folders

- **01_Source_Code/** — application, security analyzer, datasets, and tests. Start with [README.md](01_Source_Code/README.md) for setup and usage.
- **02_Documentation/** — project reports, technical guides, presentation, demo script, and figures.
- **04_Results/** — evaluation metrics, benchmark summaries, and model outputs.
- **Complete project ZIP** — [Download from Google Drive](https://drive.google.com/file/d/1gYwbsN5a5ePPh0r300wPxvkC2kWX44Ae/view).
- **Screen recording** — the only manually uploaded asset in the [submission release](https://github.com/smnawfal/25CSB1A64_25CSB1A66_CodeCommentGenerator/releases/tag/submission-25CSB1A64-25CSB1A66); GitHub’s source-code archives are generated automatically.

## Further details

- [Project documentation](02_Documentation/docs/Project_Documentation.pdf)
- [Security, agentic AI, and RAG](02_Documentation/docs/SECURE_AGENTIC_AI_AND_RAG.md)
- [Security datasets and evaluation](02_Documentation/docs/SECURITY_DATASET_AND_EVALUATION.md)
- [GUI guide](02_Documentation/docs/GUI.md)
- [Final project report](02_Documentation/submission_docs/Report_Final_CodeCommentGenerator.pdf)
