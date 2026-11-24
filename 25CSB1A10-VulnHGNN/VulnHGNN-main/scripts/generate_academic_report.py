from pathlib import Path
import json

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "report"
OUT_DIR.mkdir(exist_ok=True)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_margins(section):
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_toc(document):
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = 'TOC \\o "1-3" \\h \\z \\u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Right-click and select Update Field to refresh the table of contents."
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(text)
    run._r.append(fld_char3)


def add_heading(document, text, level=1):
    p = document.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


def add_caption(document, text):
    p = document.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True
    p.runs[0].font.size = Pt(9)
    return p


def add_image(document, path, width=6.5, caption=None):
    if path.exists():
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(width))
        if caption:
            add_caption(document, caption)


def add_table(document, headers, rows, widths=None):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, text in enumerate(headers):
        hdr.cells[i].text = str(text)
        set_cell_shading(hdr.cells[i], "1F4E78")
        for run in hdr.cells[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
        hdr.cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    document.add_paragraph()
    return table


def add_bullets(document, items):
    for item in items:
        document.add_paragraph(item, style="List Bullet")


doc = Document()
set_margins(doc.sections[0])

styles = doc.styles
styles["Normal"].font.name = "Times New Roman"
styles["Normal"].font.size = Pt(11)
styles["Normal"].paragraph_format.line_spacing = 1.15
styles["Title"].font.name = "Times New Roman"
for style_name in ("Heading 1", "Heading 2", "Heading 3"):
    style = styles[style_name]
    style.font.name = "Times New Roman"
    style.font.color.rgb = RGBColor(31, 78, 120)

section = doc.sections[0]
header = section.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = header.add_run("VulnHGNN - Vulnerability Detection and Self-Healing")
run.bold = True
run.font.size = Pt(9)
run.font.color.rgb = RGBColor(31, 78, 120)
footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run("National Institute of Technology Warangal  |  ")
add_page_number(footer)

# Cover page
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("NATIONAL INSTITUTE OF TECHNOLOGY WARANGAL")
r.bold = True
r.font.size = Pt(16)
p = doc.add_paragraph("Department of Computer Science and Engineering")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(13)
doc.add_paragraph("")
p = doc.add_paragraph("PROJECT REPORT")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(20)
doc.add_paragraph("")
p = doc.add_paragraph("VulnHGNN: Vulnerability Detection, Localization,\nand Automated Self-Healing for C/C++")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(18)
doc.add_paragraph("")
add_image(doc, ROOT / "docs" / "vulnhgnn_updated_architecture.png", 5.9)
doc.add_paragraph("")

table = doc.add_table(rows=4, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
data = [
    ("Submitted by", "Chepuri Saidattu"),
    ("Roll Number", "25CSB1A10"),
    ("Email", "cs25csb1a10@student.nitw.ac.in"),
    ("GitHub Repository", "https://github.com/SaiDattu3607/VulnHGNN-CD-Project-"),
]
for i, (a, b) in enumerate(data):
    table.cell(i, 0).text = a
    table.cell(i, 1).text = b
    table.cell(i, 0).paragraphs[0].runs[0].bold = True
table.style = "Table Grid"
doc.add_page_break()

add_heading(doc, "DECLARATION", 1)
doc.add_paragraph(
    "I hereby declare that the project entitled \"VulnHGNN: Vulnerability Detection, "
    "Localization, and Automated Self-Healing for C/C++\" is an original record of work "
    "completed by me using the project repository identified in this report. The work "
    "described here is based on the implementation, experiments, test cases, and generated "
    "results available in the repository. Where external concepts or tools are used, they are "
    "acknowledged in the references."
)
doc.add_paragraph("")
doc.add_paragraph("Name: Chepuri Saidattu")
doc.add_paragraph("Roll Number: 25CSB1A10")
doc.add_paragraph("Signature: ______________________")
doc.add_page_break()

add_heading(doc, "ACKNOWLEDGEMENT", 1)
doc.add_paragraph(
    "I express sincere gratitude to my course faculty and the Department of Computer Science "
    "and Engineering, NIT Warangal, for guidance and for providing the opportunity to complete "
    "this project. I also acknowledge the open-source communities behind Python, PyTorch, "
    "PyTorch Geometric, Flask, LLVM/Clang, NetworkX, and CodeCarbon. Their tools enabled the "
    "design and evaluation of a reproducible vulnerability-analysis system."
)
doc.add_page_break()

add_heading(doc, "ABSTRACT", 1)
doc.add_paragraph(
    "VulnHGNN is a hybrid C/C++ vulnerability-analysis project that combines graph neural "
    "network inference, LLVM IR representation, local compiler diagnostics, a Gemini-assisted "
    "web review, bounded repair workflows, and optional carbon tracking. The legacy CLI "
    "compiles C/C++ source to LLVM IR, converts functions into heterogeneous instruction graphs "
    "with sequential, definition-use, and control-flow edges, and applies a VulnGAT multi-label "
    "classifier for CWE-190, CWE-191, CWE-369, and CWE-476. Localization scores identify "
    "instructions relevant to a predicted weakness, after which available IR repair rules and "
    "GNN re-detection support an iteration-bounded self-healing loop."
)
doc.add_paragraph(
    "The web application uses a different primary full-analysis path: source is reviewed by "
    "Gemini while Clang supplies local syntax and supported compiler diagnostics. Live editor "
    "checks remain local and debounced. Results are advisory, and source repair proposals require "
    "explicit user review. Security controls include source-size and NUL validation, request "
    "limits, API-key and HMAC token gates, security headers, and structured JSON report export."
)
doc.add_paragraph(
    "A repository virtual-environment test run completed with 39 passing tests in 6.00 seconds. "
    "A diagnostic run over ten repository fixtures reported micro precision 0.5833, micro recall "
    "0.3889, and micro F1 0.4667. These fixtures may overlap training or tuning data and therefore "
    "are not an independent held-out benchmark. A separate 66-fixture benchmark report is also "
    "reported cautiously because its coverage and support are limited."
)
doc.add_paragraph(
    "Keywords: Vulnerability Detection, Graph Neural Networks, LLVM IR, Clang, Gemini, CWE, "
    "Code Localization, Self-Healing, Secure Software Engineering"
)
doc.add_page_break()

add_heading(doc, "TABLE OF CONTENTS", 1)
add_toc(doc)
doc.add_page_break()

add_heading(doc, "LIST OF FIGURES", 1)
add_table(doc, ["Number", "Title"], [
    ("Figure 1", "Updated VulnHGNN architecture"),
    ("Figure 2", "Legacy system pipeline"),
    ("Figure 3", "Self-healing feedback loop"),
    ("Figure 4", "Detection performance comparison"),
    ("Figure 5", "Clean VulnHGNN web interface"),
    ("Figure 6", "Local Clang live diagnostic"),
])
add_heading(doc, "LIST OF TABLES", 1)
add_table(doc, ["Number", "Title"], [
    ("Table 1", "Legacy and current web analysis comparison"),
    ("Table 2", "Supported vulnerability classes"),
    ("Table 3", "Repository test categories"),
    ("Table 4", "Diagnostic fixture results"),
    ("Table 5", "66-fixture benchmark summary"),
    ("Table 6", "Project dependencies"),
])
doc.add_page_break()

add_heading(doc, "I. INTRODUCTION", 1)
add_heading(doc, "1.1 Background and Motivation", 2)
doc.add_paragraph(
    "Security defects in C/C++ systems are difficult to identify because source behavior depends "
    "on control flow, memory operations, arithmetic boundaries, and external APIs. String-pattern "
    "scanners can miss structural relationships, while manual review does not scale. VulnHGNN "
    "integrates compiler-generated intermediate representation with machine learning and bounded "
    "automated repair. The project also exposes a browser interface for rapid developer feedback."
)
add_heading(doc, "1.2 Problem Statement", 2)
doc.add_paragraph(
    "Given C/C++ source code, the system should: (i) validate and compile it safely, (ii) detect "
    "supported vulnerability patterns, (iii) localize suspicious instructions or lines, "
    "(iv) propose repair actions that remain under explicit review, (v) revalidate outcomes, "
    "(vi) expose audit evidence, and (vii) avoid presenting failed or unavailable analysis as clean."
)
add_heading(doc, "1.3 Objectives", 2)
add_bullets(doc, [
    "Compile C/C++ source into LLVM IR and construct instruction graphs.",
    "Predict multiple supported CWE labels using VulnGAT.",
    "Combine Gemini advisory findings with local Clang diagnostics in the web workflow.",
    "Rank vulnerable instructions through attention and gradient-based localization.",
    "Apply compiler-checked, bounded, rule-based IR repair proposals.",
    "Maintain explicit stop reasons instead of allowing open-ended repair.",
    "Provide downloadable security-analysis JSON and sustainability data.",
])
add_heading(doc, "1.4 Scope and Limitations", 2)
doc.add_paragraph(
    "The legacy GNN supports five labels: non-vulnerable plus CWE-476, CWE-191, CWE-190, and "
    "CWE-369. The Gemini web review can normalize a broader MITRE CWE catalog, but its output is "
    "advisory and no provider response proves correctness. Clang live checks cover syntax and "
    "specific confirmed compiler diagnostics. Compilation confirms syntax and IR validity; it does "
    "not prove semantic correctness or security."
)

add_heading(doc, "II. BACKGROUND CONCEPTS", 1)
add_heading(doc, "2.1 LLVM Intermediate Representation", 2)
doc.add_paragraph(
    "LLVM IR is a typed intermediate language that exposes functions, basic blocks, instructions, "
    "operands, and memory operations. Clang lowers C/C++ source to IR, enabling graph construction "
    "and compiler validation independent of the original source syntax."
)
add_heading(doc, "2.2 Graph Neural Networks", 2)
doc.add_paragraph(
    "A heterogeneous function graph represents each instruction as a node. Edges capture sequential "
    "execution, definition-use relationships, and control flow. A graph attention network aggregates "
    "neighbor features and attention weights to produce a graph-level multi-label result."
)
add_heading(doc, "2.3 Vulnerability Classes", 2)
add_table(doc, ["CWE", "Meaning", "Legacy guidance"], [
    ("CWE-190", "Integer overflow or wraparound", "Check arithmetic bounds and input ranges."),
    ("CWE-191", "Integer underflow", "Check subtraction against the type minimum."),
    ("CWE-369", "Divide by zero", "Verify the divisor before division or modulo."),
    ("CWE-476", "NULL pointer dereference", "Check pointers before dereference."),
])
add_heading(doc, "2.4 Repair and Verification", 2)
doc.add_paragraph(
    "Repair is interpreted as a bounded transformation of LLVM IR. Candidate patches are limited "
    "to the available rule set, then checked with Clang and re-evaluated by the GNN. A successful "
    "fix should compile, introduce no new detected CWE, and leave no remaining detected CWE."
)

add_heading(doc, "III. RELATED WORK", 1)
doc.add_paragraph(
    "Recent vulnerability-analysis systems use code property graphs, abstract syntax trees, LLVM IR, "
    "intermediate representations, and graph neural networks. Devign, Reveal, SySeVR, and ReVeal-like "
    "learning-based approaches have demonstrated that structure-aware code representations outperform "
    "text-only baselines in many settings. However, graph quality, dataset leakage, and independent "
    "validation remain important concerns."
)
doc.add_paragraph(
    "Static analyzers such as Clang and Clang-Tidy provide compiler-validated diagnostics and are "
    "deterministic for supported patterns. They do not replace semantic vulnerability modeling for "
    "all CWE categories. Language-model reviewers can explain broader context and propose fixes, but "
    "their findings must be treated as advisory. VulnHGNN separates deterministic compilation checks "
    "from model or agent findings and explicitly records that distinction."
)
add_heading(doc, "3.1 Research Gap", 2)
add_bullets(doc, [
    "Avoiding file-level leakage between training, tuning, and evaluation splits.",
    "Providing explicit failure behavior instead of false clean predictions.",
    "Combining model localization with compiler-validated repair.",
    "Keeping live web feedback local so every keystroke does not call an external model.",
    "Distinguishing advisory AI findings from deterministic compiler diagnostics.",
])

add_heading(doc, "IV. SYSTEM REQUIREMENTS", 1)
add_heading(doc, "4.1 Hardware and Software", 2)
add_table(doc, ["Item", "Repository requirement"], [
    ("Operating system", "Windows; `.bat` launchers are used."),
    ("Python", "Python 3.8 or newer."),
    ("Core ML", "PyTorch, torch-geometric, NumPy, pandas, scikit-learn, SciPy."),
    ("Graph processing", "NetworkX."),
    ("Web", "Flask, python-dotenv."),
    ("Compiler", "Clang for syntax, IR, and live diagnostics."),
    ("Carbon tracking", "CodeCarbon."),
    ("Optional LLM", "Google AI Studio OpenAI-compatible Gemini endpoint."),
])
add_heading(doc, "4.2 Functional Requirements", 2)
add_bullets(doc, [
    "Accept C and C++ source through the web editor or CLI.",
    "Reject empty source, NUL bytes, and source above 1 MB.",
    "Expose live syntax and supported Clang findings without external AI calls.",
    "Send only full-analysis source up to 64 KB to Gemini.",
    "Return explicit unavailable-provider errors instead of GNN fallback.",
    "Export the latest web review as downloadable JSON.",
])

add_heading(doc, "V. PROPOSED FRAMEWORK", 1)
add_heading(doc, "5.1 Updated Architecture", 2)
add_image(doc, ROOT / "docs" / "vulnhgnn_updated_architecture.png", 6.6,
          "Figure 1: Updated VulnHGNN architecture")
doc.add_paragraph(
    "The architecture separates entry points, guardrails, web analysis, legacy GNN processing, "
    "output generation, and observability. Shared source validation protects both web and CLI paths."
)
add_heading(doc, "5.2 Web Analysis Flow", 2)
add_bullets(doc, [
    "The browser sends debounced live-check requests after a typing pause.",
    "Clang validates syntax and returns selected confirmed diagnostics.",
    "Pressing Analyze sends source up to 64 KB to the configured Gemini provider.",
    "The response is normalized into a security score, summary, findings, and scope notice.",
    "The UI downloads a local JSON report; Gemini does not execute code or apply repairs.",
])
add_heading(doc, "5.3 Legacy CLI Pipeline", 2)
add_image(doc, ROOT / "docs" / "diagrams" / "system_pipeline.png", 6.6,
          "Figure 2: Legacy VulnHGNN system pipeline")
doc.add_paragraph(
    "The CLI compiles source to LLVM IR, validates its structure and size, parses functions and "
    "instructions, builds node and edge features, creates PyG graphs, runs VulnGAT, localizes relevant "
    "nodes, applies available repair rules, and re-runs detection."
)

add_heading(doc, "5.4 Graph Representation", 2)
doc.add_paragraph(
    "Instruction nodes use 22 features in the model implementation. Three edge types are embedded "
    "and supplied to GATv2: sequential execution, definition-use, and control flow. The VulnGAT "
    "architecture uses three graph attention layers, BatchNorm, residual connections, mean and maximum "
    "pooling, and a final multi-label classifier."
)
add_heading(doc, "5.5 Localization and Repair", 2)
add_image(doc, ROOT / "docs" / "diagrams" / "feedback_loop.png", 6.6,
          "Figure 3: Detect-localize-repair-validate feedback loop")
doc.add_paragraph(
    "Localization combines attention-derived and gradient-derived node scores. Ranked instructions "
    "are passed to repair rules. The loop stops when no vulnerabilities remain, no repair is available, "
    "a new CWE is detected, validation fails, or the configurable iteration limit is reached."
)

add_heading(doc, "VI. IMPLEMENTATION", 1)
add_heading(doc, "6.1 Main Components", 2)
add_table(doc, ["Concern", "Implementation"], [
    ("Web UI/API", "src/app.py, src/templates/, src/static/"),
    ("Gemini review", "src/llm_security_review.py"),
    ("CLI", "src/pipeline.py"),
    ("Security controls", "src/security.py"),
    ("Repair loop", "src/feedback_loop.py"),
    ("Prediction", "src/predict.py, src/pyg_model.py"),
    ("Graph construction", "src/ir_parser.py, src/pyg_dataset.py"),
    ("Localization", "src/localization.py"),
    ("IR repair", "src/ir_healer.py"),
    ("Validation", "src/validation.py"),
    ("Carbon metrics", "src/carbon_tracker.py"),
])
add_heading(doc, "6.2 API Endpoints", 2)
add_table(doc, ["Endpoint", "Purpose"], [
    ("GET /", "Serve the web audit studio."),
    ("POST /api/live-check", "Run debounced local Clang checks."),
    ("POST /api/analyze", "Run Gemini-assisted full web analysis."),
    ("POST /api/suggest-fix", "Create an opt-in source fix from a signed finding."),
    ("POST /api/localize", "Localize vulnerable instructions."),
    ("POST /api/heal", "Run source/IR healing behavior."),
    ("POST /api/pipeline", "Run the complete legacy pipeline."),
])
add_heading(doc, "6.3 Input and Security Hardening", 2)
doc.add_paragraph(
    "Flask limits request bodies to 16 MB, and source validation rejects empty text, NUL bytes, "
    "and data larger than 1 MB. Source exceeding 64 KB is not sent to Gemini. The app supports "
    "optional API-key enforcement, HMAC-signing of findings, short-lived token verification, "
    "rate limiting, and standard security headers."
)

add_heading(doc, "VII. DATASET AND EXPERIMENTAL SETUP", 1)
add_heading(doc, "7.1 Repository Fixtures", 2)
doc.add_paragraph(
    "The repository contains ten diagnostic C fixtures and a benchmark structure with 66 fixtures "
    "covering 23 CWE categories. The ten fixtures include a clean source and combinations of "
    "CWE-190, CWE-191, CWE-369, and CWE-476. The benchmark report is not assumed to be independent "
    "held-out evidence."
)
add_heading(doc, "7.2 Training Split", 2)
doc.add_paragraph(
    "The repository now provides source-file-grouped graph splits to reduce the risk that functions "
    "from one file occur across training and evaluation partitions. The existing checkpoint was not "
    "reported as retrained, and generated fixture metrics explicitly carry a diagnostic-only warning."
)
add_heading(doc, "7.3 Evaluation Environment", 2)
add_table(doc, ["Setting", "Evidence"], [
    ("Test host", "Windows 11"),
    ("Python", "Python 3.12/3.14 environment observations"),
    ("Model device", "CPU"),
    ("Checkpoint", "results/pyg_gnn_v9/best_pyg_model.pt"),
    ("Checkpoint epoch", "78"),
    ("Diagnostic fixture count", "10"),
    ("Benchmark fixture count", "66"),
])

add_heading(doc, "VIII. EXPERIMENTAL RESULTS AND ANALYSIS", 1)
add_heading(doc, "8.1 Automated Test Outcome", 2)
doc.add_paragraph(
    "The complete test suite was executed with the project virtual-environment interpreter:"
)
add_table(doc, ["Test category", "Coverage"], [
    ("Source filtering", "Empty, NUL, size, valid C, and unsupported input."),
    ("Prediction", "Fail-closed behavior and unavailable model handling."),
    ("Gemini review", "Normalization and broad CWE catalog support."),
    ("Live check", "Valid code, division-by-zero, syntax errors, and language validation."),
    ("Grouped training", "Functions from the same source file remain grouped by split."),
    ("Comprehensive end-to-end", "Flask routes, headers, rate limiting, HMAC, API key, Clang, and benchmark integrity."),
])
doc.add_paragraph(
    "Result: 39 tests passed, 0 failed, in 6.00 seconds. One deprecation warning from TorchScript "
    "was reported."
)

add_heading(doc, "8.2 Diagnostic Fixture Analysis", 2)
add_table(doc, ["Metric", "Value"], [
    ("Fixture count", "10"),
    ("Micro precision", "0.5833"),
    ("Micro recall", "0.3889"),
    ("Micro F1", "0.4667"),
    ("Checkpoint validation F1", "0.0000"),
])
add_table(doc, ["CWE", "Precision", "Recall", "F1", "TP / FP / FN"], [
    ("CWE-190", "1.0000", "0.2500", "0.4000", "1 / 0 / 3"),
    ("CWE-191", "1.0000", "0.2000", "0.3333", "1 / 0 / 4"),
    ("CWE-369", "1.0000", "0.2000", "0.3333", "1 / 0 / 4"),
    ("CWE-476", "0.4444", "1.0000", "0.6154", "4 / 5 / 0"),
])
doc.add_paragraph(
    "Interpretation: The clean fixture was classified without false GNN labels, and individual "
    "CWE-190, CWE-191, and CWE-369 predictions had high precision but low recall. CWE-476 was "
    "recalled in every positive fixture but also produced five false positives. These results "
    "demonstrate threshold tuning and calibration needs. They must not be generalized."
)

add_heading(doc, "8.3 66-Fixture Benchmark Report", 2)
doc.add_table(rows=1, cols=2) if False else None
add_table(doc, ["Method", "Micro precision", "Micro recall", "Micro F1", "Macro F1"], [
    ("Clang", "1.0000", "0.2222", "0.3636", "0.1401"),
])
doc.add_paragraph(
    "The 66-fixture JSON report contains 23 covered CWE categories. Clang achieved perfect "
    "precision on the labels it detected in this report but low recall and limited macro F1. "
    "The report also contains model and Gemini/GNN comparison entries. Any live provider or "
    "offline-mock status must be checked before presentation, because not all entries represent "
    "executed external inference."
)
add_heading(doc, "8.4 Baseline Comparison", 2)
add_image(doc, ROOT / "docs" / "diagrams" / "baselines.png", 6.6,
          "Figure 4: Repository baseline comparison visualization")
doc.add_paragraph(
    "The baseline visualization is descriptive and should not replace measured, independently "
    "validated experiments. It contains representative comparisons among VulnHGNN and named tools."
)

add_heading(doc, "8.5 Live Web Evidence", 2)
add_image(doc, ROOT / "docs" / "vulnhgnn_web_ui.png", 6.6,
          "Figure 5: VulnHGNN web interface")
add_image(doc, ROOT / "docs" / "vulnhgnn_live_check.png", 6.6,
          "Figure 6: Local Clang live-check for constant division by zero")
doc.add_paragraph(
    "The screenshots demonstrate the browser interface and local live diagnostic flow. In the "
    "live-check screenshot, a source containing 10 / 0 was validated by Clang and reported as "
    "CWE-369 without a Gemini request."
)

add_heading(doc, "8.6 Carbon and Sustainability", 2)
carbon = ROOT / "results" / "emissions.csv"
if carbon.exists():
    doc.add_paragraph(
        "CodeCarbon data is retained in results/emissions.csv. The current execution row "
        "documents approximately 5.8458 seconds, 8.6082e-07 kWh, 1.4725e-07 kg of CO2, "
        "CPU utilization 10 percent, and an Intel 11th Gen i7-1195G7 CPU in the recorded run."
    )

add_heading(doc, "IX. TEST PLAN AND TEST CASES", 1)
add_table(doc, ["ID", "Test", "Expected result", "Verified"], [
    ("TC-01", "Empty source validation", "400/rejected", "Pass"),
    ("TC-02", "NUL-byte source", "Rejected with null-byte message", "Pass"),
    ("TC-03", "Valid C source", "Accepted", "Pass"),
    ("TC-04", "Security headers", "Required headers included", "Pass"),
    ("TC-05", "Rate limiting", "Fifth allowed, sixth blocked", "Pass"),
    ("TC-06", "API-key open mode", "Allowed without key", "Pass"),
    ("TC-07", "API-key enforced mode", "Wrong/missing key rejected", "Pass"),
    ("TC-08", "HMAC valid finding", "Token verifies", "Pass"),
    ("TC-09", "Tampered source", "Token rejected", "Pass"),
    ("TC-10", "Expired token", "Token rejected", "Pass"),
    ("TC-11", "Broad CWE normalization", "Catalog CWE IDs preserved", "Pass"),
    ("TC-12", "Web index", "HTTP 200 and VulnHGNN content", "Pass"),
    ("TC-13", "Live valid code", "Valid status", "Pass"),
    ("TC-14", "Constant division by zero", "CWE-369 returned", "Pass"),
    ("TC-15", "Live syntax error", "Invalid status", "Pass"),
])

add_heading(doc, "X. ADVANTAGES AND APPLICATIONS", 1)
add_bullets(doc, [
    "Immediate local syntax feedback through the browser.",
    "Clear separation of deterministic and advisory findings.",
    "Fail-closed behavior when provider or model inference is unavailable.",
    "Instruction-level localization instead of binary file-only classification.",
    "Compiler validation and explicit review for repair proposals.",
    "Source, API, and report safeguards suitable for a local audit prototype.",
])
doc.add_paragraph(
    "Potential applications include developer IDE extensions, secure-code coursework, CI pre-screening, "
    "vulnerability triage, and research on graph-based code analysis."
)

add_heading(doc, "XI. CONCLUSION AND FUTURE WORK", 1)
doc.add_paragraph(
    "VulnHGNN demonstrates a complete C/C++ vulnerability-analysis workflow that combines compiler "
    "representation, graph attention, bounded repair, local Clang feedback, Gemini-assisted review, "
    "security controls, and audit export. The repository test suite passed 39 tests, and the web and "
    "CLI components are integrated in separate, well-documented runtime paths."
)
doc.add_paragraph(
    "Future work should train and evaluate a complete held-out dataset using source-file-grouped "
    "splits, improve thresholds and per-CWE calibration, expand the repair catalog, add independent "
    "human and compiler validation for generated fixes, and run a consistent 66-fixture benchmark "
    "for GNN, Gemini, and Clang. Production deployment would additionally require authentication, "
    "rate limiting, isolated compiler execution, restricted filesystem access, and operational monitoring."
)

add_heading(doc, "REFERENCES", 1)
refs = [
    "[1] Y. Zhou, S. Liu, J. Siow, X. Du, and Y. Liu, \"Devign: Effective vulnerability identification by learning comprehensive program semantics via graph neural networks,\" NeurIPS, 2019.",
    "[2] M. Allamanis, M. Brockschmidt, and M. Khademi, \"Learning to represent programs with graphs,\" ICLR, 2018.",
    "[3] S. Chakraborty, R. Krishna, Y. Ding, and B. Ray, \"Deep learning based vulnerability detection: Are we there yet?\" IEEE TSE, 2021.",
    "[4] IBM, \"System call, memory safety and CWE-476,\" NIST National Vulnerability Database, 2024.",
    "[5] LLVM Project, \"LLVM Language Reference Manual,\" https://llvm.org/docs/LangRef.html.",
    "[6] The Clang Team, \"Clang: A C language family frontend for LLVM,\" https://clang.llvm.org.",
    "[7] MITRE, \"Common Weakness Enumeration,\" https://cwe.mitre.org.",
    "[8] MITRE, \"CWE-190: Integer Overflow or Wraparound,\" 2025.",
    "[9] MITRE, \"CWE-191: Integer Underflow,\" 2025.",
    "[10] MITRE, \"CWE-369: Divide by Zero,\" 2025.",
    "[11] MITRE, \"CWE-476: NULL Pointer Dereference,\" 2025.",
    "[12] P. Veličković et al., \"Graph Attention Networks,\" ICLR, 2018.",
    "[13] M. Fey and J. E. Lenssen, \"Fast graph representation learning with PyTorch Geometric,\" ICLR Workshop, 2019.",
    "[14] Flask, \"Flask Web Framework Documentation,\" https://flask.palletsprojects.com.",
    "[15] Google AI for Developers, \"Gemini API and OpenAI-compatible API documentation,\" https://ai.google.dev.",
    "[16] CodeCarbon, \"Track and reduce CO2 emissions from compute,\" https://codecarbon.io.",
    "[17] L. Zhang et al., \"A survey of deep learning for software engineering,\" ACM Computing Surveys, 2023.",
]
for ref in refs:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)

add_heading(doc, "APPENDIX A: REPOSITORY STRUCTURE", 1)
add_table(doc, ["Path", "Purpose"], [
    ("src/", "Application, model, parser, localization, repair, and validation implementation."),
    ("tests/", "Unit, integration, live-check, security, split, and end-to-end tests."),
    ("dataset/", "Dataset and benchmark support."),
    ("test_files/", "C fixture source files."),
    ("docs/", "Architecture diagrams and visualizations."),
    ("results/", "Checkpoints, reports, model outputs, and carbon metrics."),
    ("scripts/", "Utilities and report generation."),
])

add_heading(doc, "APPENDIX B: KEY CONFIGURATION", 1)
add_table(doc, ["Variable", "Purpose"], [
    ("VULNHGNN_LLM_API_KEY", "Gemini-compatible provider API key."),
    ("VULNHGNN_LLM_BASE_URL", "OpenAI-compatible provider endpoint."),
    ("VULNHGNN_LLM_MODEL", "Selected provider model."),
    ("VULNHGNN_API_KEY", "Optional web API-key protection."),
    ("VULNHGNN_FINDING_SIGNING_KEY", "HMAC key for signed findings."),
])

add_heading(doc, "APPENDIX C: RUN COMMANDS", 1)
for text in [
    "python -m venv venv",
    "venv\\Scripts\\activate",
    "pip install -r requirements.txt",
    "run.bat",
    "python src\\pipeline.py path\\to\\file.c --no-carbon --model results\\pyg_gnn_v9\\best_pyg_model.pt",
    "venv\\Scripts\\python.exe -m pytest tests -q",
]:
    p = doc.add_paragraph(text)
    p.style = "Intense Quote"

add_heading(doc, "APPENDIX D: PROJECT LINKS", 1)
doc.add_paragraph("GitHub repository: https://github.com/SaiDattu3607/VulnHGNN-CD-Project-")
doc.add_paragraph("Student email: cs25csb1a10@student.nitw.ac.in")

# Update fields on open
settings = doc.settings.element
update_fields = OxmlElement("w:updateFields")
update_fields.set(qn("w:val"), "true")
settings.append(update_fields)

word_path = OUT_DIR / "VulnHGNN_Academic_Project_Report_Chepuri_Saidattu.docx"
doc.save(word_path)
print(word_path)
