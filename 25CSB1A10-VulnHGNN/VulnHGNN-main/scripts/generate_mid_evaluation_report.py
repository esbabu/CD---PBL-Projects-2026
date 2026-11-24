from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "mid_evaluation_report"
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


def add_page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, end])


def add_heading(document, text, level=1):
    p = document.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


def add_caption(document, text):
    p = document.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if p.runs:
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
    set_repeat_table_header(table.rows[0])
    for i, text in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = str(text)
        set_cell_shading(cell, "1F4E78")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
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
section = doc.sections[0]
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.72)
section.left_margin = Inches(0.82)
section.right_margin = Inches(0.82)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = 1.15
for name in ("Heading 1", "Heading 2", "Heading 3"):
    style = doc.styles[name]
    style.font.name = "Times New Roman"
    style.font.color.rgb = RGBColor(31, 78, 120)

header = section.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.CENTER
header_run = header.add_run("VulnHGNN - AI Agent and Live Analysis")
header_run.bold = True
header_run.font.size = Pt(9)
header_run.font.color.rgb = RGBColor(31, 78, 120)

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run("National Institute of Technology Warangal  |  ")
add_page_number(footer)

# Cover
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
p = doc.add_paragraph("MID-EVALUATION PROJECT REPORT")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(20)

doc.add_paragraph("")
p = doc.add_paragraph(
    "VulnHGNN: Gemini-Assisted C/C++ Vulnerability Agent\n"
    "with Real-Time Clang Feedback"
)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(18)

doc.add_paragraph("")
add_image(doc, ROOT / "docs" / "vulnhgnn_web_ui.png", 6.4)

table = doc.add_table(rows=4, cols=2)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
identity = [
    ("Submitted by", "Chepuri Saidattu"),
    ("Roll Number", "25CSB1A10"),
    ("Email", "cs25csb1a10@student.nitw.ac.in"),
    ("GitHub Repository", "https://github.com/SaiDattu3607/VulnHGNN-CD-Project-"),
]
for i, (label, value) in enumerate(identity):
    table.cell(i, 0).text = label
    table.cell(i, 1).text = value
    table.cell(i, 0).paragraphs[0].runs[0].bold = True
doc.add_paragraph("")
p = doc.add_paragraph("Mid Evaluation")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
doc.add_page_break()

add_heading(doc, "DECLARATION", 1)
doc.add_paragraph(
    "I declare that this mid-evaluation report presents the Gemini-assisted vulnerability "
    "agent and real-time Clang feedback implemented in the VulnHGNN project up to the "
    "mid-evaluation stage. Security hardening, prompt-injection work, and repair/localization "
    "extensions not completed at this stage are intentionally outside this report."
)
doc.add_paragraph("Name: Chepuri Saidattu")
doc.add_paragraph("Roll Number: 25CSB1A10")
doc.add_paragraph("Signature: ______________________")
doc.add_page_break()

add_heading(doc, "ACKNOWLEDGEMENT", 1)
doc.add_paragraph(
    "I thank my project guide and the Department of Computer Science and Engineering, "
    "NIT Warangal, for guidance during the design and implementation of the AI-assisted "
    "vulnerability-analysis prototype. I also acknowledge the open-source communities "
    "behind Flask, LLVM/Clang, Python, Google Gemini, and related development tools."
)
doc.add_page_break()

