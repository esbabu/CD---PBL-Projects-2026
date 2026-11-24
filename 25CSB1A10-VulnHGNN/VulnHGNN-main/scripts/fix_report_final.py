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


def find_index_by_text(doc, text_fragment):
    for idx, paragraph in enumerate(doc.paragraphs):
        if text_fragment in paragraph.text:
            return idx
    return None


def remove_paragraphs_by_text(doc, texts):
    remove_indices = []
    for idx, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() in texts:
            remove_indices.append(idx)
    for idx in reversed(remove_indices):
        p = doc.paragraphs[idx]._p
        parent = p.getparent()
        parent.remove(p)


def remove_paragraph_range(doc, start_text, end_text):
    start_idx = find_index_by_text(doc, start_text)
    end_idx = find_index_by_text(doc, end_text)
    if start_idx is None or end_idx is None or start_idx >= end_idx:
        return False
    for idx in range(end_idx, start_idx - 1, -1):
        p = doc.paragraphs[idx]._p
        parent = p.getparent()
        parent.remove(p)
    return True


def insert_paragraph_at(doc, index, text):
    paragraph = doc.paragraphs[index].insert_paragraph_before(text)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return paragraph


def main():
    doc = Document(REPORT_PATH)

    # 1) Replace the progress snapshot block with the abstract.
    start_idx = find_index_by_text(doc, "Progress snapshot: 8/10")
    second_idx = find_index_by_text(doc, "The current system validates")
    if start_idx is not None and second_idx is not None:
        # remove both paragraphs and replace with a single abstract paragraph
        for idx in range(second_idx, start_idx - 1, -1):
            p = doc.paragraphs[idx]._p
            parent = p.getparent()
            parent.remove(p)
        doc.paragraphs[start_idx].insert_paragraph_before(ABSTRACT_TEXT)
        # clear the just-inserted paragraph and set it to the final abstract text
        doc.paragraphs[start_idx].text = ABSTRACT_TEXT
        doc.paragraphs[start_idx].alignment = WD_ALIGN_PARAGRAPH.LEFT
        print("Fix 1: Replaced progress snapshot block with abstract paragraph.")
    else:
        print("Warning: progress snapshot text not found.")

    # 2) Move the methodology intro to the start of Section 3.
    intro_text = "The pipeline processes code in the following sequence:"
    intro_idx = find_index_by_text(doc, intro_text)
    if intro_idx is not None:
        # remove from current location
        old_p = doc.paragraphs[intro_idx]._p
        parent = old_p.getparent()
        parent.remove(old_p)

    section3_index = find_index_by_text(doc, "3. Methodology")
    if section3_index is not None:
        insert_idx = section3_index + 1
        insert_paragraph_at(doc, insert_idx, intro_text)
        print("Fix 2: Moved methodology intro to the top of Section 3.")
    else:
        print("Warning: Section 3 heading not found.")

    # 3) Delete duplicate plain-text table rows in Results.
    remove_paragraphs_by_text(
        doc,
        [
            "Method | Precision | Recall | F1",
            "GNN (checkpoint epoch 78) | — | — | 0.467",
            "Gemini (comment-stripped source) | — | — | 0.909",
            "Clang-Tidy (keyword-mapped) | High | Lower | 0.435",
        ],
    )
    print("Fix 3: Removed duplicate plain-text Results rows.")

    doc.save(REPORT_PATH)
    print(f"Saved updated report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
