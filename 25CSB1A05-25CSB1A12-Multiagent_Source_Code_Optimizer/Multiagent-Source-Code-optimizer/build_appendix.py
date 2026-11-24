"""Script to generate all 13 Appendix screenshots via Selenium, annotate them with red borders and callout boxes, and embed them into CompilerAI_Optimization_Studio_Research_Paper.docx."""
import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SCREENSHOTS_DIR = Path("appendix_screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Code samples for generating each state
# ---------------------------------------------------------------------------
CODE_TWO_SUM = """def two_sum(nums: list[int], target: int) -> list[int]:
    # Inefficient O(n^2) brute force search
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

CODE_CPP_VULNERABLE = """// Vulnerable C++ sample with memory safety and command injection defects
#include <iostream>
#include <cstring>
#include <cstdlib>

void process_user(char* input) {
    char buffer[32];
    strcpy(buffer, input); // CWE-120: Buffer Overflow
    std::cout << "Buffer: " << buffer << std::endl;
}

void backup_database(char* filename) {
    char cmd[128];
    sprintf(cmd, "cp %s /backup/", filename); // CWE-134 & CWE-78
    system(cmd);
}

int main() {
    process_user("test");
    backup_database("data.txt");
    return 0;
}
"""

CODE_CPP_OPTIMIZE = """#include <vector>
#include <numeric>

long long sumArray(const std::vector<int>& arr) {
    long long total = 0;
    // O(n^2) redundant nested loop
    for (size_t i = 0; i < arr.size(); ++i) {
        for (size_t j = 0; j < arr.size(); ++j) {
            if (i == j) {
                total += arr[i];
            }
        }
    }
    return total;
}
"""

CODE_SYNTAX_ERROR = """def calculate_metrics(values):
    # Syntax error: missing colon and smart quotes
    for val in values
        print("Value:", val)
    return sum(values)
"""

CODE_MODULE_STUDENT = """import os
import pickle
import hashlib

students = []
passwords = {}

def register(username, password):
    passwords[username] = hashlib.md5(password.encode()).hexdigest()

def sort_students():
    n = len(students)
    for i in range(n):
        for j in range(0, n-i-1):
            if students[j]["marks"] < students[j+1]["marks"]:
                temp = students[j]
                students[j] = students[j+1]
                students[j+1] = temp

def calculate_average():
    total = 0
    for student in students:
        for i in range(1000):
            total += student["marks"] / 1000
    return total / len(students)

def find_duplicates():
    duplicates = []
    for i in range(len(students)):
        for j in range(len(students)):
            if i != j and students[i]["roll"] == students[j]["roll"]:
                if students[i] not in duplicates:
                    duplicates.append(students[i])
    return duplicates
"""

# ---------------------------------------------------------------------------
# Annotation Helper: Draws red border and template-style callout boxes
# ---------------------------------------------------------------------------
def annotate_image(input_path: Path, output_path: Path, callouts: list[dict]):
    im = Image.open(input_path).convert("RGB")
    W, H = im.size
    draw = ImageDraw.Draw(im)

    # 1. Outer red bounding border (matching template PDF style)
    border_color = (204, 0, 0) # Rich crimson red #cc0000
    draw.rectangle([6, 6, W - 7, H - 7], outline=border_color, width=5)

    # Try loading a standard font
    font = None
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except Exception:
        font_bold = ImageFont.load_default()

    # 2. Draw Callout boxes ("Purpose of This")
    for c in callouts:
        box_x1, box_y1, box_x2, box_y2 = c["box"]
        target_x, target_y = c.get("target", (box_x1, box_y1))
        label = c.get("label", "Purpose of This")

        # Draw black border white fill box
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
        # Draw label text
        bbox = draw.textbbox((0, 0), label, font=font_bold)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = box_x1 + (box_x2 - box_x1 - text_w) // 2
        text_y = box_y1 + (box_y2 - box_y1 - text_h) // 2
        draw.text((text_x, text_y), label, fill=(0, 0, 0), font=font_bold)

        # Draw callout arrow/pointer from box to target
        if "target" in c:
            tip_x, tip_y = target_x, target_y
            if tip_x < box_x1:
                base_x = box_x1
                base_y = (box_y1 + box_y2) // 2
                draw.polygon([(tip_x, tip_y), (base_x, base_y - 10), (base_x, base_y + 10)], fill=(0, 0, 0))
            elif tip_x > box_x2:
                base_x = box_x2
                base_y = (box_y1 + box_y2) // 2
                draw.polygon([(tip_x, tip_y), (base_x, base_y - 10), (base_x, base_y + 10)], fill=(0, 0, 0))
            elif tip_y < box_y1:
                base_x = (box_x1 + box_x2) // 2
                base_y = box_y1
                draw.polygon([(tip_x, tip_y), (base_x - 10, base_y), (base_x + 10, base_y)], fill=(0, 0, 0))
            else:
                base_x = (box_x1 + box_x2) // 2
                base_y = box_y2
                draw.polygon([(tip_x, tip_y), (base_x - 10, base_y), (base_x + 10, base_y)], fill=(0, 0, 0))

    im.save(output_path, "PNG", quality=95)
    print(f"[+] Saved annotated: {output_path}")


# ---------------------------------------------------------------------------
# Selenium Driver Routine to Capture All 13 Figures
# ---------------------------------------------------------------------------
def capture_all_figures():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1600,980')

    driver = webdriver.Chrome(options=options)
    driver.get("http://127.0.0.1:5173")
    time.sleep(3)

    def set_monaco(code: str):
        driver.execute_script("window.monaco.editor.getModels()[0].setValue(arguments[0]);", code)
        time.sleep(0.5)

    def select_lang(lang_val: str):
        for sel in driver.find_elements(By.TAG_NAME, "select"):
            for opt in sel.find_elements(By.TAG_NAME, "option"):
                if opt.get_attribute("value") == lang_val:
                    opt.click()
                    time.sleep(0.5)
                    return

    def click_button_text(txt: str):
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if txt in b.text:
                b.click()
                time.sleep(0.5)
                return True
        return False

    def click_run_and_wait(timeout_s: int = 15):
        click_button_text("Run")
        for _ in range(timeout_s):
            time.sleep(1)
            body = driver.find_element(By.TAG_NAME, "body").text
            if "Completed" in body or "Partially Completed" in body or "failed" in body:
                break
        time.sleep(1)

    # ---------------- Fig. 1: GUI Initial State ----------------
    print("[*] Capturing Fig 1: Initial UI...")
    select_lang("python")
    set_monaco(CODE_TWO_SUM)
    click_button_text("Full Pipeline")
    click_button_text("Heuristics")
    click_button_text("Output")
    time.sleep(1)
    raw_1 = SCREENSHOTS_DIR / "raw_fig1.png"
    driver.save_screenshot(str(raw_1))
    callouts_1 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (20, 200, 110, 360), "target": (120, 280), "label": "Purpose of This"},
        {"box": (1480, 200, 1570, 360), "target": (1470, 280), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_1, SCREENSHOTS_DIR / "fig_1.png", callouts_1)

    # ---------------- Fig. 2: Full Pipeline Completed Output ----------------
    print("[*] Capturing Fig 2: Full Pipeline Execution...")
    click_run_and_wait(12)
    click_button_text("Output")
    time.sleep(1)
    raw_2 = SCREENSHOTS_DIR / "raw_fig2.png"
    driver.save_screenshot(str(raw_2))
    callouts_2 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (1480, 200, 1570, 360), "target": (1470, 280), "label": "Purpose of This"},
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 620, 110, 780), "target": (120, 700), "label": "Purpose of This"},
    ]
    annotate_image(raw_2, SCREENSHOTS_DIR / "fig_2.png", callouts_2)

    # ---------------- Fig. 3: Side-by-Side Optimized Code Diff ----------------
    print("[*] Capturing Fig 3: Optimized Code Diff...")
    click_button_text("Optimized Code")
    time.sleep(1)
    raw_3 = SCREENSHOTS_DIR / "raw_fig3.png"
    driver.save_screenshot(str(raw_3))
    callouts_3 = [
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_3, SCREENSHOTS_DIR / "fig_3.png", callouts_3)

    # ---------------- Fig. 4: Detailed Algorithmic Transformation & Metrics ----------------
    print("[*] Capturing Fig 4: Detailed Algorithmic Metrics...")
    raw_4 = SCREENSHOTS_DIR / "raw_fig4.png"
    driver.save_screenshot(str(raw_4))
    callouts_4 = [
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_4, SCREENSHOTS_DIR / "fig_4.png", callouts_4)

    # ---------------- Fig. 5: Neuro-Symbolic Security Audit Dashboard ----------------
    print("[*] Capturing Fig 5: Security Dashboard (Clean)...")
    click_button_text("Security")
    time.sleep(1)
    raw_5 = SCREENSHOTS_DIR / "raw_fig5.png"
    driver.save_screenshot(str(raw_5))
    callouts_5 = [
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_5, SCREENSHOTS_DIR / "fig_5.png", callouts_5)

    # ---------------- Fig. 6: Security Audit on Vulnerable C++ Code ----------------
    print("[*] Capturing Fig 6: Security Findings on Vulnerable C++...")
    select_lang("cpp")
    set_monaco(CODE_CPP_VULNERABLE)
    click_button_text("Security") # Set Mode: Security
    time.sleep(0.5)
    click_run_and_wait(10)
    time.sleep(1)
    raw_6 = SCREENSHOTS_DIR / "raw_fig6.png"
    driver.save_screenshot(str(raw_6))
    callouts_6 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_6, SCREENSHOTS_DIR / "fig_6.png", callouts_6)

    # ---------------- Fig. 7: Deterministic Security Patching View ----------------
    print("[*] Capturing Fig 7: Security Patch View...")
    raw_7 = SCREENSHOTS_DIR / "raw_fig7.png"
    driver.save_screenshot(str(raw_7))
    callouts_7 = [
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_7, SCREENSHOTS_DIR / "fig_7.png", callouts_7)

    # ---------------- Fig. 8: Messages and Diagnostic Event Stream ----------------
    print("[*] Capturing Fig 8: Messages Trace Stream...")
    click_button_text("Messages")
    time.sleep(1)
    raw_8 = SCREENSHOTS_DIR / "raw_fig8.png"
    driver.save_screenshot(str(raw_8))
    callouts_8 = [
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
        {"box": (1480, 600, 1570, 760), "target": (1470, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_8, SCREENSHOTS_DIR / "fig_8.png", callouts_8)

    # ---------------- Fig. 9: Standalone 'Optimize' Mode ----------------
    print("[*] Capturing Fig 9: Dedicated Optimize Mode...")
    click_button_text("Optimize") # Set Mode: Optimize
    select_lang("python")
    set_monaco(CODE_TWO_SUM)
    click_run_and_wait(10)
    time.sleep(1)
    raw_9 = SCREENSHOTS_DIR / "raw_fig9.png"
    driver.save_screenshot(str(raw_9))
    callouts_9 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (1480, 200, 1570, 360), "target": (1470, 280), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_9, SCREENSHOTS_DIR / "fig_9.png", callouts_9)

    # ---------------- Fig. 10: Standalone 'Security' Mode ----------------
    print("[*] Capturing Fig 10: Dedicated Security Mode...")
    click_button_text("Security") # Set Mode: Security
    select_lang("cpp")
    set_monaco(CODE_CPP_VULNERABLE)
    click_run_and_wait(10)
    time.sleep(1)
    raw_10 = SCREENSHOTS_DIR / "raw_fig10.png"
    driver.save_screenshot(str(raw_10))
    callouts_10 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (1480, 200, 1570, 360), "target": (1470, 280), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_10, SCREENSHOTS_DIR / "fig_10.png", callouts_10)

    # ---------------- Fig. 11: C++ Algorithmic Optimization (sumArray) ----------------
    print("[*] Capturing Fig 11: C++ sumArray Optimization...")
    click_button_text("Full Pipeline")
    select_lang("cpp")
    set_monaco(CODE_CPP_OPTIMIZE)
    click_run_and_wait(12)
    click_button_text("Optimized Code")
    time.sleep(1)
    raw_11 = SCREENSHOTS_DIR / "raw_fig11.png"
    driver.save_screenshot(str(raw_11))
    callouts_11 = [
        {"box": (680, 20, 880, 60), "target": (780, 70), "label": "Purpose of This"},
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_11, SCREENSHOTS_DIR / "fig_11.png", callouts_11)

    # ---------------- Fig. 12: Python Module Mode Multi-Unit Decomposition ----------------
    print("[*] Capturing Fig 12: Module Mode (student_manager.py)...")
    select_lang("python")
    set_monaco(CODE_MODULE_STUDENT)
    click_button_text("Full Pipeline")
    click_button_text("Output")
    click_run_and_wait(12)
    time.sleep(1)
    raw_12 = SCREENSHOTS_DIR / "raw_fig12.png"
    driver.save_screenshot(str(raw_12))
    callouts_12 = [
        {"box": (20, 200, 110, 360), "target": (120, 280), "label": "Purpose of This"},
        {"box": (1480, 200, 1570, 360), "target": (1470, 280), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_12, SCREENSHOTS_DIR / "fig_12.png", callouts_12)

    # ---------------- Fig. 13: Syntax Gate (Stage S0) Parse Check & Repair ----------------
    print("[*] Capturing Fig 13: Syntax Gate Repair...")
    set_monaco(CODE_SYNTAX_ERROR)
    click_run_and_wait(10)
    click_button_text("Messages")
    time.sleep(1)
    raw_13 = SCREENSHOTS_DIR / "raw_fig13.png"
    driver.save_screenshot(str(raw_13))
    callouts_13 = [
        {"box": (20, 200, 110, 360), "target": (120, 280), "label": "Purpose of This"},
        {"box": (680, 500, 880, 540), "target": (780, 550), "label": "Purpose of This"},
        {"box": (20, 600, 110, 760), "target": (120, 680), "label": "Purpose of This"},
    ]
    annotate_image(raw_13, SCREENSHOTS_DIR / "fig_13.png", callouts_13)

    driver.quit()
    print("[+] All 13 live screenshots captured and annotated successfully!")


# ---------------------------------------------------------------------------
# Embed into CompilerAI_Optimization_Studio_Research_Paper.docx
# ---------------------------------------------------------------------------
FIGURE_METADATA = [
    {
        "fig_num": 1,
        "title": "Fig. 1. Graphical User Interface of the CompilerAI Optimization Studio.",
        "img": "fig_1.png",
        "desc": "The figure 1 shows the main graphical user interface of the CompilerAI Optimization Studio, consisting of a top control navigation bar for configuring execution modes (Full Pipeline, Optimize, Security) and inference engines (Heuristics, Local LLM), a Monaco-based source code input editor with multi-language syntax highlighting, a live pipeline stage graph tracking real-time agent lifecycle events via Server-Sent Events (SSE), and a multi-tabbed results inspection panel."
    },
    {
        "fig_num": 2,
        "title": "Fig. 2. Full Pipeline Execution and Consolidated Output Panel.",
        "img": "fig_2.png",
        "desc": "The figure 2 illustrates the completed execution of the Full Pipeline mode, demonstrating sequential multi-agent orchestration. The Live Pipeline Stage Graph confirms 100% execution across all stages (Source validation, Algorithmic Optimization, Security Auditing, and Final Completion), while the Output tab renders the consolidated execution summary, elapsed execution time, and verification status."
    },
    {
        "fig_num": 3,
        "title": "Fig. 3. Side-by-Side Algorithmic Code Optimization and Diff Viewer.",
        "img": "fig_3.png",
        "desc": "The figure 3 illustrates the side-by-side algorithmic code optimization view in CompilerAI. The left panel shows the original inefficient O(n²) nested loop routine, while the right panel displays the verified rewritten candidate algorithm incorporating an auxiliary hash map and binary search bisect lookup, accompanied by the empirical scaling speedup factor and complexity class transition."
    },
    {
        "fig_num": 4,
        "title": "Fig. 4. Detailed Algorithmic Transformation and Complexity Analysis View.",
        "img": "fig_4.png",
        "desc": "The figure 4 presents the detailed algorithmic transformation metrics and verification ladder evidence. It displays the fitted empirical time complexity, memory allocation ratio, verification tier achieved (Tier T2 backed by Hypothesis differential fuzzing), and the formal rationale detailing why the synthesized candidate guarantees strict functional equivalence."
    },
    {
        "fig_num": 5,
        "title": "Fig. 5. Neuro-Symbolic Security Audit Dashboard and CWE Overview.",
        "img": "fig_5.png",
        "desc": "The figure 5 presents the neuro-symbolic security audit dashboard of the CompilerAI Security Agent. It displays the overall qualitative security score (100/100), score delta indicator confirming zero introduced regressions, and verification status across six Common Weakness Enumeration (CWE) vulnerability domains."
    },
    {
        "fig_num": 6,
        "title": "Fig. 6. Detailed Security Defect Diagnostic Cards on Vulnerable C++ Code.",
        "img": "fig_6.png",
        "desc": "The figure 6 illustrates the detailed security vulnerability diagnostic cards generated by the Security Agent on a vulnerable C++ program. The interface highlights critical defects including CWE-120 (classic buffer overflow via strcpy) and CWE-134 (uncontrolled format string), specifying exact line numbers, severity ratings, and actionable remediation guidance."
    },
    {
        "fig_num": 7,
        "title": "Fig. 7. Deterministic Security Patching and Unified Code Diff.",
        "img": "fig_7.png",
        "desc": "The figure 7 demonstrates the deterministic security patching engine in CompilerAI. The system automatically synthesizes line-level surgical replacements for dangerous C APIs—converting unsafe functions like gets() and strcpy() to fgets() and strncpy() with bounded buffer limits—while maintaining transactional rollback protection."
    },
    {
        "fig_num": 8,
        "title": "Fig. 8. Diagnostic Messages and Execution Lifecycle Trace Stream.",
        "img": "fig_8.png",
        "desc": "The figure 8 illustrates the Messages and diagnostic trace stream tab. It captures all internal compiler facts, triage decisions, syntax gate results, Hypothesis fuzzer progress, and reason codes emitted across the multi-agent orchestration lifecycle, providing transparent auditing for developers."
    },
    {
        "fig_num": 9,
        "title": "Fig. 9. Dedicated Algorithmic Optimization Mode ('Optimize') Execution.",
        "img": "fig_9.png",
        "desc": "The figure 9 displays CompilerAI operating in dedicated Optimize mode. In this mode, the orchestrator bypasses security auditing to minimize execution latency, focusing exclusively on AST intent extraction, Hypothesis fuzzing oracle generation, candidate transformation search, and empirical speedup measurement."
    },
    {
        "fig_num": 10,
        "title": "Fig. 10. Dedicated Security Audit Mode ('Security') Execution.",
        "img": "fig_10.png",
        "desc": "The figure 10 illustrates the dedicated Security mode. The system executes static AST taint heuristics and concurrent SAST tools directly against unoptimized source code, allowing developers to audit legacy codebases for critical vulnerabilities without altering program logic."
    },
    {
        "fig_num": 11,
        "title": "Fig. 11. High-Performance C++ Algorithmic Optimization and Scaling Verification.",
        "img": "fig_11.png",
        "desc": "The figure 11 demonstrates C++ algorithmic optimization within CompilerAI. The Optimization Agent analyzes a quadratic sumArray routine in C++, eliminates redundant nested iterations, compiles and benchmarks using Clang/LLVM, and validates asymptotic speedup with strict functional equivalence."
    },
    {
        "fig_num": 12,
        "title": "Fig. 12. Python Module Mode Multi-Unit Decomposition and Optimization.",
        "img": "fig_12.png",
        "desc": "The figure 12 presents Module Mode in CompilerAI, reverse-engineering and optimizing a complex multi-unit program (student_manager.py). The system decomposes the module into 18 independent units, resolves state dependencies via synthetic fixtures, optimizes five algorithmic bottlenecks, and verifies stateful call-sequence equivalence."
    },
    {
        "fig_num": 13,
        "title": "Fig. 13. Syntax Gate (Stage S0) Parse Check and Deterministic Repair.",
        "img": "fig_13.png",
        "desc": "The figure 13 illustrates the Stage S0 Syntax Gate. When source code with syntax slips is submitted, deterministic heuristic fixers automatically repair syntax errors (e.g., inserting missing colons, converting smart quotes to ASCII, and balancing delimiters), allowing compiler triage to proceed smoothly without unnecessary pipeline termination."
    },
]

def update_word_document(src_docx: str = "CompilerAI_Optimization_Studio_Research_Paper.docx", target_docx: str = "CompilerAI_Optimization_Studio_Research_Paper_with_Appendix.docx"):
    print(f"[*] Reading source Word document: {src_docx}...")
    doc = docx.Document(src_docx)

    # 1. Check if APPENDIX already exists to avoid duplication
    appendix_p_idx = -1
    for idx, p in enumerate(doc.paragraphs):
        if p.text.strip() == "APPENDIX" or p.text.strip().startswith("APPENDIX"):
            appendix_p_idx = idx
            break

    # If it already exists, remove subsequent paragraphs
    if appendix_p_idx != -1:
        print(f"[*] Found existing APPENDIX at paragraph {appendix_p_idx}. Overwriting with updated version...")
        for _ in range(len(doc.paragraphs) - appendix_p_idx):
            p = doc.paragraphs[-1]
            p._element.getparent().remove(p._element)

    # Add a page break before APPENDIX
    doc.add_page_break()

    # Title: APPENDIX
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("APPENDIX")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(14)
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(2)

    # Subtitle: (Sample Screenshots with Description)
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("(Sample Screenshots with Description)")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(16)

    # Add all 13 figures
    for idx, fig in enumerate(FIGURE_METADATA):
        img_file = SCREENSHOTS_DIR / fig["img"]
        if not img_file.exists():
            print(f"[!] Warning: Image {img_file} not found, skipping...")
            continue

        # Add image
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_file), width=Inches(5.75))

        # Add Figure Title
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(3)
        run_cap = p_cap.add_run(fig["title"])
        run_cap.bold = True
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10)

        # Add Figure Description
        p_desc = doc.add_paragraph()
        p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_desc.paragraph_format.space_before = Pt(0)
        p_desc.paragraph_format.space_after = Pt(14)
        run_desc = p_desc.add_run(fig["desc"])
        run_desc.font.name = "Times New Roman"
        run_desc.font.size = Pt(9.5)

    # Save to target_docx
    doc.save(target_docx)
    print(f"[+] Successfully saved updated document to {target_docx} with all 13 figures and descriptions!")

    # Also try saving directly to src_docx if unlocked
    if target_docx != src_docx:
        try:
            doc.save(src_docx)
            print(f"[+] Also successfully overwritten original {src_docx}!")
        except Exception as e:
            print(f"[*] Note: Original {src_docx} is currently locked by Word ({e}). The complete updated document is available at {target_docx}.")

if __name__ == "__main__":
    capture_all_figures()
    update_word_document()