add_heading(doc, "ABSTRACT", 1)
doc.add_paragraph(
    "VulnHGNN is a web-based C/C++ vulnerability-analysis prototype that combines a "
    "Gemini-assisted security agent with deterministic Clang compiler checks. The system "
    "provides two analysis modes: local live checks during editing and a complete analysis "
    "request triggered by the user."
)
doc.add_paragraph(
    "Live mode uses Clang without external API calls. It validates C/C++ syntax and reports "
    "supported compiler-confirmed findings. Full analysis sends the submitted source to a "
    "configured Gemini provider through an OpenAI-compatible interface, normalizes its "
    "structured findings, and combines them with local Clang diagnostics. The resulting "
    "findings include severity, CWE, source line, evidence, reason, and recommendation."
)
doc.add_paragraph(
    "Focused agent tests completed successfully: 6 tests passed across Gemini response "
    "normalization and agent/Clang web behavior. The tests confirm CWE normalization, "
    "local-only live checks, Gemini-plus-Clang analysis, and explicit failure when the "
    "agent is unavailable."
)
doc.add_paragraph(
    "Keywords: Gemini Agent, C/C++, Clang, Live Vulnerability Feedback, CWE Analysis, "
    "Flask Web Interface"
)
doc.add_page_break()

add_heading(doc, "TABLE OF CONTENTS", 1)
paragraph = doc.add_paragraph()
run = paragraph.add_run()
begin = OxmlElement("w:fldChar")
begin.set(qn("w:fldCharType"), "begin")
instruction = OxmlElement("w:instrText")
instruction.set(qn("xml:space"), "preserve")
instruction.text = 'TOC \\o "1-3" \\h \\z \\u'
separator = OxmlElement("w:fldChar")
separator.set(qn("w:fldCharType"), "separate")
placeholder = OxmlElement("w:t")
placeholder.text = "Table of contents - update field in Word."
end = OxmlElement("w:fldChar")
end.set(qn("w:fldCharType"), "end")
run._r.extend([begin, instruction, separator, placeholder, end])
doc.add_page_break()

add_heading(doc, "I. INTRODUCTION", 1)
add_heading(doc, "1.1 Project Background", 2)
doc.add_paragraph(
    "Traditional compiler diagnostics are deterministic but often difficult for users to "
    "interpret. Cloud AI models can provide contextual explanations and broader CWE "
    "coverage, but their findings should remain advisory. VulnHGNN therefore combines "
    "Gemini review with local Clang diagnostics instead of relying on a single mechanism."
)
add_heading(doc, "1.2 Problem Statement", 2)
doc.add_paragraph(
    "Developers need immediate feedback while writing C/C++ and a broader full-analysis "
    "review after entering source code. The project should separate local syntax/compiler "
    "checking from external agent review, provide understandable findings, identify source "
    "lines, and report provider or analysis failures clearly."
)
add_heading(doc, "1.3 Mid-Evaluation Objectives", 2)
add_bullets(doc, [
    "Create a browser interface for C/C++ source entry.",
    "Run debounced local Clang checks while the user types.",
    "Call a Gemini-compatible agent only for full analysis.",
    "Normalize agent output into structured CWE findings.",
    "Merge Gemini and Clang findings into one result.",
    "Display risk, severity, evidence, and recommendations.",
    "Handle unavailable agent configuration and provider failures explicitly.",
])
add_heading(doc, "1.4 Scope at Mid Evaluation", 2)
doc.add_paragraph(
    "The report covers source entry, the web interface, Gemini agent integration, Clang "
    "live checks, structured result normalization, API behavior, and testing. It does not "
    "cover prompt-injection hardening or any later security modules, because those items "
    "were not included in the mid-evaluation implementation."
)

add_heading(doc, "II. PROBLEM DOMAIN AND EXISTING APPROACHES", 1)
add_heading(doc, "2.1 Compiler-Based Analysis", 2)
doc.add_paragraph(
    "Clang validates syntax and emits diagnostics for selected compiler conditions. It is "
    "deterministic and can confirm that a construct is present, but it does not identify "
    "every possible weakness."
)
add_heading(doc, "2.2 Agent-Based Analysis", 2)
doc.add_paragraph(
    "A Gemini-compatible agent reads source code as a C/C++ security-review request and "
    "returns structured findings. It can cover a broad set of CWE categories and explain "
    "the risk and recommendation in natural language. Agent findings remain advisory."
)
add_heading(doc, "2.3 Hybrid Approach", 2)
doc.add_paragraph(
    "The VulnHGNN prototype uses Clang for local, confirmed compiler diagnostics and Gemini "
    "for broader contextual review. Live typing remains local. Full analysis combines both "
    "sources and does not silently substitute an offline detector when the agent is unavailable."
)

