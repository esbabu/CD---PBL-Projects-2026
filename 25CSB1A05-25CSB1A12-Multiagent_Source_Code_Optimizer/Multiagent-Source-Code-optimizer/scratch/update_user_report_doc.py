import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading_styled(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.name = 'Arial'
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)  # slate-900
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)  # slate-800
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
    else:
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)  # slate-700
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    return p

def main():
    source_path = r'C:\Users\jaish\Desktop\TOC FINAL FOLDER\END FOLDER\Multiagnet-Source-Code-Optimizer End report.docx'
    print(f'Reading source document from: {source_path}')
    doc = docx.Document(source_path)

    print(f'Initial paragraphs count: {len(doc.paragraphs)}')
    print(f'Initial inline images count: {len(doc.inline_shapes)}')

    # Add a page break to cleanly separate the Test Cases section
    doc.add_page_break()

    # DEDICATED SEPARATE SECTION FOR TEST CASES
    add_heading_styled(doc, 'SECTION: BENCHMARK TEST CASES & LIVE EXECUTION PROOFS (198 TEST CASES)', level=1)
    add_heading_styled(doc, 'VII.   SYSTEMATIC BENCHMARK TEST CASES (198 TEST CASES WITH INDIVIDUAL SCREENSHOTS & DESCRIPTIONS)', level=2)

    add_body_p(doc,
        'This dedicated section provides an exhaustive, systematically cataloged evaluation of all 198 ground-truth test cases '
        'evaluated within the CompilerAI Optimization Studio across its autonomous multi-agent orchestration architecture. '
        'The benchmark test suite spans three distinct evaluation corpora: (1) the C++ ground-truth benchmark suite (vulnerable_samples.cpp) '
        'containing 87 test cases (66 security vulnerability cases across 7 CWE domains and 21 algorithmic optimization cases); '
        '(2) the Python ground-truth benchmark suite (vulnerable_samples.py) containing 107 test cases (73 security vulnerability cases '
        'across 10 distinct categories and 34 algorithmic optimization cases across 9 problem families); and (3) built-in language starter presets '
        'and execution mode invariants across C++, Python, C, and JavaScript (4 test cases). Each test case is individually numbered (Test Case 1 through '
        'Test Case 198), accompanied by an explicit description of the underlying flaw or optimization opportunity, line references, remediation guidance, '
        'and an individual live screenshot captured directly from the running studio platform, systematically numbered as Screenshot .1 through Screenshot .198.'
    )

    # Load Metadata JSON
    meta_path = 'scratch/all_198_metadata.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    print(f'Loaded {len(metadata)} test case records from {meta_path}.')

    for item in metadata:
        tc_num = item['tc_num']
        suite = item['suite']
        tc_type = item['type']
        sev = item['severity']
        title = item['title']
        cwe = item['cwe']
        line = item['line']
        desc = item['description']
        remed = item['remediation']
        img_path = item['screenshot']

        # Section Headings
        if tc_num == 1:
            add_heading_styled(doc, '1. C++ Benchmark Suite: vulnerable_samples.cpp (Test Cases 1 – 87)', level=2)
            add_heading_styled(doc, '1.1 C++ Security Audit Findings (Test Cases 1 – 66)', level=3)
            add_body_p(doc, 'The following 66 test cases evaluate memory safety defects, buffer overflows, format string vulnerabilities, integer overflow hazards, file races, and cryptographic flaws in C++:')
        elif tc_num == 67:
            add_heading_styled(doc, '1.2 C++ Algorithmic Transformations & Optimizations (Test Cases 67 – 87)', level=3)
            add_body_p(doc, 'The following 21 test cases validate algorithmic rewrites, loop invariance hoisting, container pre-allocations, and asymptotic complexity reductions in C++:')
        elif tc_num == 88:
            add_heading_styled(doc, '2. Python Benchmark Suite: vulnerable_samples.py (Test Cases 88 – 194)', level=2)
            add_heading_styled(doc, '2.1 Python Security Audit Findings (Test Cases 88 – 160)', level=3)
            add_body_p(doc, 'The following 73 test cases evaluate injection flaws, deserialization exploits, path traversal vulnerabilities, permission errors, weak cryptography, and resource exhaustion in Python:')
        elif tc_num == 161:
            add_heading_styled(doc, '2.2 Python Algorithmic Transformations & Optimizations (Test Cases 161 – 194)', level=3)
            add_body_p(doc, 'The following 34 test cases evaluate Python AST rewrites, list comprehension hoisting, generator streaming, hash set conversions, and vectorization:')
        elif tc_num == 195:
            add_heading_styled(doc, '3. Built-in Language Starters & Execution Mode Invariants (Test Cases 195 – 198)', level=2)
            add_body_p(doc, 'The following 4 test cases validate core platform execution mode invariants and language runtime support across C++, Python, C, and JavaScript:')

        # Test Case Title / Bullet
        p_tc = doc.add_paragraph()
        p_tc.paragraph_format.space_before = Pt(8)
        p_tc.paragraph_format.space_after = Pt(2)
        r_num = p_tc.add_run(f'• Test Case {tc_num} [{sev} - {cwe}]: ')
        r_num.bold = True
        r_num.font.name = 'Arial'
        r_num.font.size = Pt(9.5)
        if sev == 'CRITICAL':
            r_num.font.color.rgb = RGBColor(0xb9, 0x1c, 0x1c)  # red-700
        elif sev == 'HIGH':
            r_num.font.color.rgb = RGBColor(0xc2, 0x41, 0x0c)  # orange-700
        elif sev == 'MEDIUM':
            r_num.font.color.rgb = RGBColor(0xb4, 0x53, 0x09)  # amber-700
        elif sev == 'OPTIMIZATION':
            r_num.font.color.rgb = RGBColor(0x1d, 0x4e, 0xd8)  # blue-700
        else:
            r_num.font.color.rgb = RGBColor(0x33, 0x41, 0x55)  # slate-700

        r_title = p_tc.add_run(f'{title}')
        r_title.bold = True
        r_title.font.name = 'Arial'
        r_title.font.size = Pt(9.5)
        r_title.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)

        if line:
            r_line = p_tc.add_run(f' ({line})')
            r_line.italic = True
            r_line.font.name = 'Arial'
            r_line.font.size = Pt(9)
            r_line.font.color.rgb = RGBColor(0x64, 0x74, 0x8b)

        # Description
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_before = Pt(1)
        p_desc.paragraph_format.space_after = Pt(2)
        p_desc.paragraph_format.line_spacing = 1.15
        r_desc_lbl = p_desc.add_run('Description: ')
        r_desc_lbl.bold = True
        r_desc_lbl.font.name = 'Arial'
        r_desc_lbl.font.size = Pt(8.5)
        r_desc_lbl.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        r_desc_txt = p_desc.add_run(desc)
        r_desc_txt.font.name = 'Arial'
        r_desc_txt.font.size = Pt(8.5)
        r_desc_txt.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        # Remediation
        if remed:
            p_rem = doc.add_paragraph()
            p_rem.paragraph_format.space_before = Pt(1)
            p_rem.paragraph_format.space_after = Pt(3)
            p_rem.paragraph_format.line_spacing = 1.15
            r_rem_lbl = p_rem.add_run('Remediation / Transformation: ')
            r_rem_lbl.bold = True
            r_rem_lbl.font.name = 'Arial'
            r_rem_lbl.font.size = Pt(8.5)
            r_rem_lbl.font.color.rgb = RGBColor(0x04, 0x78, 0x57)  # emerald-700
            r_rem_txt = p_rem.add_run(remed)
            r_rem_txt.font.name = 'Arial'
            r_rem_txt.font.size = Pt(8.5)
            r_rem_txt.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        # Screenshot Image
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(3)
            p_img.paragraph_format.space_after = Pt(2)
            run_img = p_img.add_run()
            if tc_num in [195, 196, 197, 198]:
                run_img.add_picture(img_path, width=Inches(5.6))
            else:
                run_img.add_picture(img_path, width=Inches(6.0))

        # Screenshot Caption
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(8)
        run_cap = p_cap.add_run(f'Screenshot .{tc_num}: Live Platform Output for Test Case {tc_num} — {title}')
        run_cap.italic = True
        run_cap.font.name = 'Arial'
        run_cap.font.size = Pt(8)
        run_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

        if tc_num % 50 == 0:
            print(f'   Embedded Test Case {tc_num} / 198...')

    # Output paths to save
    targets = [
        r'C:\Users\jaish\Desktop\TOC FINAL FOLDER\END FOLDER\Multiagnet-Source-Code-Optimizer_End_report.docx',
        r'C:\Users\jaish\Desktop\TOC FINAL FOLDER\END FOLDER\Multiagnet-Source-Code-Optimizer End report_updated.docx',
        r'Multiagnet-Source-Code-Optimizer End report.docx',
        r'Multiagent-Source-Code-Optimizer_End_report.docx',
        r'CompilerAI_Optimization_Studio_Research_Paper.docx',
        r'CompilerAI_Optimization_Studio_Research_Paper_with_Appendix.docx'
    ]

    for t in targets:
        try:
            print(f'Saving to: {t}')
            doc.save(t)
            print(f' -> Successfully saved {t}')
        except Exception as e:
            print(f' -> Could not save {t} (may be locked by Word): {e}')

    # Try original path if possible
    try:
        doc.save(source_path)
        print(f' -> Successfully overwritten original: {source_path}')
    except Exception as e:
        print(f' -> Note: Original file {source_path} is currently locked by Word: {e}')

if __name__ == '__main__':
    main()
