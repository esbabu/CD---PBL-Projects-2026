from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "VulnHGNN_Project_Report.docx"


def find_section_index(doc, keywords):
    for idx, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        lower = text.lower()
        if any(keyword.lower() in lower for keyword in keywords):
            return idx
    return None


def add_paragraphs_after_section(doc, heading_keywords, paragraphs):
    index = find_section_index(doc, heading_keywords)
    if index is None:
        print(f"Warning: section heading not found for {heading_keywords[0]}; skipping insert.")
        return False

    body = doc.element.body
    anchor = body[index]
    for paragraph in reversed(paragraphs):
        body.insert(body.index(anchor) + 1, paragraph._p)
    return True


def add_table_after_section(doc, heading_keywords, rows):
    index = find_section_index(doc, heading_keywords)
    if index is None:
        print(f"Warning: section heading not found for {heading_keywords[0]}; skipping table insert.")
        return False

    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    header = table.rows[0].cells
    header_values = ["Method", "Precision", "Recall", "F1"]
    for cell, value in zip(header, header_values):
        cell.text = value
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in paragraph.runs:
                run.bold = True

    for row_values in rows:
        row_cells = table.add_row().cells
        for cell, value in zip(row_cells, row_values):
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    body = doc.element.body
    anchor = body[index]
    body.insert(body.index(anchor) + 1, table._tbl)
    return True


def ensure_section_at_end(doc, heading_text, bullets):
    if find_section_index(doc, [heading_text]) is not None:
        print(f"Section already exists: {heading_text}")
        return

    heading = doc.add_paragraph()
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = heading.add_run(heading_text)
    run.bold = True

    for bullet in bullets:
        paragraph = doc.add_paragraph(bullet)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.style = "List Bullet"


# Load existing report
report_doc = Document(REPORT_PATH)

# Fix 1: Methodology section
methodology_list = [
    "1. Input validation — Reject empty, malformed, or oversized source, and normalize file paths before any analysis begins.",
    "2. Local Clang compilation — Compile the submitted source with Clang to surface syntax issues and confirm constant division-by-zero warnings in a local temp file that is cleaned up in a finally block.",
    "3. Gemini review — Send the source as structured JSON data to the configured provider with explicit untrusted-data instructions, bounded findings, and validator checks on severity and line numbers.",
    "4. Finding assembly — Keep Gemini findings separate from Clang diagnostics, and only attach a short-lived HMAC token to Gemini findings that are opted into AI repair suggestions.",
    "5. Opt-in repair — When the user triggers a fix suggestion, the server verifies the HMAC token, operates on a copy of the source, validates the repaired copy with Clang, and shows a side-by-side diff with Apply and Discard controls.",
]
methodology_paragraphs = []
for item in methodology_list:
    paragraph = report_doc.add_paragraph(item)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.style = "List Number"
    methodology_paragraphs.append(paragraph)

hmac_paragraph = report_doc.add_paragraph(
    "For the fix-request path, each Gemini finding is signed with a short-lived HMAC token (10-minute TTL) that is bound to the exact source text, language, and finding content. The server verifies that token before accepting any repair request, preventing replay and forgery attacks. The signing key is VULNHGNN_FINDING_SIGNING_KEY, kept server-side and at least 32 random bytes long."
)
hmac_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

if add_paragraphs_after_section(report_doc, ["methodology"], methodology_paragraphs + [hmac_paragraph]):
    print("Section 3 updated: Methodology")
else:
    print("Warning: Methodology section missing; skipped.")

# Fix 2: Results section
results_table_rows = [
    ["GNN (checkpoint epoch 78)", "—", "—", "0.467"],
    ["Gemini (comment-stripped source)", "—", "—", "0.909"],
    ["Clang-Tidy (keyword-mapped)", "High", "Lower", "0.435"],
]
if add_table_after_section(report_doc, ["results"], results_table_rows):
    print("Section 4 updated: Results table")
else:
    print("Warning: Results section missing; skipped table insert.")

results_note = [
    "29 repository tests passed, including mocked prompt-injection inputs and signed-token checks.",
    "These results show that Gemini provided a materially stronger diagnostic result on the repository fixtures than the GNN, while Clang-Tidy remained high precision but lower recall for the supported vulnerability classes.",
    "Gemini replaced the GNN as the primary web detector because the diagnostic evidence was stronger, the web path is broader than the GNN's four supported CWEs, and the legacy GNN remains available only for CLI and repair workflows."
]
results_paragraphs = []
for text in results_note:
    paragraph = report_doc.add_paragraph(text)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    results_paragraphs.append(paragraph)

if add_paragraphs_after_section(report_doc, ["results"], results_paragraphs):
    print("Section 4 updated: Results notes")
else:
    print("Warning: Results section missing; skipped notes insert.")

# Fix 3: Future Work
future_work = [
    "- Expand evaluation to 50–100 labeled fixtures from the Juliet Test Suite (NIST SARD) for CWE-190, 191, 369, and 476 to get a credible held-out benchmark.",
    "- Add a per-CWE breakdown table with Precision, Recall, and F1 for each vulnerability category.",
    "- Add HTTP Basic Auth and per-IP rate limiting (10 req/min) to the Flask endpoints.",
    "- Add isolated compiler execution with subprocess timeouts and resource limits to prevent side effects from submitted source.",
    "- Add a source privacy consent notice informing users when code is sent to the Gemini API.",
    "- Test prompt-injection cases systematically (hostile comments, embedded instructions) in the fix request path.",
]
ensure_section_at_end(report_doc, "5. Future Work", future_work)
print("Section 5 updated: Future Work")

# Fix 4: References
references = [
    "[1] Y. Zhou et al., \"Devign: Effective Vulnerability Identification by Learning Comprehensive Program Semantics via Graph Neural Networks,\" NeurIPS 2019, arXiv:1909.03496.",
    "[2] D. Guo et al., \"GraphCodeBERT: Pre-training Code Representations with Data Flow,\" arXiv:2009.08366, 2020.",
    "[3] Jaya9899, \"VulnHGNN,\" GitHub, https://github.com/Jaya9899/VulnHGNN.",
    "[4] Google, \"Gemini API: Structured outputs,\" https://ai.google.dev/gemini-api/docs/structured-output.",
    "[5] LLVM Project, \"Clang Diagnostics Reference,\" https://clang.llvm.org/docs/DiagnosticsReference.html.",
    "[6] MITRE, \"CWE-190, CWE-191, CWE-369, CWE-476,\" https://cwe.mitre.org/.",
]
ensure_section_at_end(report_doc, "6. References", references)
print("Section 6 updated: References")

report_doc.save(REPORT_PATH)
print(f"Saved updated report: {REPORT_PATH}")
