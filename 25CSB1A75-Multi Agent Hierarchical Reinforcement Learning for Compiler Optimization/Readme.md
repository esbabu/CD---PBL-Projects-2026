

Multi-Agent Hierarchical Reinforcement Learning for Compiler Optimization

- **Student** — Sumit Sah
- **Roll number** — 25CSB1A75
- **Branch** — Computer Science and Engineering (Artificial Intelligence and Data Science), NIT Warangal
- **Course** — Compiler Design, Project-Based Learning (PBL) 2026
- **Project guide** — Prof. Erukala Suresh Babu
- **Project repository** — [PBL-SC-IDE on GitHub](https://github.com/sumitsah03690-bit/PBL-SC-IDE-)
- **Google Drive link** - https://drive.google.com/drive/u/7/folders/1ajFmFD18mJlNTSng13xUsV7TX6A6b0vb
## About the project

Secure Compiler IDE is a customized editor that helps students understand compiler diagnostics, find security issues, and compare compiler optimizations. It analyzes individual files and whole projects, explains findings through optional local AI models, and proposes syntax repairs for review. For eligible C and C++ files, it measures object size using standard compiler settings and reinforcement-learning-selected LLVM passes. High-severity security findings block optimization measurements.

## Project files

- Final end-semester report [25CSB1A75-SUMIT SAH - END REPORT- UPDATED]
## How to run
From the project root, with Python 3 and Clang installed, run a single-file check and a short workspace scan:

```bash
printf '%s\n' 'int main(void) { return 0; }' | python3 -m secure_compiler_backend.server --stdin hello.c
python3 -m secure_compiler_backend.server --workspace secure_compiler_backend --max-files 3
```

In the customized VSCodium editor, open the Analysis panel and select **Analyze Current File** or **Analyze Project**