add_heading(doc, "III. PROPOSED AGENT FRAMEWORK", 1)
add_heading(doc, "3.1 System Architecture", 2)
add_table(doc, ["Stage", "Responsibility"], [
    ("Source entry", "Accept C or C++ source in the browser."),
    ("Live check", "Debounce typing and call the local Clang endpoint."),
    ("Clang validation", "Check syntax and supported compiler diagnostics."),
    ("Full analysis", "Send source once to the configured Gemini-compatible provider."),
    ("Response normalization", "Validate score, severity, CWE, line, evidence, and recommendation."),
    ("Result merging", "Combine Gemini findings with Clang-confirmed findings."),
    ("Web response", "Return a structured JSON response for the interface."),
])

add_heading(doc, "3.2 Runtime Flow", 2)
add_bullets(doc, [
    "The user enters C or C++ source in the browser.",
    "After the typing pause, /api/live-check performs local Clang validation.",
    "Live checks do not call Gemini.",
    "Pressing Analyze triggers /api/analyze.",
    "Clang compilation and supported diagnostics are generated locally.",
    "Source code up to 64 KB is sent to the configured Gemini-compatible provider.",
    "The provider response is normalized into a bounded finding structure.",
    "Gemini findings and Clang findings are shown together.",
])

add_heading(doc, "3.3 Gemini Agent Configuration", 2)
add_table(doc, ["Element", "Purpose"], [
    ("VULNHGNN_LLM_API_KEY", "Provider API key."),
    ("VULNHGNN_LLM_MODEL", "Selected Gemini-compatible model."),
    ("VULNHGNN_LLM_API_URL", "OpenAI-compatible provider endpoint."),
    ("64 KB limit", "Maximum source size sent for review."),
    ("25-second timeout", "Maximum provider request duration."),
    ("128 KB response limit", "Maximum provider response size."),
])

add_heading(doc, "3.4 Structured Response", 2)
doc.add_paragraph(
    "The normalized agent response contains an integer security score from 0 to 100, a "
    "concise summary, a risk level, and up to 15 findings. Each finding has a title, "
    "severity, optional CWE identifier, source line, evidence, reason, and recommendation."
)

add_heading(doc, "IV. IMPLEMENTATION", 1)
add_heading(doc, "4.1 Web Interface", 2)
add_image(doc, ROOT / "docs" / "vulnhgnn_web_ui.png", 6.5,
          "Figure 1: VulnHGNN initial web interface")
doc.add_paragraph(
    "The interface contains a source editor, language selector, live system status, "
    "sustainability display, audit metrics, and tabs for detection, map, and healing."
)

add_heading(doc, "4.2 Live Clang Check", 2)
add_image(doc, ROOT / "docs" / "vulnhgnn_live_check.png", 6.5,
          "Figure 2: Full analysis with Gemini findings and Clang confirmation")
doc.add_paragraph(
    "The live/full result screen combines a Gemini review area with a deterministic Clang "
    "diagnostic panel. In the sample, Clang confirms constant division by zero as CWE-369 "
    "and Gemini explains the arithmetic flaw and secure correction."
)

add_heading(doc, "4.3 Main Implementation Components", 2)
add_table(doc, ["Component", "File", "Role"], [
    ("Web interface", "src/templates/, src/static/", "Editor and result presentation."),
    ("Flask API", "src/app.py", "Live-check and full-analysis endpoints."),
    ("Agent integration", "src/llm_security_review.py", "Provider request and response normalization."),
    ("Clang utilities", "src/predict.py", "Compilation and compiler diagnostic functions."),
])

