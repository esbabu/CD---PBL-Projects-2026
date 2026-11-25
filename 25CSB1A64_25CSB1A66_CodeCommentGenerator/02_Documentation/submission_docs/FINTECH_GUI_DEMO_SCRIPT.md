# Fintech Security GUI Demo Script

**Target length:** about 5 minutes  
**Sample:** `tests/large_corpus/cases/case_18_loan_origination.py` — synthetic, 2,110 lines, with 10 planted security findings. Analyze it in the app; do not execute it.

## 0:00 — Introduction

**On screen:** Open Code Comment Generator on the Generator page.

**Narration:** “I’m demonstrating a secure-code-review workflow with a synthetic loan-origination service. This 2,110-line sample has known planted issues, so we can see how the analyzer surfaces risks. The app analyzes source code; it doesn’t run the service.”

## 0:20 — Generate documentation

**On screen:** Open the sample file. Confirm Python and Rule-Based are selected. Click **Generate Comments**. Show the annotated output and highlight-added-lines control.

**Narration:** “The Generator adds documentation to the code and highlights the lines it inserted. It also runs the analysis pipeline and saves the annotated file and run logs. I can review the result here, copy it, or save it as a separate file.”

## 0:50 — Explore Insights

**On screen:** Open **Insights** and visit AST Features, AST Graph, Context Graph, Call Graph, IR Dump, Analysis Report, and Evaluation.

**Narration:** “Insights exposes the structure behind the result. AST Features lists functions, classes, parameters and complexity. The AST Graph visualizes syntax structure. Context Graph summarizes function context, calls and warnings, while Call Graph shows relationships between functions. IR Dump shows the intermediate representation used by the pipeline. Analysis Report lists pattern findings and source locations. Evaluation shows the saved comment-generation metrics.”

## 1:45 — Inspect security findings

**On screen:** Open **Security**, choose **Scan Editor Code**, and select a finding from the table.

**Narration:** “Security scanning is available independently of comment generation. On this sample the analyzer reports 10 findings: six confirmed and four potential. The charts summarize the safe and unsafe split, severity, issue types and scores by function.”

**On screen:** Select the NoSQL-injection finding in `account_lookup18001`; show the Evidence panel, then click **Open in editor**.

**Narration:** “This finding traces request JSON into a MongoDB account query. The Evidence panel shows the source-to-sink path, confidence, and suggested fix. Opening it in the editor jumps to the relevant line. Findings can also be filtered by severity or status and exported as JSON.”

**Optional:** If the agent is configured and completes successfully, click **Auto-fix**, show its verification steps, review the patch, then accept or discard it. Do not present an unverified patch as fixed.

## 2:50 — Model training

**On screen:** Open **ML Training**. Show the model card, current scores, preset options, saved-dataset checkbox, progress and cancel controls.

**Narration:** “The ML Training page shows whether a model is available, when it was saved, and its evaluation scores. It offers Quick check, Standard, Full and Custom presets, with progress reporting and cancellation during fine-tuning. The current model was trained with Quick check, which validates the pipeline; it is not a quality benchmark. ML and Neurosymbolic comment generation are Python-only.”

## 3:25 — Performance

**On screen:** Open **Performance**. Show Comparison, a detector-engine tab, then Pipeline. Click **Profile editor code** on the Pipeline tab.

**Narration:** “The Comparison and engine tabs show saved security-detection evaluation results: precision, recall, F1, confusion matrices, vulnerability-family recall and latency. These are security-detection metrics, separate from the comment model’s Evaluation tab. Pipeline shows saved timing and memory benchmarks by language and processing stage. Profile editor code runs a warm-up, timing pass and memory pass on the code in the Generator, then lists the cost of each block.”

## 4:20 — Logs and close

**On screen:** Open **Logs**. Select a GUI pipeline log and a training report. Finish on the annotated output or Security findings page.

**Narration:** “Logs brings pipeline logs and training reports into one viewer. Together, the pages support a review workflow: document code, inspect its structure, investigate security findings, measure the analysis, and review run history. This is a prototype using a synthetic sample; it is not a compliance certification.”
