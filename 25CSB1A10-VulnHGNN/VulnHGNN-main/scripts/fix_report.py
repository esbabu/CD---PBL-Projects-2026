from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "VulnHGNN_Project_Report.docx"


ABSTRACT_TEXT = (
    "This report documents the modified VulnHGNN C/C++ security-analysis prototype. "
    "The web application uses Gemini agent review plus local Clang checks for full analysis, "
    "with debounced local-only checks while typing. An opt-in repair path requires a short-lived "
    "HMAC token bound to the exact source, language, and finding before requesting a fix; proposals "
    "are compiler-checked and shown for explicit user approval before any edit is applied. The legacy "
    "GNN remains available for CLI and repair workflows. On ten repository fixtures, micro-F1 was 0.467 "
    "for the GNN, 0.909 for Gemini on comment-stripped source, and 0.435 for Clang-Tidy. All 29 repository tests passed."
)


def find_heading_index(doc, heading_text):
    for idx, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == heading_text:
            return idx
    return None


def replace_progress_snapshot(doc):
    for idx, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if text.startswith("Progress snapshot:"):
            paragraph.text = ABSTRACT_TEXT
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            print(f"Updated progress paragraph at paragraph index {idx}.")
            return True
    print("Warning: Progress snapshot paragraph not found.")
    return False


def move_methodology_intro_to_top(doc):
    section_index = find_heading_index(doc, "3. Methodology")
    if section_index is None:
        print("Warning: Section 3 heading not found.")
        return False

    intro_text = "The pipeline processes code in the following sequence:"
    intro_index = None
    for idx in range(section_index + 1, len(doc.paragraphs)):
        text = doc.paragraphs[idx].text.strip()
        if text.startswith("4. ") or text.startswith("5. ") or text.startswith("6. "):
            break
        if text == intro_text:
            intro_index = idx
            break

    if intro_index is None:
        # If the intro is absent in this section, insert it at the top of the section.
        insert_before_idx = None
        for idx in range(section_index + 1, len(doc.paragraphs)):
            text = doc.paragraphs[idx].text.strip()
            if text.startswith("1. "):
                insert_before_idx = idx
                break
        if insert_before_idx is None:
            insert_before_idx = section_index + 1
        doc.paragraphs[insert_before_idx].insert_paragraph_before(intro_text)
        print("Inserted methodology intro at section top.")
        return True

    # Move existing intro paragraph to just after the section heading.
    intro_paragraph = doc.paragraphs[intro_index]
    intro_paragraph.text = intro_text
    intro_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    insert_before_idx = None
    for idx in range(section_index + 1, len(doc.paragraphs)):
        text = doc.paragraphs[idx].text.strip()
        if text.startswith("1. "):
            insert_before_idx = idx
            break
    if insert_before_idx is None:
        insert_before_idx = section_index + 1
    doc.paragraphs[insert_before_idx].insert_paragraph_before(intro_text)
    # Remove the original copy from its old location.
    if intro_index != insert_before_idx:
        original = doc.paragraphs[intro_index + 1]
        parent = original._p.getparent()
        parent.remove(original._p)
    print("Moved methodology intro to the start of Section 3.")
    return True


def replace_results_pipe_text_with_table(doc):
    section_index = find_heading_index(doc, "4. Results")
    if section_index is None:
        print("Warning: Section 4 heading not found.")
        return False

    # Remove the four specific plain-text rows in this section.
    bad_rows = {
        "Method | Precision | Recall | F1",
        "GNN (checkpoint epoch 78) | — | — | 0.467",
        "Gemini (comment-stripped source) | — | — | 0.909",
        "Clang-Tidy (keyword-mapped) | High | Lower | 0.435",
    }
    for paragraph in list(doc.paragraphs):
        if paragraph.text.strip() in bad_rows:
            parent = paragraph._p.getparent()
            parent.remove(paragraph._p)

    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    header_values = ["Method", "Precision", "Recall", "F1"]
    for cell, value in zip(table.rows[0].cells, header_values):
        cell.text = value
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in paragraph.runs:
                run.bold = True

    row_values = [
        ["GNN (checkpoint epoch 78)", "—", "—", "0.467"],
        ["Gemini (comment-stripped source)", "—", "—", "0.909"],
        ["Clang-Tidy (keyword-mapped)", "High", "Lower", "0.435"],
    ]
    for values in row_values:
        row_cells = table.add_row().cells
        for cell, value in zip(row_cells, values):
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Insert the table immediately after the Results heading.
    body = doc._body
    heading_p = doc.paragraphs[section_index]._p
    body.insert(body.index(heading_p) + 1, table._tbl)
    print("Replaced pipe-separated results rows with a proper Word table.")
    return True


def main():
    doc = Document(REPORT_PATH)

    replace_progress_snapshot(doc)
    move_methodology_intro_to_top(doc)
    replace_results_pipe_text_with_table(doc)

    doc.save(REPORT_PATH)
    print(f"Saved updated report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