add_heading(doc, "4.4 API Design", 2)
add_table(doc, ["Endpoint", "Method", "Purpose"], [
    ("/", "GET", "Serve the web interface."),
    ("/api/live-check", "POST", "Run local Clang feedback after typing."),
    ("/api/analyze", "POST", "Run Gemini plus Clang full analysis."),
])

add_heading(doc, "V. GEMINI REVIEW PROCESS", 1)
add_heading(doc, "5.1 Agent Prompt", 2)
doc.add_paragraph(
    "The agent is instructed to audit C/C++ source for concrete CWE weaknesses and return "
    "valid JSON only. It requests a security score, summary, severity, CWE, source line, "
    "evidence, explanation, and secure-coding recommendation."
)
add_heading(doc, "5.2 Output Validation", 2)
add_bullets(doc, [
    "The security score must be an integer between 0 and 100.",
    "Severities are restricted to critical, high, medium, or low.",
    "CWE identifiers must match the CWE-NNN format.",
    "Source lines must be positive integers.",
    "Findings are limited to 15 entries.",
    "Text fields are trimmed and length bounded.",
])
add_heading(doc, "5.3 Failure Behavior", 2)
doc.add_paragraph(
    "If the agent is not configured or the provider response fails, the full-analysis endpoint "
    "returns an explicit unavailable result instead of presenting a false clean analysis."
)

add_heading(doc, "VI. CLANG LIVE-CHECK PROCESS", 1)
doc.add_paragraph(
    "The live-check feature writes source to a temporary C or C++ file and invokes the local "
    "Clang compiler. The endpoint reports syntax validity and supported diagnostics. Current "
    "confirmed checks include constant division-by-zero and selected compiler diagnostics."
)
add_table(doc, ["Result", "Meaning"], [
    ("Valid", "Clang compiled the source without reported syntax failure."),
    ("Invalid", "Clang reported syntax or compiler errors."),
    ("CWE-369", "Clang confirmed constant division by zero."),
])

add_heading(doc, "VII. TESTING", 1)
add_heading(doc, "7.1 Test Environment", 2)
doc.add_paragraph(
    "Focused tests were executed using the project's virtual-environment Python interpreter."
)
add_heading(doc, "7.2 Agent and Live-Check Test Cases", 2)
add_table(doc, ["Test", "Verified behavior"], [
    ("CWE preservation", "Supported CWE-190 identifier is retained."),
    ("Invalid CWE handling", "CWE-999 is not promoted as a known result."),
    ("Malformed CWE handling", "Non-string CWE values are discarded."),
    ("Live-check locality", "Live checks call Clang and do not call Gemini."),
    ("Gemini plus Clang", "Agent and Clang findings are merged."),
    ("Unavailable agent", "Analyze returns 503 instead of false clean output."),
])

doc.add_paragraph(
    "Result: 6 focused tests passed, 0 failed, in 6.80 seconds. The run produced one "
    "deprecation warning from TorchScript; this warning is unrelated to the agent tests."
)

add_heading(doc, "7.3 Test Coverage Summary", 2)
add_table(doc, ["Area", "Coverage"], [
    ("Gemini response normalization", "Score, summary, severity, CWE, and findings."),
    ("CWE validation", "Supported, unsupported, and malformed values."),
    ("Live analysis", "Local-only behavior and Clang findings."),
    ("Full agent analysis", "Agent plus Clang merge and model-free web behavior."),
    ("Provider failure", "Explicit unavailable-agent response."),
])

add_heading(doc, "VIII. RESULTS AND ANALYSIS", 1)
add_heading(doc, "8.1 Initial Interface", 2)
doc.add_paragraph(
    "The initial interface provides source entry, a C/C++ language selector, live status, "
    "audit metrics, and analysis tabs. It clearly distinguishes live local feedback from "
    "full provider-based review."
)
add_heading(doc, "8.2 Full Analysis Result", 2)
doc.add_paragraph(
    "In the sample result, Gemini reports a higher apparent risk score of 0 out of 100 "
    "and identifies the arithmetic division-by-zero issue. Clang independently confirms "
    "CWE-369 on source line 3. This demonstrates complementary agent and compiler evidence."
)
add_heading(doc, "8.3 Observations", 2)
add_bullets(doc, [
    "Clang provides fast, local confirmation for supported diagnostics.",
    "Gemini provides broader contextual explanation and recommendations.",
    "Combining both sources improves result readability.",
    "Advisory findings require manual interpretation.",
    "Provider availability is essential for the full-analysis route.",
])

add_heading(doc, "IX. ADVANTAGES AND APPLICATIONS", 1)
add_bullets(doc, [
    "Immediate local feedback during source editing.",
    "Broader CWE coverage through Gemini.",
    "Structured and line-oriented findings.",
    "Clear separation between live and full analysis.",
    "No silent fallback when full agent review is unavailable.",
    "Suitable for educational vulnerability-analysis demonstrations.",
])
doc.add_paragraph(
    "Possible applications include secure-code learning, IDE-integrated vulnerability review, "
    "coding interview assistance, and educational demonstrations of compiler-agent integration."
)

add_heading(doc, "X. CONCLUSION", 1)
doc.add_paragraph(
    "At the mid-evaluation stage, VulnHGNN implements a Gemini-assisted C/C++ vulnerability "
    "agent integrated with local Clang diagnostics. The browser interface supports debounced "
    "live checks and full analysis, and agent responses are normalized into understandable "
    "structured findings."
)
doc.add_paragraph(
    "Focused testing verified Gemini response normalization, local-only live checks, "
    "Gemini-plus-Clang merging, and explicit unavailable-provider handling. The implementation "
    "at this stage is limited to the agent and Clang parts and does not include later "
    "prompt-injection or security-hardening work."
)

add_heading(doc, "REFERENCES", 1)
refs = [
    "[1] Google AI for Developers, \"Gemini API and OpenAI-compatible API documentation,\" https://ai.google.dev.",
    "[2] The Clang Team, \"Clang: A C language family frontend for LLVM,\" https://clang.llvm.org.",
    "[3] LLVM Project, \"LLVM Language Reference Manual,\" https://llvm.org/docs/LangRef.html.",
    "[4] MITRE, \"Common Weakness Enumeration,\" https://cwe.mitre.org.",
    "[5] Flask, \"Flask Web Framework Documentation,\" https://flask.palletsprojects.com.",
    "[6] MITRE, \"CWE-369: Divide by Zero,\" https://cwe.mitre.org/data/definitions/369.html.",
]
for ref in refs:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)

add_heading(doc, "APPENDIX A: MID-EVALUATION FOLDER STRUCTURE", 1)
add_table(doc, ["Path", "Purpose"], [
    ("src/app.py", "Web API and UI route implementation."),
    ("src/llm_security_review.py", "Gemini-compatible agent integration."),
    ("src/predict.py", "Clang and compiler diagnostic utilities."),
    ("src/templates/", "Web HTML templates."),
    ("src/static/", "Browser JavaScript and interface assets."),
    ("tests/test_llm_security_review.py", "Agent response normalization tests."),
    ("tests/test_live_check.py", "Live-check and Gemini-plus-Clang tests."),
])

add_heading(doc, "APPENDIX B: PROJECT LINKS", 1)
doc.add_paragraph("GitHub repository: https://github.com/SaiDattu3607/VulnHGNN-CD-Project-")
doc.add_paragraph("Student email: cs25csb1a10@student.nitw.ac.in")

settings = doc.settings.element
update_fields = OxmlElement("w:updateFields")
update_fields.set(qn("w:val"), "true")
settings.append(update_fields)

word_path = OUT_DIR / "VulnHGNN_Mid_Evaluation_Agent_Report_Chepuri_Saidattu.docx"
doc.save(word_path)
print(word_path)
